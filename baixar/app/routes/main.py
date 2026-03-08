from flask import Blueprint, render_template
from flask_login import current_user

# Criamos a Blueprint 'main'
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Esta é a página inicial (O Portal).
    Passamos o status de autenticação para o HTML para decidir
    se mostramos 'Entrar' ou 'Bem-vindo'.
    """
    return render_template("index.html", autenticado=current_user.is_authenticated)
