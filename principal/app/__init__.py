import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Simple portal: only the index page with links to other systems.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    from .routes.main import main_bp

    app.register_blueprint(main_bp)

    return app
