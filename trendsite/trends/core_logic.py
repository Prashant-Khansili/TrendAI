from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import time
import pandas as pd
from ddgs import DDGS
import json
import requests
from .interests import USER_INTERESTS

pd.set_option('future.no_silent_downcasting', True)


def fetch_trends_safely(keywords, retries=3, delay=10):
    """
    Fetches Google Trends data for a list of keywords, skipping any that cause errors.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    all_trends = []

    for keyword in keywords:
        print(f"Fetching trend for: {keyword}")
        for i in range(retries):
            try:
                pytrends.build_payload([keyword], cat=0, timeframe='today 5-y', geo='', gprop='')
                trend_df = pytrends.interest_over_time()
                if not trend_df.empty:
                    all_trends.append(trend_df.drop(columns='isPartial'))
                break  # Success, break retry loop
            except TooManyRequestsError:
                if i < retries - 1:
                    print(f"Too many requests for '{keyword}'. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"Skipping '{keyword}' after multiple failed attempts (Too Many Requests).")
            except requests.exceptions.RequestException as e:
                # Catching generic request exceptions, including 400 errors
                print(f"Could not fetch trend for '{keyword}'. It may be an invalid term. Skipping.")
                break # Break retry loop on client error
            except Exception as e:
                print(f"An unexpected error occurred for '{keyword}': {e}. Skipping.")
                break

    if not all_trends:
        return None

    # Concatenate all successful dataframes
    final_df = pd.concat(all_trends, axis=1)
    final_df = final_df.loc[:,~final_df.columns.duplicated()] # Remove duplicate columns if any
    return final_df


def get_duckduckgo_summary(topic):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(topic, max_results=3)
            for r in results:
                snippet = r.get("body")
                link = r.get("href")
                if snippet:
                    return snippet, link
        return f"No DuckDuckGo results found for '{topic}'.", None
    except Exception as e:
        return f"Error fetching DuckDuckGo summary: {e}", None


def categorize_trend(topic, summary):
    """Categorizes a trend based on keywords in its title and summary."""
    text_to_check = (topic + " " + summary).lower()
    for category, keywords in USER_INTERESTS.items():
        if any(keyword in text_to_check for keyword in keywords):
            return category
    return "General"


def get_realtime_trends():
    """Fetches real-time trending searches from Google Trends."""
    try:
    
        pytrends = TrendReq(hl='en-US', tz=360)
        # Use realtime_trending_searches for more reliable real-time data
        trending_searches_df = pytrends.realtime_trending_searches(pn='US') 
        return trending_searches_df['title'].tolist()
    except Exception as e:
        print(f"Could not fetch real-time trends: {e}")
        return []

def get_trends_briefing(selected_interests=None):
    trending_topics = get_realtime_trends()
    if not trending_topics:
        trending_topics = ["AI", "Machine Learning", "Stock Market", "Interest Rates", "UPSC Exams", "Indian Premier League"] # Fallback
    
    structured_trends = []
    selected_set = set(selected_interests or [])

    for topic in trending_topics[:20]: # Limit to top 20 topics
        summary, source = get_duckduckgo_summary(topic)
        category = categorize_trend(topic, summary)

        if category and (not selected_set or category in selected_set):
            trend_object = {
                "topic": topic,
                "context": summary,
                "category": category,
                "source": source
            }
            structured_trends.append(trend_object)
            time.sleep(1)
    
    return structured_trends

if __name__ == "__main__":
    briefing = get_trends_briefing()
    print(json.dumps(briefing, indent=4))
