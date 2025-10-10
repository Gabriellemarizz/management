from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange
from wtforms import IntegerField, SubmitField


class CodeForm(FlaskForm):

    codigo = IntegerField(
        'codigo', validators=[
        DataRequired(message="O código é necessário para cadastramento. Verifique o seu email"),
        NumberRange(min=100000, max=999999)
        ]
        )
    
    submit = SubmitField('Verificar')