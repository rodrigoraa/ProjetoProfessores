# agenda/app/routes/booking.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Agendamento, Recurso, Turma, Periodo
from datetime import datetime, date

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/")
@login_required
def dashboard():
    # Carrega dados para os selects do formulário HTML
    recursos = Recurso.query.filter_by(ativo=True).order_by(Recurso.nome).all()
    turmas = Turma.query.order_by(Turma.nome).all()
    periodos = Periodo.query.order_by(Periodo.ordem).all()

    # Busca apenas agendamentos de hoje para frente
    hoje = date.today()
    agendamentos = (
        Agendamento.query.filter(Agendamento.data >= hoje)
        .order_by(Agendamento.data)
        .all()
    )

    return render_template(
        "agenda.html",
        recursos=recursos,
        turmas=turmas,
        periodos=periodos,
        agendamentos=agendamentos,
    )


@booking_bp.route("/agendar", methods=["POST"])
@login_required
def agendar():
    recurso_id = request.form.get("recurso")
    turma_id = request.form.get("turma")
    periodo_id = request.form.get("periodo")

    try:
        data_obj = datetime.strptime(request.form.get("data"), "%Y-%m-%d").date()
    except ValueError:
        flash("Data inválida.", "danger")
        return redirect(url_for("booking.dashboard"))

    # Validação 1: Não permitir agendamento no passado
    if data_obj < date.today():
        flash("Não é possível agendar em datas passadas.", "warning")
        return redirect(url_for("booking.dashboard"))

    # Validação 2: Prevenir conflitos (Double Booking)
    conflito = Agendamento.query.filter_by(
        recurso_id=recurso_id, data=data_obj, periodo_id=periodo_id
    ).first()

    if conflito:
        flash(
            f"Conflito! O recurso já está reservado por {conflito.professor.nome} nesta aula.",
            "danger",
        )
    else:
        novo = Agendamento(
            recurso_id=recurso_id,
            user_id=current_user.id,
            turma_id=turma_id,
            periodo_id=periodo_id,
            data=data_obj,
        )
        db.session.add(novo)
        db.session.commit()
        flash("Reserva confirmada com sucesso!", "success")

    return redirect(url_for("booking.dashboard"))


@booking_bp.route("/cancelar/<int:id>", methods=["POST"])
@login_required
def cancelar(id):
    agendamento = Agendamento.query.get_or_404(id)

    # Apenas o dono da reserva ou um admin podem cancelar
    if agendamento.user_id != current_user.id and not current_user.is_admin:
        flash("Você não tem permissão para cancelar esta reserva.", "danger")
        return redirect(url_for("booking.dashboard"))

    db.session.delete(agendamento)
    db.session.commit()
    flash("Reserva cancelada.", "info")
    return redirect(url_for("booking.dashboard"))
