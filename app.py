import os
from dotenv import load_dotenv
from flask import Flask, g
from pymongo import MongoClient

from routes import pages

load_dotenv()

def create_app():
    app = Flask(__name__)

    @app.before_request
    def before_request():
        """Open a new database connection before each request."""
        if 'db_client' not in g:
            g.db_client = MongoClient(os.environ.get("MONGODB_URI"))

    @app.teardown_appcontext
    def close_db(exception=None):
        """Close the database connection after the request."""
        db_client = g.pop('db_client', None)
        if db_client is not None:
            db_client.close()

    app.register_blueprint(pages)
    return app
