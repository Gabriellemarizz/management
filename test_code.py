from models.models import db, Usuario
from app import create_app
import requests


# Inicializando a aplicação para poder realizar as operações de teste e criando a sua instância
# app = create_app()


# Testanto o código dentro do contexto da aplicação para poder realizar as aplicações de forma
# Integrada e não isolada(não é permitido)

"""
with app.app_context():
    # Inserindo um usuário no banco de dados 
    new_user = Usuario(nome_usuario='Keven', email="keven@keven.com")
    new_user.set_password('123')
    db.session.add(new_user)
    db.session.commit()
    print(f'User: {new_user.nome_usuario} inserido com sucesso!')
"""
# Função para testar conexão com internet
def verificar_conexao():
    # Se a conexão der certo, retorna true
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    # Se a conexão falhar, retorna false
    except requests.ConnectionError:
        return False

# Testando aplicação para enviar email

# Tudo dando certo: HEHEHEHEH
import yagmail
if not verificar_conexao():
    print('Sem internet')

else:
    yag = yagmail.SMTP('l.kevenmedeiros.c@gmail.com', 'ozgj viwb whju dmot')
    yag.send(
        to='keven.developerweb@gmail.com',
        subject="Testanto conexão com internet",
        contents="Você já tomou água hoje? Um fato curioso é ela faz muito bem para os rins. Sem ela, você pode acumular pedras enormeees, que somente se retiram através de cirurgia"
    )

    print('Verifique seu email BB')