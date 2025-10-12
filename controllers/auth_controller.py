from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from flask_login import login_required, login_user, current_user, logout_user
# Importanto formulário seguro adaptado ao Flask para a realização da autenticação no sistema
from forms.auth_forms import Login_Form
# Importas formulário seguto flask_wtf para cadastro
from forms.cad_form import FormCad
# Importando banco de dados Usuario para realizar as operações de consulta no banco de dados 
from models.models import Usuario 
# Importando banco de dados DB para realizar operações Crud
from models.models import db
# Importando bibliotecas para enviar email de confirmação
import yagmail
from controllers.email_controller import verificar_conexao
from random import randint
from forms.cod_form import CodeForm
# Importando formulário para atualizações que o usuário queira realizar
from forms.password_form import SenhaForm
from forms.confirm_password_form import ConfirmSenhaForm
from forms.email_form import EmailForm

# Definindo o blueprint para login
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)



@auth_bp.route('/login', methods=['GET', 'POST'])
def logar_no_sistema():
    # Definindo formulário 
    formulario = Login_Form()

    # Aqui não preciso saber o tipo da requesição, uma vez que validate_on_submite é se
    # os dados estiverem corretos e for do tipo "POST".
    if formulario.validate_on_submit():
        username = formulario.username.data
        password = formulario.password.data

        # Verificando usuário e senha no banco de dados 

        usuario = Usuario.query.filter_by(nome_usuario = username).first()
        # Aqui é preciso que tenha usuário para usar a função de verificar senha. Ou seja
        # Não tem como simplificar as duas verificações em um só IF
        if usuario:
            verificador = usuario.check_password(password)

            if verificador and usuario:
                login_user(usuario)
                return redirect(url_for('user.index'))
            # Caso da senha estar errada. O alert não revela o dado que está errado para evitar 
            # facilitar a vida do hacker
            else:
                flash('username ou senha está incorreto')
                return redirect(url_for('auth.logar_no_sistema'))
            
        # Caso do username estar errado. O alert não revela o dado que está errado para evitar 
        # facilitar a vida do hacker
        else:
            flash('username ou senha está incorreto')
            return redirect(url_for('auth.logar_no_sistema'))
    
    # As mensagens de erro do formulario WTF não aparecerão no html uma vez que o flask_wtf 
    # só deixa enviar o formulário se os campus username e senha estiverem preenchidos. 
    # A mensagem só apareceria se fosse enivado valores nulos.
    # As mensagens flash estão aparecendo perfeitamente 

    # Se os dados estiverem errados ou a requisição for do tipo "GET"
    return render_template('./auth/login.html', formulario=formulario)
        

# Rota para cadastrar usuário 
@auth_bp.route('/cad_user', methods=['POST', 'GET'])
def cadastrar_usuario():
    formulario_cad = FormCad()
    # Aqui eu não preciso verificar se formulário é post ou get, uma vez que o validador de
    # formulário faz isso automáticamente. Caso contrario eu estária pegando os dados sem
    # eles passarem pela validação

    # verificando se os dados foram enviador corretamente conforme as regras de cadastro.
    # Se não, recarrega o formulário de cadastramento com as mensagens de erro.
    if formulario_cad.validate_on_submit():
        username = formulario_cad.nome.data
        email = formulario_cad.email.data
        senha = formulario_cad.senha.data

        # Colocando dados dentro de um session
        session['dados_usuario'] = [username, email, senha]
        # Criando código e colocando em uma session
        codigo = randint(100000,999999)
        session['codigo_verificador'] = codigo
        # Declarando origem
        session['origem'] = 'cadastrar_usuario'

        # Redirecionando dados para a rota de checar email

        return redirect(url_for('auth.checar_email'))

        

    # Aqui, se não for post e se houver erros ele renderiza o formulário com as mensagens de
    # erro que houveram durante o cadastramento
    return render_template('./auth/cadastramento.html', formulario_cad=formulario_cad)
        

# Rota para checar email
@auth_bp.route('/checar_email', methods=['POST', 'GET'])
def checar_email():

    # Instruções: Checar email pode vir de duas rotas distintas entre si.
    # 1º) É de cadastrar_usuario 
    # 2º) É de atualizar email
    # Um verificador de origem será enviado da rota atualizar_email, para que a rota apenas atualize e não cadastre um novo usuário
    # Carregando código verificador 
    codigo_verificador = session.get('codigo_verificador')
    # Carregando origem
    origem = session.get('origem', None)
    # Carregando dados do usuário 
    dados_usuarios = session.get('dados_usuario', None)
    # Carregando o formulário de código
    formulario = CodeForm()

    
    # FUNÇÕES DE RECEBER DADOS DO FORMULÁRIO
    if formulario.validate_on_submit():

        # Carregando código do formulário
        codigo_email = formulario.codigo.data

        # ROTA DE ATUALIZAR EMAIL

        if origem == 'atualizar_email' and current_user.is_authenticated:
            # Pegando email novo no session
            novo_email = session.get('novo_email')
            
            if codigo_email == codigo_verificador:
                    # Buscando usuário atual
                    novo_usuário = Usuario.query.filter_by(id=current_user.id).first()
                    # Mudando o email
                    novo_usuário.email = novo_email
                    # Confirmando alteração no banco de dados
                    db.session.commit()

                    # Excluindo código verificador, novo email e origem
                    session.pop('codigo_verificador')
                    session.pop('novo_email')
                    session.pop('origem')

                    # Redirecionando ele para o controlador de usuários
                    return redirect(url_for('user.index'))
                
            else:
                    flash('Código errado! Reenvie o código ou tente novamente com outro email')
                    return redirect(url_for('auth.checar_email'))


        # ROTA DE CADASTRAR USUÁRIO
        
        # Recebendo dados de formulário
        if origem == 'cadastrar_usuario':
            codigo_email = formulario.codigo.data
            if codigo_email == codigo_verificador:
                # Cadastrando usuario
                # Como eu não construi a classe Usuario com self, eu tenho que passar manualmente quais
                # Atributos eu quero inserir, não posso apenas jogar pela ordem.
                novo_usuário = Usuario(nome_usuario=dados_usuarios[0], email=dados_usuarios[1])
                # Usando set_password para gerar a senha em hash
                novo_usuário.set_password(dados_usuarios[2])
                # Adicionando usuario no banco
                db.session.add(novo_usuário)
                # Finalizando a operação de inserção de novo usuário
                db.session.commit()

                # Excluindo sessions
                session.pop('codigo_verificador')
                session.pop('dados_usuario')
                session.pop('origem')
                

                # Logando novo usuário no sistema
                login_user(novo_usuário)

                # Redirecionando ele para o controlador de usuários
                return redirect(url_for('user.index'))
            
            else:
                flash('Código errado! Reenvie o código ou tente novamente com outro email')
                return redirect(url_for('auth.checar_email'))
    
    # FUNÇÕES PARA PROCESSAR E ENVIAR EMAIL E FORMULÁRIO

    # Processando para qual email enviar

    if origem == 'atualizar_email':
        email = session.get('novo_email')
    else:
        email = dados_usuarios[1]


    # Processando mensagem
    mensagem = f'Código para confirmação: {codigo_verificador}'

    
    # Verificando se há internet para poder enviar

    if not verificar_conexao():
        if origem=='atualizar_email':
            return "Não é possível realizar a atualização de email por falta de conexão a internet"
        if origem=='cadastrar_usuario':
            return "Não é possível realizar cadastramento por falta de conexão a internet"

    else:
        yag = yagmail.SMTP('l.kevenmedeiros.c@gmail.com', 'ozgj viwb whju dmot')
        yag.send(
            to=email,
            subject="Confirme seu email",
            contents=mensagem
        )

    # Depois de enviar o email, renderizando o template html para preencher o código verificador 

    return render_template('./email/cod_email.html', formulario=formulario, origem=origem)
        

# Rota para confirmar senha - antes da atualização

# Rota para confirmar novo email - depois de selecionar o novo email


# Rota para atualizar dados de usuário 
@auth_bp.route('/atualizar_email', methods=['GET', 'POST'])
@login_required
def atualizar_email():

    formulario = EmailForm()

    # Se o formulario for eviado 
    if formulario.validate_on_submit():
        email = formulario.email.data

        
        # Colocando o novo email em session para enviar para a checagem
        session['novo_email'] = email

        # Gerando um código verificador 
        codigo = randint(100000,999999)
        session['codigo_verificador'] = codigo

        # Redirecionando para a rota de checar email declarando a origem
        session['origem'] = "atualizar_email"


        return redirect(url_for('auth.checar_email'))

    

    return render_template('./email/email_update.html', formulario=formulario)

@auth_bp.route('/atualizar_senha')
@login_required
def atualizar_senha():

    return "password update"
            





# Rota para deslogar da aplicação 
@auth_bp.route('/logout')
@login_required
def deslogar_do_sistema():
    logout_user()
    # Asso aqui limpa dados de sessão que eu inseri manualmente em um usuário anterior e 
    # evita que eles fiquem armazenados e apareçam em um usuário aleatório 
    session.clear()
    return redirect(url_for('auth.logar_no_sistema'))



