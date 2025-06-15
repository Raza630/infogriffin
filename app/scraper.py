from flask import current_app
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from datetime import datetime
from app.models import Article
from app import db

async def scrape_google_news(query=""):
    base_url = "https://news.google.com"
    url = f"{base_url}/search?q={query}&hl=en-US&gl=US&ceid=US%3Aen"
    async with ClientSession() as session:
        await fetch_articles(session, base_url, url, query)

async def get_final_image_url(session, image_url):
    try:
        async with session.head(image_url, allow_redirects=True) as response:
            if response.status == 200:
                return str(response.url)
            else:
                return "https://via.placeholder.com/150"
    except Exception:
        return "https://via.placeholder.com/150"

async def fetch_articles(session, base_url, url, query):
    async with session.get(url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), "html.parser")
            articles = soup.find_all("article")

            image_tasks = []
            today = datetime.utcnow().date()

            articles_data = []
            for article in articles:
                headline_element = article.find("a", class_="DY5T1d")
                headline = headline_element.text.strip() if headline_element else "N/A"
                link = base_url + headline_element["href"][1:] if headline_element else "N/A"

                source_element = article.find("div", class_="SVJrMe")
                source = source_element.text.strip() if source_element else "N/A"

                date_element = article.find("time")
                date = date_element["datetime"] if date_element else "N/A"
                article_date = datetime.fromisoformat(date).date() if date != "N/A" else None

                if article_date != today:
                    continue

                description_element = article.find("div", class_="xBbh9")
                description = description_element.text.strip() if description_element else "N/A"

                image_element = article.find("img", class_="tvs3Id")
                image_url = image_element["src"] if image_element else "https://via.placeholder.com/150"

                if image_url.startswith("/") or image_url.startswith("."):
                    image_url = base_url + image_url

                image_tasks.append(get_final_image_url(session, image_url))

                articles_data.append({
                    "headline": headline,
                    "link": link,
                    "source": source,
                    "date": date,
                    "description": description,
                    "image_url": "",
                    "query": query
                })

            # Resolve image URLs asynchronously
            final_image_urls = await asyncio.gather(*image_tasks)

            # Save articles to database
            for idx, article in enumerate(articles_data):
                article['image_url'] = final_image_urls[idx]

                # Check for existing articles
                existing_article = Article.query.filter_by(link=article['link']).first()
                if not existing_article:
                    try:
                        new_article = Article(
                            headline=article['headline'],
                            link=article['link'],
                            source=article['source'],
                            date=datetime.fromisoformat(article['date']),
                            description=article['description'],
                            image_url=article['image_url'],
                            search_query=article['query']
                        )
                        db.session.add(new_article)
                    except Exception as e:
                        current_app.logger.error(f"Error adding article: {e}")
            db.session.commit()











# import asyncio
# from aiohttp import ClientSession
# from bs4 import BeautifulSoup
# from datetime import datetime
# from .models import Article
# from . import db

# async def scrape_google_news():
#     base_url = "https://news.google.com"
#     url = f"{base_url}/search?q=&hl=en-US&gl=US&ceid=US%3Aen"
#     async with ClientSession() as session:
#         await fetch_articles(session, base_url, url)

# async def get_final_image_url(session, image_url):
#     try:
#         async with session.head(image_url, allow_redirects=True) as response:
#             if response.status == 200:
#                 return str(response.url)
#             else:
#                 return "https://via.placeholder.com/150"
#     except Exception:
#         return "https://via.placeholder.com/150"

# async def fetch_articles(session, base_url, url):
#     async with session.get(url) as response:
#         if response.status == 200:
#             soup = BeautifulSoup(await response.text(), "html.parser")
#             articles = soup.find_all("article")

#             image_tasks = []
#             today = datetime.utcnow().date()

#             articles_data = []
#             for article in articles:
#                 headline_element = article.find("a", class_="JtKRv")
#                 headline = headline_element.text.strip() if headline_element else "N/A"
#                 link = base_url + headline_element["href"][1:] if headline_element else "N/A"

#                 source_element = article.find("div", class_="vr1PYe")
#                 source = source_element.text.strip() if source_element else "N/A"

#                 date_element = article.find("time")
#                 date = date_element["datetime"] if date_element else "N/A"
#                 article_date = datetime.fromisoformat(date).date() if date != "N/A" else None

#                 if article_date != today:
#                     continue

#                 description_element = article.find("div", class_="B6pJDd")
#                 description = description_element.text.strip() if description_element else "N/A"

#                 image_element = article.find("img", class_="Quavad")
#                 image_url = image_element["src"] if image_element else "https://via.placeholder.com/150"

#                 if image_url.startswith("/"):
#                     image_url = base_url + image_url

#                 image_tasks.append(get_final_image_url(session, image_url))

#                 articles_data.append({
#                     "headline": headline,
#                     "link": link,
#                     "source": source,
#                     "date": date,
#                     "description": description,
#                     "image_url": "",
#                     "query": ""
#                 })

#             final_image_urls = await asyncio.gather(*image_tasks)

#             for idx, article in enumerate(articles_data):
#                 article['image_url'] = final_image_urls[idx]

#                 existing_article = Article.query.filter_by(link=article['link']).first()
#                 if not existing_article:
#                     new_article = Article(
#                         headline=article['headline'],
#                         link=article['link'],
#                         source=article['source'],
#                         date=datetime.fromisoformat(article['date']),
#                         description=article['description'],
#                         image_url=article['image_url'],
#                         query=article['query']
#                     )
#                     db.session.add(new_article)

#             db.session.commit()
