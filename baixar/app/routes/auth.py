import os  # Importação necessária para ler as variáveis do .env
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from ..models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Remove pontos e traços: transforma "123.456.789-00" em "12345678900"
        cpf_limpo = "".join(filter(str.isdigit, request.form.get("cpf")))
        senha = request.form.get("senha")

        user = User.query.filter_by(cpf=cpf_limpo).first()

        # Verifica o hash da senha de forma segura
        if user and user.verificar_senha(senha):
            login_user(user)
            return redirect(url_for("dl.ferramentas"))

        flash("CPF ou Senha incorretos.", "danger")
    return render_template("login.html")


@auth_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        cpf_limpo = "".join(filter(str.isdigit, request.form.get("cpf")))
        senha = request.form.get("senha")
        codigo_enviado = request.form.get("codigo_escola")

        # MELHORIA: Lê a senha da escola definida no arquivo .env
        # Se não encontrar no .env, usa o padrão 'EESJV2026' como segurança
        codigo_correto = os.getenv("CODIGO_ESCOLA", "EESJV2026")

        if codigo_enviado != codigo_correto:
            flash("Código de segurança da escola inválido!", "danger")
            return redirect(url_for("auth.registrar"))

        # Verifica duplicidade de CPF
        if User.query.filter_by(cpf=cpf_limpo).first():
            flash("Este CPF já está cadastrado.", "warning")
            return redirect(url_for("auth.registrar"))

        # Criação do usuário com Hash de senha
        novo_usuario = User(nome=nome, cpf=cpf_limpo)
        novo_usuario.set_senha(senha)  # Transforma texto puro em código seguro

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça seu login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("registrar.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
