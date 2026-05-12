from django.shortcuts import render
from .services.news_service import fetch_combined_for_interests
from .forms import InterestForm
from .models import Trend

def homepage(request):
    form = InterestForm(request.GET or None)
    selected_interests = []

    if form.is_valid():
        selected_interests = form.cleaned_data.get("interests", [])

    trends = fetch_combined_for_interests(selected_interests)

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

    return render(request, "trends/index.html", {
        "trends": trends,
        "form": form
    })
