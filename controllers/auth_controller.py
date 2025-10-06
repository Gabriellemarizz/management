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

        # CADASTRANDO USUÁRIO

        # Como eu não construi a classe Usuario com self, eu tenho que passar manualmente quais
        # Atributos eu quero inserir, não posso apenas jogar pela ordem.
        novo_usuário = Usuario(nome_usuario=username, email=email)
        # Usando set_password para gerar a senha em hash
        novo_usuário.set_password(senha)
        # Adicionando usuario no banco
        db.session.add(novo_usuário)
        # Finalizando a operação de inserção de novo usuário
        db.session.commit()
            

        # Logando novo usuário no sistema
        login_user(novo_usuário)

        # Redirecionando ele para o controlador de usuários
        return redirect(url_for('user.index'))

    # Aqui, se não for post e se houver erros ele renderiza o formulário com as mensagens de
    # erro que houveram durante o cadastramento
    return render_template('./auth/cadastramento.html', formulario_cad=formulario_cad)
        



# Rota para deslogar da aplicação 
@auth_bp.route('/logout')
@login_required
def deslogar_do_sistema():
    logout_user()
    # Asso aqui limpa dados de sessão que eu inseri manualmente em um usuário anterior e 
    # evita que eles fiquem armazenados e apareçam em um usuário aleatório 
    session.clear()
    return redirect(url_for('auth.logar_no_sistema'))



