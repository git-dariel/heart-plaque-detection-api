from flask import Flask
from app.routes.image_route import image_route
from app.routes.server_route import server_route
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOADED_FOLDER"] = Config.UPLOAD_FOLDER

    # Register blueprints
    app.register_blueprint(image_route)
    app.register_blueprint(server_route)

    return app