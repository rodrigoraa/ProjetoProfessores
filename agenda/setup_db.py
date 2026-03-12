# agenda/setup_db.py
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("Limpando banco de dados antigo...")
    db.drop_all()
    
    print("Criando estrutura limpa...")
    db.create_all()
    
    print("Criando a sua conta de Administrador...")
    # Coloque o seu nome e a senha que você quer usar para logar
    senha_hash = generate_password_hash("fera@123") 
    admin = User(nome="eesaojose", senha=senha_hash, is_admin=True)
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Banco pronto! Você já pode logar como 'Diretoria' e senha '123456'.")