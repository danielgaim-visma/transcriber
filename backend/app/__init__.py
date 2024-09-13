from flask import Flask
from flask_cors import CORS
from .routes.meetings import meetings
import logging

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Enable CORS
    CORS(app)

    # Load config
    app.config.from_object('config')

    # Register blueprints
    app.register_blueprint(meetings, url_prefix='/meetings')

    return app