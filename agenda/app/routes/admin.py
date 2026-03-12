# agenda/app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..models import db, Recurso, Turma, Periodo, User
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Trava de segurança: Só entra se for Admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            flash("Você não tem permissão para acessar o painel.", "danger")
            return redirect(url_for("booking.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


# --- ROTA PRINCIPAL DO PAINEL ---
@admin_bp.route("/")
@login_required
@admin_required
def painel():
    # Conta quantos itens existem para mostrar num resumo
    total_professores = User.query.count()
    total_recursos = Recurso.query.count()
    total_turmas = Turma.query.count()
    return render_template(
        "admin/painel.html",
        profs=total_professores,
        recs=total_recursos,
        turmas=total_turmas,
    )


# --- 1. CADASTRAR SALAS E MÁQUINAS ---
@admin_bp.route("/recursos", methods=["GET", "POST"])
@login_required
@admin_required
def recursos():
    if request.method == "POST":
        novo = Recurso(nome=request.form.get("nome"), tipo=request.form.get("tipo"))
        db.session.add(novo)
        db.session.commit()
        flash(f"{novo.nome} cadastrado com sucesso!", "success")
        return redirect(url_for("admin.recursos"))
    return render_template("admin/recursos.html", recursos=Recurso.query.all())


# --- 2. CADASTRAR TURMAS ---
@admin_bp.route("/turmas", methods=["GET", "POST"])
@login_required
@admin_required
def turmas():
    if request.method == "POST":
        nova = Turma(nome=request.form.get("nome"), turno=request.form.get("turno"))
        db.session.add(nova)
        db.session.commit()
        flash(f"Turma {nova.nome} cadastrada!", "success")
        return redirect(url_for("admin.turmas"))
    return render_template("admin/turmas.html", turmas=Turma.query.all())


# --- 3. CADASTRAR AULAS (Ex: 1ª Aula, 2ª Aula) ---
@admin_bp.route("/aulas", methods=["GET", "POST"])
@login_required
@admin_required
def aulas():
    if request.method == "POST":
        nova = Periodo(nome=request.form.get("nome"), ordem=request.form.get("ordem"))
        db.session.add(nova)
        db.session.commit()
        flash("Horário de aula cadastrado!", "success")
        return redirect(url_for("admin.aulas"))
    return render_template(
        "admin/aulas.html", aulas=Periodo.query.order_by(Periodo.ordem).all()
    )


# --- 4. CADASTRAR PROFESSORES ---
@admin_bp.route("/professores", methods=["GET", "POST"])
@login_required
@admin_required
def professores():
    if request.method == "POST":
        nome = request.form.get("nome")
        senha = generate_password_hash(request.form.get("senha"))
        is_admin = True if request.form.get("is_admin") == "on" else False

        novo_prof = User(nome=nome, senha=senha, is_admin=is_admin)
        db.session.add(novo_prof)
        db.session.commit()
        flash(f"Professor {nome} cadastrado!", "success")
        return redirect(url_for("admin.professores"))
    return render_template("admin/professores.html", professores=User.query.all())


# --- CADASTRAR DISCIPLINAS ---
@admin_bp.route("/disciplinas", methods=["GET", "POST"])
@login_required
@admin_required
def disciplinas():
    # Não se esqueça de importar a classe Disciplina no topo do ficheiro admin.py!
    # from ..models import db, Recurso, Turma, Periodo, User, Disciplina

    if request.method == "POST":
        nova = Disciplina(nome=request.form.get("nome"))
        db.session.add(nova)
        db.session.commit()
        flash(f"Disciplina {nova.nome} registada!", "success")
        return redirect(url_for("admin.disciplinas"))
    return render_template("admin/disciplinas.html", disciplinas=Disciplina.query.all())
