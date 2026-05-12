import requests
import os
from ..interests import USER_INTERESTS
from .newsdata_service import get_interest_payload

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
        if not API_KEY:
            print("NewsAPI error: missing NEWS_API_KEY")
            return []
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            print("NewsAPI error:", data.get("message") or data.get("code") or "unknown error")
            return []

        articles = []

        for article in data.get("articles", []):
            articles.append({
                "topic": article.get("title"),
                "context": article.get("description") or "",
                "category": category,
                "source": article.get("url"),
                "source_tag": "NewsAPI"
            })

        return articles

    except Exception as e:
        print("NewsAPI error:", e)
        return []


def fetch_news_for_interests(interests, page_size=12):
    url = "https://newsapi.org/v2/everything"

    if not API_KEY:
        print("NewsAPI error: missing NEWS_API_KEY")
        return []

    interests = interests or []
    if not interests:
        return fetch_news(category="general", page_size=page_size)

    payload = get_interest_payload()
    keywords_map = payload.get("keywords") or {}
    per_interest = max(1, page_size // len(interests))
    articles = []
    seen = set()

    for interest in interests:
        keywords = keywords_map.get(interest) or USER_INTERESTS.get(interest, [])
        if keywords:
            query_terms = keywords[:3]
            query = " OR ".join(f'"{term}"' for term in query_terms)
        else:
            query = interest

        params = {
            "q": query,
            "language": "en",
            "pageSize": per_interest,
            "sortBy": "publishedAt",
            "searchIn": "title,description",
            "apiKey": API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
        except Exception as e:
            print("NewsAPI error:", e)
            continue

        if data.get("status") != "ok":
            print("NewsAPI error:", data.get("message") or data.get("code") or "unknown error")
            continue

        for article in data.get("articles", []):
            source_url = article.get("url")
            dedupe_key = source_url or article.get("title")
            if not dedupe_key or dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            articles.append({
                "topic": article.get("title"),
                "context": article.get("description") or "",
                "category": interest,
                "source": source_url,
                "source_tag": "NewsAPI"
            })

    if not articles:
        return fetch_news(category="general", page_size=page_size)

    return articles


def fetch_hn_for_interests(interests, page_size=12):
    url = "https://hn.algolia.com/api/v1/search"

    interests = interests or []
    if not interests:
        interests = ["technology"]

    payload = get_interest_payload()
    keywords_map = payload.get("keywords") or {}
    per_interest = max(1, page_size // len(interests))
    articles = []
    seen = set()

    for interest in interests:
        keywords = keywords_map.get(interest) or USER_INTERESTS.get(interest, [])
        if keywords:
            query_terms = keywords[:2]
            query = " ".join(query_terms)
        else:
            query = interest

        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": per_interest
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
        except Exception as e:
            print("HN API error:", e)
            continue

        for hit in data.get("hits", []):
            title = hit.get("title") or hit.get("story_title")
            if not title:
                continue
            source_url = hit.get("url") or hit.get("story_url")
            dedupe_key = source_url or title
            if not dedupe_key or dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            articles.append({
                "topic": title,
                "context": hit.get("story_text") or hit.get("comment_text") or "",
                "category": interest,
                "source": source_url,
                "source_tag": "HackerNews"
            })

    return articles


def fetch_combined_for_interests(interests, page_size=12):
    newsapi_items = fetch_news_for_interests(interests, page_size=page_size)
    hn_items = fetch_hn_for_interests(interests, page_size=page_size)

    combined = []
    seen = set()

    for item in newsapi_items + hn_items:
        dedupe_key = item.get("source") or item.get("topic")
        if not dedupe_key or dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        combined.append(item)

    return combined
