from flask import Flask, request, session, redirect, url_for
from flask_login import LoginManager
from models.models import db
from models.models import Usuario
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.email_controller import email_bp, iniciar_scheduler
# Importando controlador para testar novas funções
from controllers.dashboard_controller import dashboard_bp

def create_app():

    app = Flask(__name__)
    
    # Confuguração
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_app.db'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    

    # Inicializando 
    db.init_app(app)

    # Limpando variavéis de autenticação de email armazenadas e update de senha em session
    # Porque? Alguém simplismente poderia acessar uma dessas rotas, e ao invés de completar a autenticação (o que acarretaria na 
    # eliminação das variaveis), ela poderia simplismente mudar de rota e ir fazer outra coisa qualquer, e o session iria ficar salvo

    # Minha solução foi: Se for para qualquer outra rota, apague
    @app.before_request
    def apagando_variaveis_de_emai_e_password_update():

        # Verificando a rota atual
        rota_atual = request.endpoint

        # VARIÁVEIS DE EMAIL
        
        # Rotas permitidas
        rotas_permitidas_email = [
            'auth.atualizar_email',
            'auth.checar_email',
            'auth.cadastrar_usuario'
        ]


        if 'codigo_verificador' in session and rota_atual not in rotas_permitidas_email:
                # Apagando variáveis
                session.pop('codigo_verificador', None)
                session.pop('origem', None)
                session.pop('dados_usuario', None)
                session.pop('novo_email', None)
                print('🗑️ VARIÁVEIS DE AUTENTICAÇÃO DE EMAIL APAGADAS AO ACESSAR ROTAS DIVERGENTES')

        # VARIÁVEL DE SENHA

        rotas_permitidas_senha = [
             'auth.atualizar_senha',
             'auth.confirmar_senha'
        ]

        if 'token_password_update' in session and rota_atual not in rotas_permitidas_senha:
             # Apagando variável
             session.pop('token_password_update', None)
             print('🗑️ VARIÁVEL DE ATUALIZAÇÃO DE SENHA APAGADA AO ACESSAR ROTAS DIVERGENTES')
    
    # Configurando Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Aqui é a rota que o usuário será redirecionando quando não estive logado no sistema
    login_manager.login_view = 'auth.logar_no_sistema'  
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'

    # Aqui adicionamos uma função index de redirecionamento de usuário para a página de login
    @app.route('/')
    def index():
         return redirect(url_for('auth.logar_no_sistema'))
    
    # Função para carregar usuário 
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    

    # Registrando blueprints 
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(email_bp)
    # Registrando blueprint de teste
    app.register_blueprint(dashboard_bp)

    # Inicializado a biblioteca de trabalho automático para enviar meus emails automaticamente as 17h50
    iniciar_scheduler(app)
    
    # Criando tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)  