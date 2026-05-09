from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import time
import pandas as pd
from ddgs import DDGS
import json
import requests

pd.set_option('future.no_silent_downcasting', True)

# Define user interests and associated keywords
USER_INTERESTS = {
    "AI & Tech": ["artificial intelligence", "ai","MCP" "machine learning", "tech", "software"],
    "Finance": ["finance", "markets", "stocks", "economy", "interest rates"],
    "Law" : ["Law" , "Bar Council", "Legal", "Court", "Justice"],
    "Health": ["health", "medicine", "wellness", "fitness"],
    "Entertainment": ["entertainment", "movies", "music", "celebrities"],
    "India": ["India", "Indian", "Delhi", "Mumbai", "Bangalore"],
    "Indian Politics": ["Indian politics", "BJP", "Congress", "Modi", "Rahul Gandhi"],
    "Geopolitics": ["geopolitics", "international relations", "diplomacy", "global affairs"],
    "Competitive Exams": ["competitive exams", "UPSC", "SSC", "bank exams", "railway exams"],
    "Sports": ["sports", "football", "cricket", "tennis", "olympics" ,"IPL",  "FIFA", "NBA"],
    "Social Issues": ["social issues", "poverty", "inequality", "climate change", "human rights"]
}


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


def get_trends_briefing():
    trending_topics = ["AI", "Machine Learning", "Stock Market", "Interest Rates", "UPSC Exams", "Indian Premier League"]
    structured_trends = []

    for topic in trending_topics:
        summary, source = get_duckduckgo_summary(topic)
        category = categorize_trend(topic, summary)

        if category:
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
