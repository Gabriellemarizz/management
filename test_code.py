from models.models import db, Usuario
from app import create_app


# Inicializando a aplicação para poder realizar as operações de teste e criando a sua instância
app = create_app()


# Testanto o código dentro do contexto da aplicação para poder realizar as aplicações de forma
# Integrada e não isolada(não é permitido)

with app.app_context():
    # Inserindo um usuário no banco de dados 
    new_user = Usuario(nome_usuario='Keven', email="keven@keven.com")
    new_user.set_password('123')
    db.session.add(new_user)
    db.session.commit()
    print(f'User: {new_user.nome_usuario} inserido com sucesso!')
