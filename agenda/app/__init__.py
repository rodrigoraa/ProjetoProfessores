# agenda/app/__init__.py
import os
from flask import Flask
from .models import db, User
from flask_login import LoginManager
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    # 1. Use a mesma SECRET_KEY para o SSO funcionar
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave_mestra_eesjv")
    app.config["SESSION_COOKIE_DOMAIN"] = ".eesjv.com.br"
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)

    # 2. Caminho para o banco de dados que está na pasta 'baixar'
    # No servidor Linux, usamos o caminho absoluto
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "../../baixar/instance/usuarios.db"
    )
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.booking import booking_bp
    from .routes.admin import admin_bp
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)

    return app