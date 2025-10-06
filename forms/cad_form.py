from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import Length, Regexp, DataRequired, Email, ValidationError
# Importando usuários para verificação da usabilidade do username e senha no banco.
# Só pode usar um nome que esteja disponível
from models.models import Usuario

class FormCad(FlaskForm):

    nome = StringField('username', validators=[
        DataRequired(message="username é obrigatório")
    ])

    email = EmailField('email', validators=[
        DataRequired(message='email é obrigatório'),
        Email(message='Por favor, ensira um email válido'),
        Length(max=100, message='O email deve ter ao máximo 100 caracteres')

    ])

    senha = PasswordField('password', validators=[
        # Sem o DataRequired ele envia qualquer coisa e até mesmo campo nulo
        DataRequired(message='email é obrigatório'),
        Regexp(
            regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$',
            # Fazendo o usuário obrigatóriamente cadastrar uma senha segura
            message='A senha deve conter letras maiúscilas, minúsculas, numeros e simbolos'
        )
    ])

    submit = SubmitField('Cadastrar-me')

    # Validando username e email, que são unicos no banco de dados, diretamente no formulário 
    # para evitar trabalho na rota de autenticação, recebendo os dados já automaticamente 
    # validados. Caso os dados estejam errados, eles vão para a rota mas não passam pelo 
    # validate_on_submit(), mas voltam para a página de cadastramento com as mensagens de 
    # erro. Além disso, o flask_wtf espera que para validar corretamente, a construção
    # do nome das funções deve haver exatamente os memos nomes dos campos do formulario

    # Exemplo: validare_{nome do campo exatamente como foi informado}(self, {nome do campo})

    # Validando username
    def validate_nome(self, nome):
        user = Usuario.query.filter_by(nome_usuario=nome.data).first()
        if user:
            raise ValidationError(message='O nome de usuário já está em uso, escolha outro')
    # Validando senha
    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user: 
            raise ValidationError(message='O email já está em uso, escolha outro')
