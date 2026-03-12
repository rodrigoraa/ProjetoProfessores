import os
from flask import Flask
from .models import db, User
from flask_login import LoginManager
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    # Use a mesma SECRET_KEY do projeto de downloads
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave-padrao-eesjv")
    app.config["SESSION_COOKIE_DOMAIN"] = ".eesjv.com.br"
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
    
    # No servidor, o banco de dados será o do projeto de downloads
    # Localmente (no VS Code), você pode usar um banco de teste
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///test.db")
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = "auth.login" # Redireciona para o portal principal
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.booking import booking_bp
    app.register_blueprint(booking_bp)

    return app