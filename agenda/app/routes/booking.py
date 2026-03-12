from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Agendamento, Recurso
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/")
@login_required
def dashboard():
    recursos = Recurso.query.all()
    agendamentos = Agendamento.query.filter(Agendamento.data >= datetime.today().date()).all()
    return render_template("agenda.html", recursos=recursos, agendamentos=agendamentos)

@booking_bp.route("/agendar", methods=["POST"])
@login_required
def agendar():
    recurso_id = request.form.get("recurso")
    data_obj = datetime.strptime(request.form.get("data"), '%Y-%m-%d').date()
    aula = request.form.get("aula")
    turma = request.form.get("turma")

    # Verifica se já existe alguém nesse horário
    conflito = Agendamento.query.filter_by(recurso_id=recurso_id, data=data_obj, aula=aula).first()

    if conflito:
        flash(f"Erro: O recurso já está reservado por {conflito.professor.nome}!", "danger")
    else:
        novo = Agendamento(recurso_id=recurso_id, user_id=current_user.id, data=data_obj, aula=aula, turma=turma)
        db.session.add(novo)
        db.session.commit()
        flash("Reserva confirmada!", "success")

    return redirect(url_for("booking.dashboard"))