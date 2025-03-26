# # import feedparser

# # # List of news RSS feeds
# # RSS_FEEDS = [
# #     "http://feeds.bbci.co.uk/news/rss.xml",
# #     "http://rss.cnn.com/rss/edition.rss",
# #     "http://feeds.reuters.com/reuters/topNews",
# #     "https://www.theguardian.com/world/rss",
# # ]

# # def get_news_by_keyword(keyword, num_articles=5):
# #     keyword = keyword.lower()  # Normalize for case-insensitive search
# #     matched_articles = []

# #     for url in RSS_FEEDS:
# #         print(f"\nFetching news from: {url}")
# #         feed = feedparser.parse(url)

# #         if not feed.entries:
# #             print("No articles found or invalid RSS feed.\n")
# #             continue

# #         for entry in feed.entries:
# #             title = entry.title.lower()
# #             summary = entry.get("summary", "").lower()  # Some feeds have summaries

# #             if keyword in title or keyword in summary:
# #                 matched_articles.append({
# #                     "title": entry.title,
# #                     "link": entry.link,
# #                     "published": entry.published
# #                 })
            
# #             if len(matched_articles) >= num_articles:
# #                 break  # Limit results

# #     return matched_articles

# # if __name__ == "__main__":
# #     user_query = input("Enter a topic to search news about: ").strip()
    
# #     if not user_query:
# #         print("No keyword entered! Exiting...")
# #     else:
# #         news_results = get_news_by_keyword(user_query)

# #         if news_results:
# #             print("\n🔍 Relevant News Articles:\n")
# #             for article in news_results:
# #                 print(f"Title: {article['title']}")
# #                 print(f"Link: {article['link']}")
# #                 print(f"Published: {article['published']}")
# #                 print("-" * 50)
# #         else:
# #             print("\nNo relevant news found for your topic!")

# import feedparser
# import newspaper
# from newspaper import Article
# import concurrent.futures

# # List of news RSS feeds (expandable)
# RSS_FEEDS = [
#     "http://feeds.bbci.co.uk/news/rss.xml",
#     "http://rss.cnn.com/rss/edition.rss",
#     "http://feeds.reuters.com/reuters/topNews",
#     "https://www.theguardian.com/world/rss",
# ]

# def extract_full_text(url):
#     """Extracts full news article text using newspaper3k."""
#     try:
#         article = Article(url)
#         article.download()
#         article.parse()
#         return article.text
#     except:
#         return ""

# def fetch_news_from_feed(url, keyword):
#     """Fetch and filter news articles from a given RSS feed URL."""
#     feed = feedparser.parse(url)
#     keyword = keyword.lower()
#     matched_articles = []

#     for entry in feed.entries:
#         title = entry.title
#         summary = entry.get("summary", "")
#         link = entry.link

#         # Extract full text of the article
#         full_text = extract_full_text(link)
#         content_to_search = f"{title} {summary} {full_text}".lower()

#         # Check if the keyword exists in title, summary, or full content
#         if keyword in content_to_search:
#             matched_articles.append({
#                 "title": title,
#                 "link": link,
#                 "published": entry.get("published", "Unknown Date"),
#                 "summary": summary[:300] + "..."  # Short preview
#             })

#     return matched_articles

# def get_news_by_keyword(keyword):
#     """Fetch news in parallel from multiple RSS feeds and filter based on keyword."""
#     matched_articles = []
    
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         # Fetch news from all feeds concurrently
#         results = executor.map(lambda url: fetch_news_from_feed(url, keyword), RSS_FEEDS)
        
#         for result in results:
#             matched_articles.extend(result)

#     return matched_articles

# if __name__ == "__main__":
#     user_query = input("Enter a topic to search news about: ").strip()
    
#     if not user_query:
#         print("No keyword entered! Exiting...")
#     else:
#         print("\nFetching news... Please wait.\n")
#         news_results = get_news_by_keyword(user_query)

#         if news_results:
#             print("\n🔍 Relevant News Articles:\n")
#             for article in news_results[:10]:  # Show top 10 results
#                 print(f"Title: {article['title']}")
#                 print(f"Summary: {article['summary']}")
#                 print(f"Link: {article['link']}")
#                 print(f"Published: {article['published']}")
#                 print("-" * 50)
#         else:
#             print("\nNo relevant news found for your topic!")
# import requests
# from bs4 import BeautifulSoup
# import feedparser
# from pymongo import MongoClient
# from flask import Flask, jsonify
# import threading
# import time
# import logging
# from sentence_transformers import SentenceTransformer  # Import embedding model

# # Setup logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# # Flask API setup
# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient("mongodb://localhost:27017/")
# db = client["news_db"]
# collection = db["articles"]

# # Ensure index for vector search
# collection.create_index("link", unique=True)

# # Load the Sentence Transformer model for generating vector embeddings
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# # List of news sources
# RSS_FEEDS = [
#     "https://rss.cnn.com/rss/cnn_topstories.rss",
#     "https://feeds.bbci.co.uk/news/rss.xml"
# ]

# NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
# NEWS_API_KEY = "5bb8175f41824a08951381bf4c1fdb3a"

# # Function to generate vector embeddings
# def generate_embedding(text):
#     return model.encode(text).tolist()  # Convert to list for MongoDB storage

# # Function to fetch news from RSS Feeds
# def fetch_rss_news():
#     logging.info("Fetching news from RSS feeds...")
#     for feed_url in RSS_FEEDS:
#         try:
#             feed = feedparser.parse(feed_url)
#             for entry in feed.entries:
#                 news_text = f"{entry.title} {entry.link}"  # Combine title + link for better embedding
#                 news_data = {
#                     "title": entry.title,
#                     "link": entry.link,
#                     "source": feed_url,
#                     "published": entry.published,
#                     "vector": generate_embedding(news_text)  # Store vector embeddings
#                 }
#                 collection.update_one({"link": entry.link}, {"$set": news_data}, upsert=True)
#                 logging.info(f"✅ Stored: {entry.title} - {entry.link}")
#         except Exception as e:
#             logging.error(f"Error fetching RSS feed {feed_url}: {e}")

# # Function to fetch news from News API
# def fetch_news_api():
#     logging.info("Fetching news from News API...")
#     params = {"country": "us", "apiKey": NEWS_API_KEY}
#     try:
#         response = requests.get(NEWS_API_URL, params=params, timeout=10)
#         if response.status_code == 200:
#             articles = response.json().get("articles", [])
#             for article in articles:
#                 news_text = f"{article['title']} {article['url']}"
#                 news_data = {
#                     "title": article["title"],
#                     "link": article["url"],
#                     "source": article["source"]["name"],
#                     "published": article["publishedAt"],
#                     "vector": generate_embedding(news_text)  # Store vector embeddings
#                 }
#                 collection.update_one({"link": article["url"]}, {"$set": news_data}, upsert=True)
#                 logging.info(f"✅ Stored: {article['title']} - {article['url']}")
#         else:
#             logging.error(f"News API failed with status code {response.status_code}")
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error fetching news from API: {e}")

# # Function to scrape news from a website
# def scrape_news():
#     logging.info("Scraping news from BBC...")
#     url = "https://www.bbc.com/news"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, "html.parser")
#             articles = soup.find_all("h3")
#             for article in articles:
#                 link = article.find("a")
#                 if link and "href" in link.attrs:
#                     full_link = "https://www.bbc.com" + link["href"]
#                     news_text = f"{article.text.strip()} {full_link}"
#                     news_data = {
#                         "title": article.text.strip(),
#                         "link": full_link,
#                         "source": "BBC",
#                         "published": time.strftime("%Y-%m-%d %H:%M:%S"),
#                         "vector": generate_embedding(news_text)  # Store vector embeddings
#                     }
#                     collection.update_one({"link": full_link}, {"$set": news_data}, upsert=True)
#                     logging.info(f"✅ Stored: {article.text.strip()} - {full_link}")
#         else:
#             logging.error(f"BBC Scraping failed with status code {response.status_code}")
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error scraping news from BBC: {e}")

# # Background thread for news fetching
# def background_task():
#     while True:
#         logging.info("\n🔄 Updating news every 60 seconds...\n")
#         fetch_rss_news()
#         fetch_news_api()
#         scrape_news()
#         logging.info("\n🕒 Waiting for next update...\n")
#         time.sleep(60)  # Updates every minute

# # API to fetch stored news
# @app.route("/news", methods=["GET"])
# def get_news():
#     try:
#         news = list(collection.find({}, {"_id": 0}))
#         return jsonify(news)
#     except Exception as e:
#         logging.error(f"Error fetching news from database: {e}")
#         return jsonify({"error": "Internal Server Error"}), 500

# if __name__ == "__main__":
#     threading.Thread(target=background_task, daemon=True).start()
#     app.run(debug=True, port=5000)



import requests
import time
import schedule
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import nltk
import re

# Load SBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

# API Key for NewsAPI (Get yours at https://newsapi.org)
NEWS_API_KEY = "5bb8175f41824a08951381bf4c1fdb3a"
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

# FAISS Index for storing news embeddings
d = 384  # Dimensionality of SBERT embeddings
index = faiss.IndexFlatL2(d)

news_store = []  # Store news articles

# Preprocessing function
def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special chars
    text = text.lower().strip()
    return text

# Fetch and process news
def fetch_news():
    global news_store

    response = requests.get(NEWS_URL)
    if response.status_code != 200:
        print("⚠️ Failed to fetch news.")
        return

    news_data = response.json()["articles"]
    new_articles = []

    for article in news_data:
        title = clean_text(article["title"])
        if title and title not in news_store:
            new_articles.append(title)
            news_store.append(title)

    if new_articles:
        print(f"\n🔄 Updating news at {time.strftime('%H:%M:%S')} ...")
        embed_and_store(new_articles)

# Generate embeddings and store in FAISS
def embed_and_store(news_list):
    global index

    embeddings = model.encode(news_list, convert_to_numpy=True)
    index.add(embeddings)

    # Show top 5 recent news
    print("\n📰 Latest News Updates:")
    for i, news in enumerate(news_list[:5]):
        print(f"{i+1}. {news}")

# Scheduler to update news every minute
schedule.every(1).minutes.do(fetch_news)

if __name__ == "__main__":
    print("🚀 News Scraper Running... Press Ctrl+C to stop.")
    fetch_news()  # Initial fetch
    while True:
        schedule.run_pending()
        time.sleep(10)
