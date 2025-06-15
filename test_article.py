import asyncio
import aiohttp
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.models import Article
from app import db, create_app
from sqlalchemy import inspect

app = create_app()  # Use your Flask application factory

queries = ["Central Railways", "Western Railways", "Mumbai Metro", "Indian Railways", 
           "Mumbai Local", "Mumbai Bus", "Mumbai", "Kanpur Metro", "Bengaluru Metro"]

async def get_final_image_url(session, image_url):
    """Get final image URL after following redirects"""
    try:
        async with session.head(image_url, allow_redirects=True) as response:
            return str(response.url) if response.status == 200 else "https://via.placeholder.com/150"
    except Exception:
        return "https://via.placeholder.com/150"

async def scrape_google_news():
    """Main scraping function that runs periodically"""
    with app.app_context():
        base_url = "https://news.google.com"
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_articles(session, base_url, f"{base_url}/search?q={query}&hl=en-US&gl=US&ceid=US%3Aen", query) 
                    for query in queries]
            await asyncio.gather(*tasks)

async def fetch_articles(session, base_url, url, query):
    """Fetch and process articles for a specific query"""
    async with session.get(url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), "html.parser")
            articles = soup.find_all("article")
            today = datetime.utcnow().date()

            image_tasks = []
            articles_to_add = []

            for article in articles:
                headline_element = article.find("a", class_="JtKRv")
                if not headline_element:
                    continue
                    
                headline = headline_element.text.strip()
                link = base_url + headline_element["href"][1:]
                
                source_element = article.find("div", class_="vr1PYe")
                source = source_element.text.strip() if source_element else "N/A"
                
                date_element = article.find("time")
                if not date_element:
                    continue
                    
                date_str = date_element["datetime"]
                try:
                    article_date = datetime.fromisoformat(date_str).date()
                    if article_date != today:  # Only keep today's articles
                        continue
                except ValueError:
                    continue
                
                description_element = article.find("div", class_="B6pJDd")
                description = description_element.text.strip() if description_element else "N/A"
                
                image_element = article.find("img", class_="Quavad")
                image_url = image_element["src"] if image_element else "https://via.placeholder.com/150"
                if image_url.startswith("/"):
                    image_url = base_url + image_url

                image_tasks.append(get_final_image_url(session, image_url))
                
                articles_to_add.append({
                    "headline": headline,
                    "link": link,
                    "source": source,
                    "date": datetime.fromisoformat(date_str),
                    "description": description,
                    "image_url": "",  # Will be updated later
                    "query": query
                })

            # Get all image URLs concurrently
            final_image_urls = await asyncio.gather(*image_tasks)

            # Save articles to database
            for idx, article_data in enumerate(articles_to_add):
                article_data['image_url'] = final_image_urls[idx]
                
                # Check if article already exists
                existing = Article.query.filter_by(link=article_data['link']).first()
                if not existing:
                    try:
                        new_article = Article(
                            headline=article_data['headline'],
                            link=article_data['link'],
                            source=article_data['source'],
                            date=article_data['date'],
                            description=article_data['description'],
                            image_url=article_data['image_url'],
                            search_query=article_data['query']
                        )
                        db.session.add(new_article)
                    except Exception as e:
                        app.logger.error(f"Error adding article: {e}")
            
            db.session.commit()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scrape_google_news, 'interval', minutes=60)  # Run every hour
scheduler.start()


def initialize_database():
    """Ensure database tables exist"""
    with app.app_context():
        inspector = inspect(db.engine)
        if 'articles' not in inspector.get_table_names():
            db.create_all()
            print("Created database tables")

if __name__ == '__main__':
    initialize_database()
    asyncio.run(scrape_google_news())  # Initial scrape
    app.run(debug=True)












# from app.models import Article
# from app import db, create_app
# from datetime import datetime, timedelta
# import random
# from faker import Faker
# import asyncio
# from aiohttp import ClientSession
# from bs4 import BeautifulSoup
# from sqlalchemy import inspect

# # Initialize Faker for generating fake data
# fake = Faker()

# async def get_final_image_url(session, image_url):
#     try:
#         async with session.head(image_url, allow_redirects=True) as response:
#             if response.status == 200:
#                 return str(response.url)
#             else:
#                 return "https://via.placeholder.com/150"
#     except Exception:
#         return "https://via.placeholder.com/150"

# async def fetch_articles(session, base_url, url, query):
#     # Your existing fetch_articles implementation
#     pass

# def generate_sample_articles(count=15):
#     """Generate sample articles with realistic data"""
#     sources = ["CNN", "BBC", "Reuters", "The Guardian", "New York Times", "Washington Post"]
#     search_queries = ["technology", "politics", "health", "business", "sports", "entertainment"]
    
#     articles = []
#     for i in range(count):
#         # Generate dates within the last 30 days
#         date = datetime.now() - timedelta(days=random.randint(0, 30))
        
#         articles.append({
#             "headline": fake.sentence(nb_words=8),
#             "link": f"https://example.com/article_{i+1}",
#             "source": random.choice(sources),
#             "date": date,
#             "description": fake.paragraph(nb_sentences=3),
#             "image_url": f"https://picsum.photos/800/400?random={i}",
#             "search_query": random.choice(search_queries)
#         })
    
#     return articles





# if __name__ == '__main__':
#     app = create_app()
#     with app.app_context():
#         # Check if tables exist
#         inspector = inspect(db.engine)
#         tables = inspector.get_table_names()
#         print("All tables in the database:", tables)
        
#         # Clear existing articles (optional)
#         # db.session.query(Article).delete()
#         # db.session.commit()
        
#         # Generate and add sample articles
#         sample_articles = generate_sample_articles(40)
        
#         for article_data in sample_articles:
#             # Check if article already exists
#             existing_article = Article.query.filter_by(link=article_data['link']).first()
#             if not existing_article:
#                 try:
#                     new_article = Article(
#                         headline=article_data['headline'],
#                         link=article_data['link'],
#                         source=article_data['source'],
#                         date=article_data['date'],
#                         description=article_data['description'],
#                         image_url=article_data['image_url'],
#                         search_query=article_data['search_query']
#                     )
#                     db.session.add(new_article)
#                     print(f"Added article: {article_data['headline']}")
#                 except Exception as e:
#                     app.logger.error(f"Error adding article: {e}")
        
#         db.session.commit()
#         print(f"Successfully added {len(sample_articles)} sample articles to the database!")













# from app.models import Article
# from app import db, create_app  # Ensure create_app is imported from app/__init__.py
# from datetime import datetime
# import asyncio
# from aiohttp import ClientSession
# from bs4 import BeautifulSoup
# from sqlalchemy import inspect


# async def get_final_image_url(session, image_url):
#     try:
#         async with session.head(image_url, allow_redirects=True) as response:
#             if response.status == 200:
#                 return str(response.url)
#             else:
#                 return "https://via.placeholder.com/150"
#     except Exception:
#         return "https://via.placeholder.com/150"


# async def fetch_articles(session, base_url, url, query):
#     async with session.get(url) as response:
#         if response.status == 200:
#             soup = BeautifulSoup(await response.text(), "html.parser")
#             articles = soup.find_all("article")

#             image_tasks = []
#             today = datetime.utcnow().date()

#             articles_data = []
#             for article in articles:
#                 headline_element = article.find("a", class_="DY5T1d")
#                 headline = headline_element.text.strip() if headline_element else "N/A"
#                 link = base_url + headline_element["href"][1:] if headline_element else "N/A"

#                 source_element = article.find("div", class_="SVJrMe")
#                 source = source_element.text.strip() if source_element else "N/A"

#                 date_element = article.find("time")
#                 date = date_element["datetime"] if date_element else "N/A"
#                 article_date = datetime.fromisoformat(date).date() if date != "N/A" else None

#                 if article_date != today:
#                     continue

#                 description_element = article.find("div", class_="xBbh9")
#                 description = description_element.text.strip() if description_element else "N/A"

#                 image_element = article.find("img", class_="tvs3Id")
#                 image_url = image_element["src"] if image_element else "https://via.placeholder.com/150"

#                 if image_url.startswith("/") or image_url.startswith("."):
#                     image_url = base_url + image_url

#                 image_tasks.append(get_final_image_url(session, image_url))

#                 articles_data.append({
#                     "headline": headline,
#                     "link": link,
#                     "source": source,
#                     "date": date,
#                     "description": description,
#                     "image_url": "",
#                     "query": query
#                 })

#             # Resolve image URLs asynchronously
#             final_image_urls = await asyncio.gather(*image_tasks)

#             # Save articles to database
#             for idx, article in enumerate(articles_data):
#                 article['image_url'] = final_image_urls[idx]

#                 # Check for existing articles
#                 existing_article = Article.query.filter_by(link=article['link']).first()
#                 if not existing_article:
#                     try:
#                         new_article = Article(
#                             headline=article['headline'],
#                             link=article['link'],
#                             source=article['source'],
#                             date=datetime.fromisoformat(article['date']),
#                             description=article['description'],
#                             image_url=article['image_url'],
#                             search_query=article['query']
#                         )
#                         db.session.add(new_article)
#                     except Exception as e:
#                         current_app.logger.error(f"Error adding article: {e}")
#             db.session.commit()


# # Test database connection and table
# if __name__ == '__main__':
#     # Initialize the Flask app and push the application context
#     app = create_app()  # Ensure you have a `create_app` function in your `__init__.py`
#     with app.app_context():
#         # Get the inspector for the database engine
#         inspector = inspect(db.engine)
        
#         # Retrieve all table names
#         tables = inspector.get_table_names()

#         # Check and print all tables in the database
#         print("All tables in the database:", tables)

#         # Add a test article
#         test_article = Article(
#             headline="Sample Headline",
#             link="https://example.com",
#             source="Example Source",
#             date=datetime.strptime("2024-11-24", "%Y-%m-%d"),  # Correctly convert the date
#             description="This is a test description.",
#             image_url="https://example.com/image.jpg",
#             search_query="test"
#         )
#         db.session.add(test_article)
#         db.session.commit()
#         print("Article added successfully!")





# Test database connection and table
# if __name__ == '__main__':
#     # Initialize the Flask app and push the application context
#     app = create_app()  # Ensure you have a `create_app` function in your `__init__.py`
#     with app.app_context():
#         # Check if table exists
#         print("All tables in the database:", db.engine.table_names())

#         # Scrape data (use any query you want, here using a sample query "test")
#         query = "test"
#         base_url = "https://news.google.com"
#         url = f"{base_url}/search?q={query}&hl=en-US&gl=US&ceid=US%3Aen"

#         # Start the scraping process
#         async def run_scraping():
#             async with ClientSession() as session:
#                 await fetch_articles(session, base_url, url, query)

#         # Run the scraping function
#         asyncio.run(run_scraping())















# from app.models import Article
# from app import db, create_app  # Ensure create_app is imported from app/__init__.py

# # Test database connection and table
# if __name__ == '__main__':
#     # Initialize the Flask app and push the application context
#     app = create_app()  # Ensure you have a `create_app` function in your `__init__.py`
#     with app.app_context():
#         # Check if table exists
#         print("All tables in the database:", db.engine.table_names())

#         # Add a test article
#         test_article = Article(
#             headline="Sample Headline",
#             link="https://example.com",
#             source="Example Source",
#             date="2024-11-24",
#             description="This is a test description.",
#             image_url="https://example.com/image.jpg",
#             search_query="test"
#         )
#         db.session.add(test_article)
#         db.session.commit()
#         print("Article added successfully!")
