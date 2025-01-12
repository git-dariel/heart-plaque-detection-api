from flask import Flask
from flask_cors import CORS
from app.routes.image_route import image_route
from app.routes.server_route import server_route
from app.config.config import Config
from app.config.cloudinary_config import configure_cloudinary

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(image_route)
    app.register_blueprint(server_route)

    # Configure Cloudinary
    configure_cloudinary()

    return app