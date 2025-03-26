from scraper import fetch_latest_news

def fact_check(query: str):
    """Fact-checks news by comparing with latest NewsAPI articles."""
    related_news = fetch_latest_news(query)

    if not related_news or isinstance(related_news, str):
        return "No relevant trusted news sources found."

    response = "Comparison with trusted news:\n"
    for article in related_news[:3]:
        response += f"- {article['title']} ({article['url']})\n"

    return response
