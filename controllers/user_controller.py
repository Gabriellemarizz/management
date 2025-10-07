from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user
# Importando classes e o banco de dados para operações CRUD
from models.models import Tarefa, Lista, db
# Importando formulários necessários 
from forms.list_form import ListForm
from forms.task_forms import TaskForm
# Importando método func para usar o método de transformar todas as letras em minúsculo
from sqlalchemy import func

user_bp = Blueprint(
    'user',
    __name__,
    url_prefix="/user"
)

@user_bp.route('/')
@login_required
def index():
    # Importando as listas do usuário
    listas = Lista.query.filter_by(usuario_id=current_user.id).all()
    # Importando tarefas 
    tarefas = Tarefa.query.filter_by(usuario_id=current_user.id).all()
    return render_template('./user/index.html', listas=listas, tarefas=tarefas)

# Rota de criação de listas 
@user_bp.route('/criar_lista', methods=['GET', 'POST'])
@login_required
def criar_lista():
    formulario = ListForm()

    if formulario.validate_on_submit():
        nome = formulario.nome.data
        # Verificando usabilidade no nome
        # Aqui faremos contando com os feitos do case sensitive, assim não importa se o 
        # nome da lista é Trabalho ou trabalho, ele considerará igual
        nova_lista = Lista.query.filter(
            func.lower(Lista.nome) == nome.lower(),
            Lista.usuario_id == current_user.id
        ).first()

        if nova_lista:
            flash('Essa lista já existe, use outro nome') 
            return render_template('./user/makers/list.html', formulario=formulario)
        else:
            # Caso a nova_lista não existe, vamos cria-la e jogar no banco
            nova_lista = Lista(nome=nome, usuario_id=current_user.id)
            db.session.add(nova_lista)
            db.session.commit()
            return redirect(url_for('user.index'))
    
    return render_template('./user/makers/list.html', formulario=formulario)


# Rota para edição de listas
# Aqui estou recebendo o id da lista via URL no link de editar
@user_bp.route('/editar_lista/<int:id>', methods=['POST', 'GET'])
@login_required
def editar_lista(id):
    lista = Lista.query.get_or_404(id)
    # Pré-carregando os dados da lista
    formulario = ListForm(obj=lista)
    if formulario.validate_on_submit():
        nome = formulario.nome.data
        # Atualizando nome da lista 
        lista.nome = nome
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('./user/makers/edit_list.html', id=id, formulario=formulario)

# Rota de excluir listas 
@user_bp.route('/excluir_lista/<int:id>', methods=['GET'])
@login_required
def excluir_lista(id):
    lista = Lista.query.get_or_404(id)
    # Excluindo lista 
    db.session.delete(lista)
    db.session.commit()
    # Retornando para a página de usuário
    return redirect(url_for('user.index'))

# Criar tarefa 
@user_bp.route('/criar_atividade', methods=['POST', 'GET'])
@login_required
def criar_atividade():
    # Aqui passamos o id do usuário para ele poder carregar as listas associadas a ele na hora da requisição
    formulario = TaskForm(user_id=current_user.id)
    if formulario.validate_on_submit():
        titulo = formulario.titulo.data
        descricao = formulario.descricao.data
        data_limite = formulario.data_limite.data
        prioridade = formulario.prioridade.data
        lista_id = formulario.lista_id.data

        # Registrando tarefa no banco de dados 
        nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, data_limite=data_limite, prioridade=prioridade, lista_id=lista_id, usuario_id=current_user.id)
        db.session.add(nova_tarefa)
        db.session.commit()
        return redirect(url_for('user.index'))
    
    return render_template('./user/makers/task.html', formulario=formulario)


# Editar tarefa 

@user_bp.route('/editar_tarefa/<int:id>', methods=['POST', 'GET'])
@login_required
def editar_tarefa(id):
    # Carregando a tarefa que será atualizada
    tarefa = Tarefa.query.get_or_404(id)
    formulario = TaskForm(user_id=current_user.id, obj=tarefa)
    if formulario.validate_on_submit():
        titulo = formulario.titulo.data
        descricao = formulario.descricao.data
        data_limite = formulario.data_limite.data
        prioridade = formulario.prioridade.data
        lista_id = formulario.lista_id.data

        # Atualizando a tarefa

        # Adicionando novos valores 
        tarefa.titulo = titulo
        tarefa.descricao = descricao
        tarefa.data_limite = data_limite
        tarefa.prioridade = prioridade
        tarefa.lista_id = lista_id

        # Confirmando alterações através do banco de dados
        db.session.commit()

        # Redirecionando o meliate para a sua respectiva rota 
        return redirect(url_for('user.index'))
    
    return render_template('./user/makers/edit_task.html', id=id, formulario=formulario)


# Excluir atividade

@user_bp.route('/excluir_tarefa/<int:id>', methods=['GET'])
@login_required
def excluir_tarefa(id):
    # Carregando tarefa que será excluida
    tarefa = Tarefa.query.get_or_404(id)
    # Excluindo tarefa do banco de dados 
    db.session.delete(tarefa)
    # Confirmando operação
    db.session.commit()

    # Redirecionanco para a página de usuário
    return redirect(url_for('user.index'))






