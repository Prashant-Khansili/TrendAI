from django.shortcuts import render
from .services.news_service import fetch_news
from .forms import InterestForm

def homepage(request):
    category = request.GET.get("category", "technology")
    form = InterestForm()
    trends = fetch_news(category)

    return render(request, "trends/index.html", {
        "trends": trends,
        "category": category,
        "form": form
    })
