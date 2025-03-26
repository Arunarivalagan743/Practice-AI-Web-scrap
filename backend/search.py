from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

NEWS_FILE = "data/news.json"
FAISS_INDEX = "data/news_index.faiss"

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_news(query, threshold=0.8):
    # Load FAISS index and news data
    index = faiss.read_index(FAISS_INDEX)
    with open(NEWS_FILE, "r") as f:
        news_articles = json.load(f)

    # Convert query to vector
    query_vector = model.encode([query])

    # Search FAISS for similar articles
    D, I = index.search(np.array(query_vector), k=len(news_articles))

    # Filter results
    relevant_articles = []
    for i, score in zip(I[0], D[0]):
        if i != -1 and score < threshold:  # Lower distance = better match
            relevant_articles.append(news_articles[i])

    return relevant_articles
