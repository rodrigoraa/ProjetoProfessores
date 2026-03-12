import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from ..models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome")
        senha = request.form.get("senha")

        # Busca o usuário pelo nome
        user = User.query.filter_by(nome=nome).first()

        # Verifica o hash da senha de forma segura
        if user and user.verificar_senha(senha):
            login_user(user)
            return redirect(url_for("dl.ferramentas"))

        flash("Nome ou Senha incorretos.", "danger")
    return render_template("login.html")


@auth_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        senha = request.form.get("senha")
        codigo_enviado = request.form.get("codigo_escola")

        codigo_correto = os.getenv("CODIGO_ESCOLA", "EESJV2026")

        if codigo_enviado != codigo_correto:
            flash("Código de segurança da escola inválido!", "danger")
            return redirect(url_for("auth.registrar"))

        # Verifica duplicidade de Nome
        if User.query.filter_by(nome=nome).first():
            flash(
                "Este nome já está cadastrado. Por favor, adicione um sobrenome para diferenciar.",
                "warning",
            )
            return redirect(url_for("auth.registrar"))

        # Criação do usuário com Hash de senha
        novo_usuario = User(nome=nome)
        novo_usuario.set_senha(senha)

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça o login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("registrar.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
