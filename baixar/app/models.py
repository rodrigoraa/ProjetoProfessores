from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(
        db.String(100), unique=True, nullable=False
    )  # Tornou-se unique=True
    senha = db.Column(db.String(255), nullable=False)

    def set_senha(self, senha_plana):
        """Transforma a senha comum em um Hash seguro."""
        self.senha = generate_password_hash(senha_plana)

    def verificar_senha(self, senha_plana):
        """Compara a senha digitada com o Hash do banco."""
        return check_password_hash(self.senha, senha_plana)
