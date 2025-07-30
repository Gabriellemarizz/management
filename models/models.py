from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

tarefa_etiqueta = db.Table(
    'tarefa_etiqueta',
    db.Column('tarefa_id', db.Integer, db.ForeignKey('tarefa.id'), primary_key=True),
    db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiqueta.id'), primary_key=True)
)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    listas = db.relationship('Lista', backref='dono', lazy=True)
    tarefas = db.relationship('Tarefa', backref='usuario', lazy=True)
    comentarios = db.relationship('Comentario', backref='usuario', lazy=True)

class Lista(db.Model):
    __tablename__ = 'lista'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tarefas = db.relationship('Tarefa', backref='lista', lazy=True)

class Etiqueta(db.Model):
    __tablename__ = 'etiqueta'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    tarefas = db.relationship('Tarefa', secondary=tarefa_etiqueta, back_populates='etiquetas')

class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_limite = db.Column(db.DateTime)
    concluida = db.Column(db.Boolean, default=False)
    prioridade = db.Column(db.String(20), default='Normal') # Baixa, Normal, Alta, Urgente
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