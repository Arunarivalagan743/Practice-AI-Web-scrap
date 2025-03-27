import requests
import feedparser
import json
import time
import logging
from pymongo import MongoClient
from bs4 import BeautifulSoup

# ✅ Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["political_news"]

# ✅ Create unique index on "link" to prevent duplicates
collection.create_index("link", unique=True)

# ✅ RSS Feeds
RSS_FEEDS = [
    "https://rss.cnn.com/rss/cnn_allpolitics.rss",
    "https://feeds.bbci.co.uk/news/politics/rss.xml"
]

# 🔹 1️⃣ BBC Politics Web Scraper
def scrape_news():
    url = "https://www.bbc.com/news/politics"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        articles = soup.find_all("div", class_="gs-c-promo-body")
        
        for article in articles:
            link = article.find("a", class_="gs-c-promo-heading")
            description = article.find("p", class_="gs-c-promo-summary")
            
            if link and "href" in link.attrs:
                full_link = "https://www.bbc.com" + link["href"]
                
                # Skip if article already exists
                if collection.find_one({"link": full_link}):
                    logging.info(f"🔄 Skipping (Already Exists): {full_link}")
                    continue  

                news_data = {
                    "title": article.find("h3").text.strip() if article.find("h3") else "No Title",
                    "link": full_link,
                    "source": "BBC",
                    "description": description.text.strip() if description else "No description available",
                    "published": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Insert only if new
                collection.update_one({"link": full_link}, {"$setOnInsert": news_data}, upsert=True)
                logging.info(f"✅ Scraped: {news_data['title']}")
    
    except requests.RequestException as e:
        logging.error(f"❌ Error scraping BBC Politics: {e}")

# 🔹 2️⃣ RSS Feed Parser
def fetch_rss_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            if collection.find_one({"link": entry.link}):  # Skip duplicates
                logging.info(f"🔄 Skipping (Already Exists): {entry.link}")
                continue  

            news_data = {
                "title": entry.title,
                "link": entry.link,
                "source": feed.feed.title if "title" in feed.feed else "Unknown Source",
                "description": entry.summary if "summary" in entry else "No description available",
                "published": entry.published if "published" in entry else time.strftime("%Y-%m-%d %H:%M:%S")
            }

            collection.update_one({"link": entry.link}, {"$setOnInsert": news_data}, upsert=True)
            logging.info(f"✅ Fetched RSS: {entry.title}")

# 🔹 3️⃣ Save News to JSON
def save_news_to_json():
    news_list = list(collection.find({}, {"_id": 0}).limit(100))
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, indent=4, ensure_ascii=False)
    
    logging.info("✅ News saved in news.json")

# 🔹 4️⃣ Auto Update Every 1 Minute
def update_news():
    while True:
        logging.info("\n🔄 Updating news...")
        fetch_rss_news()
        scrape_news()
        save_news_to_json()
        logging.info("\n🕒 Waiting for the next update...\n")
        time.sleep(60)

# 🔍 5️⃣ SEARCH FUNCTION
def search_news(keyword):
    query = {"$text": {"$search": keyword}}  # MongoDB Text Search
    results = list(collection.find(query, {"_id": 0}).limit(10))

    if results:
        for article in results:
            print(f"\n🔹 Title: {article['title']}\n🔗 Link: {article['link']}\n📅 Published: {article['published']}\n")
    else:
        print("❌ No matching news found.")

# 🏁 MAIN FUNCTION
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        keyword = " ".join(sys.argv[2:])
        search_news(keyword)
    else:
        update_news()
