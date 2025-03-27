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

def generate_embeddings():
    news_articles = list(collection.find({}, {"_id": 1, "title": 1}))

    if not news_articles:
        print("❌ No news articles found.")
        return

    print(f"✅ Processing {len(news_articles)} articles...")

    titles = [article["title"] for article in news_articles]
    vectors = model.encode(titles)

    dimension = vectors.shape[1]

    # Create or load FAISS index
    if os.path.exists(FAISS_INDEX):
        index = faiss.read_index(FAISS_INDEX)
        print(f"🔹 Adding {len(vectors)} new embeddings...")
    else:
        index = faiss.IndexFlatL2(dimension)
        print(f"🔹 Creating new FAISS index...")

    index.add(np.array(vectors))

    # Store embeddings in MongoDB
    for article, vector in zip(news_articles, vectors):
        collection.update_one(
            {"_id": article["_id"]},
            {"$set": {"embedding": vector.tolist()}},  # Convert NumPy array to list for MongoDB
            upsert=True
        )

    # Save FAISS index
    os.makedirs(os.path.dirname(FAISS_INDEX), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX)

    print("✅ Embeddings stored successfully!")

if __name__ == "__main__":
    generate_embeddings()
