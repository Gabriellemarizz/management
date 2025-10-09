from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField


class EtiquetaForm(FlaskForm):

    nome = StringField('nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(max=20, message='Nome não pode ter mais que 20 caracteres')
    ])

    submit = SubmitField('Criar etiqueta')