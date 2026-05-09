import requests
import os

API_KEY = os.environ.get("NEWS_API_KEY")


def fetch_news(category="technology", page_size=10):
    url = "https://newsapi.org/v2/top-headlines"

    params = {
        "category": category,
        "language": "en",
        "pageSize": page_size,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            return []

        articles = []

        for article in data.get("articles", []):
            articles.append({
                "topic": article.get("title"),
                "context": article.get("description") or "",
                "category": category,
                "source": article.get("url")
            })

        return articles

    except Exception as e:
        print("NewsAPI error:", e)
        return []
