from . import db  # Import the `db` instance from app/__init__.py
from sqlalchemy import Column, Integer, String, Date  # Import necessary SQLAlchemy types

class Article(db.Model):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    headline = Column(String(255))
    link = Column(String(255))
    source = Column(String(255))
    date = Column(Date)
    description = Column(String(500))
    image_url = Column(String(255))
    search_query = Column(String(255))


# from . import db

# class Article(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     headline = db.Column(db.String(255))
#     link = db.Column(db.String(255))
#     source = db.Column(db.String(255))
#     date = db.Column(db.DateTime)
#     description = db.Column(db.Text)
#     image_url = db.Column(db.String(255))
#     query = db.Column(db.String(255))
