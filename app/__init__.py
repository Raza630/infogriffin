from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions outside create_app()
db = SQLAlchemy()

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # App configuration
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:@localhost/news_articles',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Add other configs here
    )
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Import and register blueprints within app context
    with app.app_context():
        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        # Create tables if they don't exist
        db.create_all()
    
    return app





# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy


# db = SQLAlchemy()

# def create_app():
#     app = Flask(__name__)
    
#     # App configuration
    
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/news_articles'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#     # Initialize extensions
#     db.init_app(app)
    

#     # Import and register blueprints
#     from .routes import main as main_blueprint
#     app.register_blueprint(main_blueprint)
    

#     return app
