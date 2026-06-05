import hashlib
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from .services.news_service import fetch_combined_for_interests
from .services.llm_service import generate_social_posts
from .forms import InterestForm
from .models import Trend, GeneratedPost


def _build_trend_key(trend):
    return f"{trend.get('topic', '')}|{trend.get('source', '')}"


def _build_request_hash(topic, context, preferences):
    raw = "|".join([
        topic or "",
        context or "",
        preferences.get("tone") or "",
        preferences.get("audience") or "",
        preferences.get("length") or "",
        preferences.get("emoji_style") or "",
        preferences.get("cta") or "",
        preferences.get("hashtags") or "",
        preferences.get("platforms") or "",
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def homepage(request):
    form = InterestForm(request.GET or None)
    selected_interests = []

    if form.is_valid():
        selected_interests = form.cleaned_data.get("interests", [])

    trends = fetch_combined_for_interests(selected_interests)
    trend_map = {}
    selected_key = request.GET.get("selected") or ""
    generated_record = None
    generation_error = ""

    for trend in trends:
        trend["trend_key"] = _build_trend_key(trend)
        trend_map[trend["trend_key"]] = trend

    if trends:
        Trend.objects.bulk_create([
            Trend(
                topic=trend.get("topic", ""),
                context=trend.get("context", ""),
                category=trend.get("category", "General"),
                source=trend.get("source")
            )
            for trend in trends
        ])

    if request.method == "POST" and request.POST.get("action") == "generate_post":
        trend_key = request.POST.get("trend_key") or ""
        selected_key = trend_key
        selected_trend = trend_map.get(trend_key, {})
        topic = selected_trend.get("topic") or request.POST.get("topic") or ""
        context = selected_trend.get("context") or request.POST.get("context") or ""
        category = selected_trend.get("category") or request.POST.get("category") or ""
        preferences = {
            "tone": request.POST.get("tone") or "",
            "audience": request.POST.get("audience") or "",
            "length": request.POST.get("length") or "",
            "emoji_style": request.POST.get("emoji_style") or "",
            "cta": request.POST.get("cta") or "",
            "hashtags": request.POST.get("hashtags") or "",
            "platforms": "LinkedIn, Instagram, X",
        }

        request_hash = _build_request_hash(topic, context, preferences)
        cache_key = f"generated_post:{request_hash}"
        cached = cache.get(cache_key)

        existing = GeneratedPost.objects.filter(request_hash=request_hash).first()

        if existing:
            generated_record = existing
            cache.set(cache_key, existing.generated_text, 60 * 60 * 24)
        elif cached:
            generated_record = GeneratedPost.objects.create(
                request_hash=request_hash,
                topic=topic,
                context=context,
                category=category,
                platforms=preferences["platforms"],
                tone=preferences["tone"],
                audience=preferences["audience"],
                length=preferences["length"],
                emoji_style=preferences["emoji_style"],
                cta=preferences["cta"],
                hashtags=preferences["hashtags"],
                generated_text=cached,
            )
        else:
            try:
                generated_text = generate_social_posts(topic, context, preferences)
                generated_record = GeneratedPost.objects.create(
                    request_hash=request_hash,
                    topic=topic,
                    context=context,
                    category=category,
                    platforms=preferences["platforms"],
                    tone=preferences["tone"],
                    audience=preferences["audience"],
                    length=preferences["length"],
                    emoji_style=preferences["emoji_style"],
                    cta=preferences["cta"],
                    hashtags=preferences["hashtags"],
                    generated_text=generated_text,
                )
                cache.set(cache_key, generated_text, 60 * 60 * 24)
            except Exception as exc:
                generation_error = str(exc)

        if generated_record:
            return redirect(f"/post/?id={generated_record.id}")
        if generation_error:
            request.session["post_error"] = generation_error
            return redirect("/post/?error=1")

    selected_trend = trend_map.get(selected_key)

    return render(request, "trends/index.html", {
        "trends": trends,
        "form": form,
        "selected_trend": selected_trend,
    })


def generated_post(request):
    post_id = request.GET.get("id")
    generation_error = ""

    if request.GET.get("error"):
        generation_error = request.session.pop("post_error", "")

    post = None
    if post_id:
        post = get_object_or_404(GeneratedPost, id=post_id)

    return render(request, "trends/post.html", {
        "post": post,
        "generation_error": generation_error,
    })
