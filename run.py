from app import create_app, db
from app.scraper import scrape_google_news
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

app = create_app()

# Scheduler to scrape articles every 60 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(scrape_google_news()), 'interval', minutes=60)
scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
