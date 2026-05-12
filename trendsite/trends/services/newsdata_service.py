import os
from datetime import timedelta
from django.utils import timezone
import requests

from ..models import TrendCache
from ..interests import USER_INTERESTS

API_KEY = os.environ.get("NEWSDATA_API_KEY")
CACHE_KEY = "newsdata_categories"
CACHE_TTL = timedelta(hours=24)


def _normalize_label(value):
    if not value:
        return None
    label = str(value).strip().replace("_", " ").replace("-", " ")
    return " ".join(label.split()).title()


def _extract_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _build_interest_payload(results):
    categories = set()
    keywords_map = {}

    for item in results:
        raw_categories = _extract_list(item.get("category") or item.get("categories"))
        raw_keywords = _extract_list(item.get("keywords") or item.get("tags") or item.get("keyword"))
        raw_keywords = [kw.lower() for kw in raw_keywords if kw]

        normalized_categories = [_normalize_label(cat) for cat in raw_categories]
        normalized_categories = [cat for cat in normalized_categories if cat]

        for category in normalized_categories:
            categories.add(category)
            if raw_keywords:
                keywords_map.setdefault(category, set()).update(raw_keywords)

    return {
        "categories": sorted(categories),
        "keywords": {key: sorted(list(values)) for key, values in keywords_map.items()}
    }


def _log_api_error(prefix, response, data):
    status = getattr(response, "status_code", "n/a")
    message = data.get("message") or data.get("status") or "unknown error"
    print(f"{prefix}: {message} (status {status})")


def fetch_newsdata_categories():
    if not API_KEY:
        print("Newsdata.io error: missing NEWSDATA_API_KEY")
        return {}

    url = "https://newsdata.io/api/1/sources"
    params = {
        "apikey": API_KEY,
        "language": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print("Newsdata.io error:", e)
        data = {}

    if data.get("status") in {"success", "ok"}:
        results = data.get("results") or data.get("sources") or []
        payload = _build_interest_payload(results)
        if payload.get("categories"):
            return payload
    else:
        _log_api_error("Newsdata.io /sources error", response, data)

    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": API_KEY,
        "language": "en",
        "size": 50,
        "q": "news"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print("Newsdata.io error:", e)
        return {}

    if data.get("status") not in {"success", "ok"}:
        _log_api_error("Newsdata.io /news error", response, data)
        return {}

    results = data.get("results") or []
    return _build_interest_payload(results)


def get_interest_payload():
    now = timezone.now()
    cached = TrendCache.objects.filter(keyword=CACHE_KEY).first()

    if cached and cached.last_fetched and now - cached.last_fetched < CACHE_TTL:
        data = cached.data or {}
        if data.get("categories"):
            return data

    fresh = fetch_newsdata_categories()
    if fresh.get("categories"):
        TrendCache.objects.update_or_create(
            keyword=CACHE_KEY,
            defaults={"data": fresh}
        )
        return fresh

    if cached and cached.data:
        return cached.data

    return {
        "categories": sorted(USER_INTERESTS.keys()),
        "keywords": {key: list(values) for key, values in USER_INTERESTS.items()}
    }


def get_interest_choices():
    payload = get_interest_payload()
    categories = payload.get("categories") or []
    if not categories:
        categories = sorted(USER_INTERESTS.keys())
    return [(category, category) for category in categories]
