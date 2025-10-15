from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError


class ConfirmSenhaForm(FlaskForm):

    senha = PasswordField('senha', validators=[
        DataRequired(message='A senha é obrigatória')
    ])

    submit = SubmitField('Verificar')

    def validate_senha(self, senha):
        from flask_login import current_user
        
        # O objetivo aqui é apenas verificar se a senha não bate com a do atual usuario logado
        # Esse template não é renderizado sem @login_required
        # Aqui é mais seguro e nem precisa procurar o usuário no banco pelo ID já que está tudo salvo no current_user
        if not current_user.check_password(senha.data):
            raise ValidationError(message='Senha inválida!')

