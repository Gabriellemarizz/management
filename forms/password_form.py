from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Regexp, ValidationError
from wtforms import PasswordField, SubmitField

class SenhaForm(FlaskForm):

    senha = PasswordField('senha', validators=[
        # Sem o DataRequired ele envia qualquer coisa e até mesmo campo nulo
        DataRequired(message='email é obrigatório'),
        Regexp(
            regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$',
            # Fazendo o usuário obrigatóriamente cadastrar uma senha segura
            message='A senha deve conter letras maiúscilas, minúsculas, numeros e simbolos'
        )
    ])

    senha_confirm = PasswordField('confirmar senha')

    submit = SubmitField('Confirmar senha')


    def confirmar_senha(self, senha, senha_confirm):
        if senha != senha_confirm:
            raise ValidationError(message='As senhas tem que ser idênticas!')