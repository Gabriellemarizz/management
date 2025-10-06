from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Length, Regexp


class Login_Form(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message='Username é obrigatório')      
    ])

    password = PasswordField('password', validators=[
        DataRequired(message='A senha é obrigatória')
    ])

    submit = SubmitField('Login')