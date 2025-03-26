# from sentence_transformers import SentenceTransformer
# import faiss
# import json
# import os
# import numpy as np

# NEWS_FILE = "data/news.json"
# FAISS_INDEX = "data/news_index.faiss"

# # Load model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# def generate_embeddings():
#     # ✅ Ensure `news.json` exists
#     if not os.path.exists(NEWS_FILE):
#         print(f"❌ Error: {NEWS_FILE} not found! Run `scraper.py` first.")
#         return

#     # ✅ Read news articles safely
#     try:
#         with open(NEWS_FILE, "r", encoding="utf-8") as f:
#             news_articles = json.load(f)
#     except json.JSONDecodeError:
#         print(f"❌ Error: {NEWS_FILE} is empty or corrupted!")
#         return

#     if not news_articles:
#         print("❌ Error: No news articles found in `news.json`.")
#         return

#     print(f"✅ Processing {len(news_articles)} articles...")

#     # Extract titles and encode them
#     titles = [article["title"] for article in news_articles]
#     vectors = model.encode(titles)

#     # Store in FAISS
#     dimension = vectors.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(np.array(vectors))

#     # Save FAISS index
#     os.makedirs(os.path.dirname(FAISS_INDEX), exist_ok=True)
#     faiss.write_index(index, FAISS_INDEX)

#     print("✅ Embeddings stored successfully!")

# if __name__ == "__main__":
#     print("🚀 Generating embeddings...")
#     generate_embeddings()
from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import numpy as np

NEWS_FILE = "data/news.json"
FAISS_INDEX = "data/news_index.faiss"

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings():
    if not os.path.exists(NEWS_FILE):
        print(f"❌ Error: {NEWS_FILE} not found! Run `scraper.py` first.")
        return

    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            news_articles = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Error: {NEWS_FILE} is empty or corrupted!")
        return

    if not news_articles:
        print("❌ Error: No news articles found in `news.json`.")
        return

    print(f"✅ Processing {len(news_articles)} articles...")

    titles = [article["title"] for article in news_articles]
    vectors = model.encode(titles)

    dimension = vectors.shape[1]


    if os.path.exists(FAISS_INDEX):
        index = faiss.read_index(FAISS_INDEX)
        print(f"🔹 Adding {len(vectors)} new embeddings to FAISS...")
    else:
        index = faiss.IndexFlatL2(dimension)
        print(f"🔹 Creating new FAISS index with {len(vectors)} embeddings...")

    index.add(np.array(vectors))

    # ✅ Save FAISS index
    os.makedirs(os.path.dirname(FAISS_INDEX), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX)

    print("✅ Embeddings stored successfully!")

if __name__ == "__main__":
    print("🚀 Generating embeddings...")
    generate_embeddings()
