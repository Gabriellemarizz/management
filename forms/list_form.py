from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class ListForm(FlaskForm):

    nome = StringField('nome', validators=[
        DataRequired(message='O nome é obrigatório'),
        Length(max=30, message='O título deve ter no máximo 30 caracteres')
    ])
    
    submit = SubmitField('Criar lista')
