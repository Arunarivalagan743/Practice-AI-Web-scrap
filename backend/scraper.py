# import requests
# import json
# import os
# from bs4 import BeautifulSoup

# NEWS_FILE = "data/news.json"

# def scrape_news():
#     url = "https://www.bbc.com/news"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)

#     if response.status_code != 200:
#         print(f"❌ Error: Unable to fetch page. Status code: {response.status_code}")
#         return []

#     soup = BeautifulSoup(response.text, "html.parser")

#     articles = []

#     # ✅ Try a different selector for headlines
#     for item in soup.select("a[href^='/news']"):  
#         title = item.get_text(strip=True)
#         link = "https://www.bbc.com" + item["href"]
#         articles.append({"title": title, "link": link})

#     if not articles:
#         print("⚠️ No articles found. BBC may have changed their structure.")

#     # ✅ Ensure `data/` directory exists
#     os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)

#     # ✅ Save to JSON file
#     with open(NEWS_FILE, "w", encoding="utf-8") as f:
#         json.dump(articles, f, indent=4, ensure_ascii=False)

#     print(f"✅ Scraped {len(articles)} articles.")
#     return articles

# if __name__ == "__main__":
#     print("🚀 Scraping news...")
#     scrape_news()
#     print("✅ News saved successfully!")




import requests
from bs4 import BeautifulSoup
import json
import os

NEWS_FILE = "data/news.json"

def scrape_news():
    url = "https://www.bbc.com/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error: Unable to fetch page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    
    for item in soup.select("a[href^='/news']"):
        title = item.get_text(strip=True)
        link = item.get("href")

        if link and not link.startswith("http"):
            link = "https://www.bbc.com" + link

        if title and link:
            articles.append({"title": title, "link": link})

    return articles

def save_news_to_json(news):
    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(news, f, indent=4, ensure_ascii=False)
    print(f"✅ News articles saved to `{NEWS_FILE}`.")

if __name__ == "__main__":
    print("🚀 Fetching BBC News...")
    news = scrape_news()

    if news:
        save_news_to_json(news)
    else:
        print("❌ No news articles found.")
