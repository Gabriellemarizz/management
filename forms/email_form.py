from flask_wtf import FlaskForm
from wtforms.validators import Email, DataRequired, Length, ValidationError
from wtforms import EmailField, SubmitField
from models.models import Usuario

class EmailForm(FlaskForm):

    email = EmailField('Novo email', validators=[
            DataRequired(message='email é obrigatório'),
            Email(message='Por favor, ensira um email válido'),
            Length(max=100, message='O email deve ter ao máximo 100 caracteres')
        ])

    submit = SubmitField('Atualizar email')

    # Validando email
    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user: 
            raise ValidationError(message='O email já está em uso, escolha outro')