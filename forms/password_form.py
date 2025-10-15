from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Regexp, ValidationError
from wtforms import PasswordField, SubmitField

class SenhaForm(FlaskForm):

    senha = PasswordField('senha', validators=[
        # Sem o DataRequired ele envia qualquer coisa e até mesmo campo nulo
        DataRequired(message='Senha é obrigatório'),
        Regexp(
            regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$',
            # Fazendo o usuário obrigatóriamente cadastrar uma senha segura
            message='A senha deve conter letras maiúscilas, minúsculas, numeros e simbolos'
        )
    ])

    senha_confirm = PasswordField('confirmar senha')

    submit = SubmitField('Confirmar senha')


    def validate_senha_confirm(self, senha_confirm):
        # Verificando se as senhas batem antes de enviar
        if senha_confirm.data != self.senha.data:
            raise ValidationError(message='As senhas tem que ser idênticas!')