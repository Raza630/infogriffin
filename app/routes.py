from flask import Blueprint, render_template, request
from .models import Article

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Predefined search queries
    queries = ["Central Railways", "Western Railways", "Mumbai Metro", "Indian Railways", "Mumbai Local", "Mumbai Bus", "Mumbai", "Kanpur Metro"]
    
    # Retrieve query parameters
    query_filter = request.args.get('query')  # Dropdown-based query
    custom_query = request.args.get('custom_query')  # Custom user-entered query

    # Start with all articles
    articles = Article.query

    # Filter articles based on dropdown selection
    if query_filter and query_filter.lower() != "all":
        articles = articles.filter(
            Article.headline.ilike(f"%{query_filter}%") | 
            Article.description.ilike(f"%{query_filter}%")
        )

    # Further filter if a custom query is provided
    if custom_query:
        articles = articles.filter(
            Article.headline.ilike(f"%{custom_query}%") | 
            Article.description.ilike(f"%{custom_query}%")
        )

    # Render the page with the filtered articles
    return render_template('indexse.html', articles=articles.all(), queries=queries)






# from flask import Blueprint, render_template, request
# from .models import Article

# main = Blueprint('main', __name__)

# @main.route('/')
# def index():
#     queries = ["Central Railways", "Western Railways", "Mumbai Metro", "Indian Railways", "Mumbai Local", "Mumbai Bus", "Mumbai", "Kanpur Metro"]
#     query_filter = request.args.get('query')
#     custom_query = request.args.get('custom_query')

#     articles = Article.query
#     if query_filter and query_filter.lower() == "all_":
#         articles = articles.filter(Article.headline.ilike(f"%{query_filter}%") | Article.description.ilike(f"%{query_filter}%"))
#     if custom_query:
#         articles = articles.filter(Article.headline.ilike(f"%{custom_query}%") | Article.description.ilike(f"%{custom_query}%"))

#     return render_template('indexse.html', articles=articles.all(), queries=queries)



