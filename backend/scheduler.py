from apscheduler.schedulers.background import BackgroundScheduler
from scraper import scrape_news
from embeddings import generate_embeddings

def update_news():
    print("Updating news and embeddings...")
    scrape_news()
    generate_embeddings()
    print("Update complete!")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_news, "interval", minutes=30)
    scheduler.start()

    print("Scheduler running. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
