from fastapi import FastAPI, Query
from search_news import search_similar_articles

app = FastAPI()

@app.get("/search")
def search_news(query: str = Query(..., description="Enter your news query")):
    results = search_similar_articles(query)
    if not results:
        return {"message": "No relevant news articles found."}
    return {"articles": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
