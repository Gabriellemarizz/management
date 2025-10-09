from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin
# Biblioteca para salvar senha em hash
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


tarefa_etiqueta = db.Table(
    'tarefa_etiqueta',
    db.Column('tarefa_id', db.Integer, db.ForeignKey('tarefa.id'), primary_key=True),
    db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiqueta.id'), primary_key=True)
)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=True)
    listas = db.relationship('Lista', backref='dono', lazy=True)
    tarefas = db.relationship('Tarefa', backref='usuario', lazy=True)
    comentarios = db.relationship('Comentario', backref='usuario', lazy=True)

    # Criando função para salvar a senha no sistema em forma de hash 
    def set_password(self, senha_hash):
        # As adições feitas nesse metodo comum é para deixar a senha extremamente mais forte 
        # e preparada contra ataques de força bruta. 
        self.senha_hash = generate_password_hash(senha_hash, method='scrypt', salt_length=64)

    # Criando função para comparar a senha do usuário com aquela que foi inserida na hora do login
    def check_password(self, senha):
        verificador = check_password_hash(self.senha_hash, senha)
        if verificador:
            return True
        else:
            return False
        
    


class Lista(db.Model):
    __tablename__ = 'lista'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tarefas = db.relationship('Tarefa', backref='lista', lazy=True)

class Etiqueta(db.Model):
    __tablename__ = 'etiqueta'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    tarefas = db.relationship('Tarefa', secondary=tarefa_etiqueta, back_populates='etiquetas')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_limite = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendente') # Pendente, Em Andamento, Concluída
    prioridade = db.Column(db.String(20), default='normal') # Baixa, Normal, Alta, Urgente
    ordem = db.Column(db.Integer, default=0) # Aqui é um campo do banco para poder posicionar tarefas de maneira manual de acordo com esse ínice, que ficará variando
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lista_id = db.Column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    etiquetas = db.relationship('Etiqueta', secondary=tarefa_etiqueta, back_populates='tarefas')
    comentarios = db.relationship('Comentario', backref='tarefa', lazy=True)

class Comentario(db.Model):
    __tablename__ = 'comentario'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)