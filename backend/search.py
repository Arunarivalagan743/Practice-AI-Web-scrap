from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pymongo import MongoClient
import os

# Load Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["political_news"]

FAISS_INDEX = "data/news_index.faiss"

def search_similar_articles(query, top_k=5):
    if not os.path.exists(FAISS_INDEX):
        print("❌ FAISS index not found.")
        return []

    index = faiss.read_index(FAISS_INDEX)
    query_vector = model.encode([query])
    
    distances, indices = index.search(np.array(query_vector), top_k)
    
    results = []
    for i in indices[0]:
        article = collection.find_one({}, {"_id": 0, "title": 1, "link": 1, "description": 1})
        if article:
            results.append(article)

    return results

if __name__ == "__main__":
    query = "US elections latest update"
    similar_articles = search_similar_articles(query)
    
    for article in similar_articles:
        print(f"🔹 {article['title']} - {article['link']}")
