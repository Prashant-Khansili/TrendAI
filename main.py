from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import time
import pandas as pd
from ddgs import DDGS

pd.set_option('future.no_silent_downcasting', True)

# Define user interests and associated keywords
USER_INTERESTS = {
    "AI & Tech": ["artificial intelligence", "ai", "machine learning", "tech", "software"],
    "Finance": ["finance", "markets", "stocks", "economy"],
    "Law" : ["Law" , "Bar Council", "Legal", "Court", "Justice"],
    "Health": ["health", "medicine", "wellness", "fitness"],
    "Entertainment": ["entertainment", "movies", "music", "celebrities"],
    "India": ["India", "Indian", "Delhi", "Mumbai", "Bangalore"],
    "Indian Politics": ["Indian politics", "BJP", "Congress", "Modi", "Rahul Gandhi"],
    "Geopolitics": ["geopolitics", "international relations", "diplomacy", "global affairs"],
    "Competetive Exams": ["competitive exams", "UPSC", "SSC", "bank exams", "railway exams"],
    "Sports": ["sports", "football", "cricket", "tennis", "olympics" ,"IPL",  "FIFA", "NBA"],
    "Social Issues": ["social issues", "poverty", "inequality", "climate change", "human rights"]
    
}


def fetch_trends(keywords, retries=3, delay=10):
    if not keywords:
        return None
    pytrends = TrendReq(hl='en-US', tz=360)
    for i in range(retries):
        try:
            pytrends.build_payload(keywords, cat=0, timeframe='today 5-y', geo='', gprop='')
            trends = pytrends.interest_over_time()
            return trends
        except TooManyRequestsError:
            if i < retries - 1:
                print(f"Too many requests. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print("The request failed after multiple retries. Please wait a moment and try again.")
                return None


def get_duckduckgo_summary(topic):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(topic, max_results=3)
            for r in results:
                snippet = r.get("body")
                link = r.get("href")
                if snippet:
                    return f"{snippet}\n(Source: {link})"
        return f"No DuckDuckGo results found for '{topic}'."
    except Exception as e:
        return f"Error fetching DuckDuckGo summary: {e}"


def categorize_trend(topic, summary):
    """Categorizes a trend based on keywords in its title and summary."""
    text_to_check = (topic + " " + summary).lower()
    for category, keywords in USER_INTERESTS.items():
        if any(keyword in text_to_check for keyword in keywords):
            return category
    return None


if __name__ == "__main__":
    trending_topics = ["AI", "Machine Learning", "Stock Market", "Interest Rates"]
    interested_trends = []

    print("\n🔥 Personalized Trend Briefing\n")

    for topic in trending_topics:
        summary = get_duckduckgo_summary(topic)
        category = categorize_trend(topic, summary)

        if category:
            interested_trends.append(topic)
            print(f"--- {topic} ---")
            print(f"Category: {category}")
            print(summary)
            print("-" * 50)
            time.sleep(2)

    if interested_trends:
        trends_data = fetch_trends(interested_trends)
        if trends_data is not None and not trends_data.empty:
            print("\n📊 Google Trends Data for Your Interests:")
            print(trends_data)
        else:
            print("\nCould not fetch trends data for your interests.")
    else:
        print("No trends found matching your interests.")