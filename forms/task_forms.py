from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class TaskForm(FlaskForm):

    titulo = StringField('titulo', validators=[
        DataRequired(message='Titulo é obrigatório'),
        Length(max=30, message='No máximo 30 caracteres')
    ])

    descricao = StringField('descricao', validators=[
        Length(max=200, message='A descrição é no máximo 200 caracteres')
    ])

    data_limite = DateField('data limite')

    prioridade = SelectField(
        'prioridade',  
        # Aqui temos as opções que irão aparecer dentro do select
        # Cada () contem ('value', 'text(valor que aparece visivelmente para o usuário)').
        # Como em qualquer select, a opção que ele selecionar, o value é o que irá para o banco de dados
        choices=[('baixa', 'Baixa'), ('normal', 'Normal'), ('alta', 'Alta'), ('urgente', 'Urgente')],
        validators=[DataRequired('Nível de prioridade é obrigatório')],
        # Aqui é o valor que ficará pré-selecionado e é o mesmo que o banco de dados irá 
        # preencher caso o campo prioridade venha nulo
        default='normal'
        )

    lista_id = SelectField(
        'lista', 
        coerce=int,
        validators=[DataRequired(message='Associação a alguma lista é obrigatória, se não tem lista, é preciso criar uma nova')]
        )

    submit = SubmitField('Criar atividade')

    # A seguinte função parece complexa, mas funciona da seguinte forma
    # Quando vamos carregar as listas que o usuário criou, não podemos carregar elas antes
    # Do usuário estar logado. Como saberemos quais são as listas dele? 

    # Essa função carrega apenas quando o usuário loga no sistema, e acessa essa requisição
    # para criar uma nova atividade. Desse modo, suas listas criadas são carregadas 
    # instântaneamente e estão prontas para ser usada no select.

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models.models import Lista
        listas = Lista.query.filter_by(usuario_id=user_id).all()
        # Agora teremos conteúdo para mostrar no selectField 
        self.lista_id.choices = [(lista.id, lista.nome) for lista in listas]