from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError


class ConfirmSenhaForm(FlaskForm):

    senha = PasswordField('senha', validators=[
        DataRequired(message='A senha é obrigatória')
    ])

    submit = SubmitField('Verificar')

    def validar_senha(self, senha):
        from models.models import Usuario
        # Carregando usuário atual
        usuario = Usuario.query.filter_by(id = current_user.id).first()
        
        # O objetivo aqui é apenas verificar se a senha não bate com a do atual usuario logado
        # Esse template não é renderizado sem @login_required
        if not usuario.check_password(senha):
            raise ValidationError(message='Senha inválida!')

