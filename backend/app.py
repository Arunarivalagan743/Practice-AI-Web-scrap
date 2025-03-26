from fastapi import FastAPI
from search import search_news

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the News Search API. Use /search?query=your_query"}

@app.get("/search")
def search_news_api(query: str):
    results = search_news(query)
    return {"query": query, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
