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
mensagem = """
    
<div style="background: #f9f1f7; padding: 30px; text-align: center; font-family: 'Arial', sans-serif;">
  <div style="max-width: 600px; background: white; margin: auto; border-radius: 15px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <div style="background: #ff6b9d; padding: 25px; border-radius: 12px 12px 0 0; color: white;">
      <h1 style="margin: 0; font-size: 36px;">Para Cla'🤍</h1>
      <p style="margin: 5px 0 0;">Uma mensagem do coração 💕</p>
    </div>

    <div style="padding: 30px; color: #444; text-align: left;">
      <p style="font-size: 18px; line-height: 1.6;">
        <b style="color: #c06c84;">Cla'🤍</b>, você não faz ideia do quão <b style="color: #c06c84;">feliz e grato</b> eu sou por ter uma pessoa tão maravilhosa quanto você em minha vida!
      </p>
      <p style="font-size: 18px; line-height: 1.6;">
        Espero crescer e ser um <b style="color: #c06c84;">marido maravilhoso</b>, que lhe ame, trate bem, cuide, seja responsável com você e com nossos talvez futuros filhos.
      </p>

      <div style="text-align: center; margin: 40px 0;">
        <div style="font-size: 64px;">❤️</div>
        <p style="font-size: 20px; font-style: italic; color: #d63031;">Você mora aqui</p>
      </div>

      <p style="text-align: center; font-style: italic; color: #999; font-size: 16px;">
        Com todo meu amor e carinho,<br>sempre seu 💕
      </p>
    </div>

    <div style="background: #ff6b9d; padding: 20px; color: white; border-radius: 0 0 12px 12px;">
      <p style="font-size: 22px; margin: 0;">Te amo infinitamente 💖</p>
    </div>
  </div>
</div>
"""




import yagmail
if not verificar_conexao():
    print('Sem internet')


else:
    yag = yagmail.SMTP('l.kevenmedeiros.c@gmail.com', 'ozgj viwb whju dmot')
    yag.send(
        to='clari.mesquitalves@gmail.com',
        subject="Para a amada e doce companheira do Sr. Medeiros",
        contents=mensagem
    )

    print('Verifique seu email BB')