from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

class Recurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50)) # Sala, Equipamento, etc.

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recurso_id = db.Column(db.Integer, db.ForeignKey('recurso.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    aula = db.Column(db.Integer, nullable=False) # 1 a 6
    turma = db.Column(db.String(50), nullable=False)
    
    recurso = db.relationship('Recurso', backref='agendamentos')
    professor = db.relationship('User', backref='meus_agendamentos')