from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from flask_login import login_required, login_user, current_user, logout_user
# Importanto formulário seguro adaptado ao Flask para a realização da autenticação no sistema
from forms.auth_forms import Login_Form
# Importando banco de dados para realizar as operações de consulta no banco de dados 
from models.models import Usuario 

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
    if request.method == "POST":
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
                flash('username ou senha está errado')
                return redirect(url_for('auth.logar_no_sistema'))
            
        # Caso do username estar errado. O alert não revela o dado que está errado para evitar 
        # facilitar a vida do hacker
        else:
            flash('username ou senha está errado')
            return redirect(url_for('auth.logar_no_sistema'))
        
    else: 
        return render_template('./auth/login.html', formulario=formulario)
        

# Rota para deslogar da aplicação 
@auth_bp.route('/logout')
@login_required
def deslogar_do_sistema():
    logout_user()
    # Asso aqui limpa dados de sessão que eu inseri manualmente em um usuário anterior e 
    # evita que eles fiquem armazenados e apareçam em um usuário aleatório 
    session.clear()
    return redirect(url_for('auth.logar_no_sistema'))



