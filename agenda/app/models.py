# agenda/app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(
        db.Boolean, default=False
    )  # Define quem pode criar salas/turmas

    # Relacionamento para buscar todos os agendamentos de um professor
    agendamentos = db.relationship("Agendamento", backref="professor", lazy=True)


class Recurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)  # Ex: Sala de Vídeo, Projetor 01
    tipo = db.Column(
        db.String(50), nullable=False
    )  # Ex: Sala, Equipamento, Laboratório
    ativo = db.Column(
        db.Boolean, default=True
    )  # Permite desativar sem apagar o histórico

    agendamentos = db.relationship("Agendamento", backref="recurso", lazy=True)


class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(
        db.String(50), unique=True, nullable=False
    )  # Ex: 1º Ano A, 3º Ano B
    turno = db.Column(db.String(20))  # Ex: Manhã, Tarde, Noite


class Periodo(db.Model):
    # Representa as aulas do dia (1ª Aula, 2ª Aula, etc)
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)  # Ex: 1ª Aula (07:00 - 07:50)
    ordem = db.Column(
        db.Integer, nullable=False
    )  # Para ordenar cronologicamente (1 a 6)


# Adicione esta nova classe junto às outras
class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(
        db.String(100), unique=True, nullable=False
    )  # Ex: Matemática, Português


# Atualize a classe Agendamento existente para incluir a disciplina
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Chaves Estrangeiras (Atualizado)
    recurso_id = db.Column(db.Integer, db.ForeignKey("recurso.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey("turma.id"), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey("periodo.id"), nullable=False)
    disciplina_id = db.Column(
        db.Integer, db.ForeignKey("disciplina.id"), nullable=False
    )  # NOVA LINHA

    # Relacionamentos
    turma = db.relationship("Turma", backref="agendamentos")
    periodo = db.relationship("Periodo", backref="agendamentos")
    disciplina = db.relationship("Disciplina", backref="agendamentos")  # NOVA LINHA
