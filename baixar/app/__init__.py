import os
from flask import Flask
from dotenv import load_dotenv
from .models import db, User
from flask_login import LoginManager

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Configurações do Aplicativo
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Define o caminho do banco de dados dentro da pasta 'instance'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "..", "instance", "usuarios.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializa o Banco de Dados
    db.init_app(app)

    # Configura o Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # Redireciona para cá se não estiver logado
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Carrega o usuário do banco pelo ID
        return User.query.get(int(user_id))

    # Importação e Registro das Blueprints (MVC - Controllers)
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.downloader import dl_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dl_bp)

    # Cria o banco de dados e as tabelas caso não existam
    # Isso acontece dentro da pasta 'instance' na raiz do projeto
    if not os.path.exists(os.path.join(basedir, "..", "instance")):
        os.makedirs(os.path.join(basedir, "..", "instance"))

    with app.app_context():
        db.create_all()

    return app
