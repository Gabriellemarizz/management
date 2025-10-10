from flask import Blueprint, session, redirect, url_for, render_template, request, flash, make_response
from flask_login import login_required, current_user
# A biblioteca seguinte será usada para declarar o grau de importância das strings presentes em prioridades
from sqlalchemy import case
# Importando classes e o banco de dados para operações CRUD
from models.models import Tarefa, Lista, db, Etiqueta
# Importando formulários necessários 
from forms.list_form import ListForm
from forms.task_forms import TaskForm
from forms.eti_form import EtiquetaForm
# Importando método func para usar o método de transformar todas as letras em minúsculo
from sqlalchemy import func
# Biblioteca que será utilizada no processo de medição de prazos
from datetime import datetime

user_bp = Blueprint(
    'user',
    __name__,
    url_prefix="/user"
)


# Rota principal de usuário

@user_bp.route('/')
@login_required
def index():
    # Importando as listas do usuário
    listas = Lista.query.filter_by(usuario_id=current_user.id).all()
    # Importando tarefas 
    tarefas = Tarefa.query.filter_by(usuario_id=current_user.id).all()
    # Importando etiquetas 
    etiquetas = Etiqueta.query.all()
    # Variável para medição de tempo
    hoje = datetime.today()



    # Verificando a existência e tipo de cookie. Caso não exista, ele é carregado com a categoria "recentes"
    ordem = request.cookies.get('ordem', 'recentes')

    # Ordenando conforme a preferência de usuário
    # Ordenando por tempo de criação

    # Recentes: Vai da mais recente até a mais antiga
    if ordem == 'recentes':
        tarefas = Tarefa.query.order_by(Tarefa.criada_em.desc()).all()
        pass
        
    # Antigas: Vai da mais antiga até a mais recente
    elif ordem=='antigas':
        tarefas = Tarefa.query.order_by(Tarefa.criada_em.asc()).all()
        pass


    # Ordenando por prazos 
        
    # Prazo curto: Dos mais curtos até os mais longos 
    elif ordem=='prazo_curto':
        tarefas = Tarefa.query.order_by(Tarefa.data_limite.asc()).all()
        pass

    # Prazo longo: Dos prazos maiores até os mais curtos 
    elif ordem == 'prazo_longo':
        tarefas = Tarefa.query.order_by(Tarefa.data_limite.desc()).all()
        pass


    # Ordenamento por prioridades   

    elif ordem == 'prioridade':
        # Como não existe uma função sqlalchemy que faça isso automaticamente, que nem o ordenador de numeros, eu preciso criar a minha própria função
        # 1) Eu declaro ao sqlalchemy um indice que tem a função de elencar posições de importância 

                                                # 1º Urgente
                                                # 2º Alta
                                                # 3º Normal
                                                # 4º Baixa
        priorizador = case ({
        'urgente': 1,
        'alta': 2,
        'normal': 3,
        'baixa': 4
        },
        value=Tarefa.prioridade
        )

        # Ordenando das mais importantes até as menos importantes
        tarefas = Tarefa.query.order_by(priorizador.asc()).all()
        pass

    # Ordenando no modo manual 
    elif ordem=='manual':
        tarefas = Tarefa.query.order_by(Tarefa.ordem.asc()).all()
        pass

    # Salvando a variável temporária 'tempo_restante' em cada objeto presente na lista de tarefas
    for t in tarefas:
        t.tempo_restante = (t.data_limite - hoje).days + 1 



    # Filtrando resultados 

    # Verificando se a lista está no modo de filtro
    modo_filtro = session.get('filtro')

    if modo_filtro:
        # Desligando indicador de filtro após acessar a rota, para não ficar recarregando toda vida
        

        filtros = session.get('filtros', [])

        for filtro_item in filtros:
            # Pegando os tipos de filtro presentes
            filtro_lista = filtro_item.get('lista')
            filtro_status = filtro_item.get('status')
            filtro_etiquetas = filtro_item.get('etiquetas')
            filtro_palavras_chave = filtro_item.get('palavras_chave')
            
            # Checkando sua existencia e aplicando na lista de tarefas geral
            if filtro_lista:
                tarefas = [t for t in tarefas if t.lista_id == int(filtro_lista)]

            if filtro_status:
                tarefas = [t for t in tarefas if t.status == filtro_status]

            if filtro_etiquetas:
                filtro_etiquetas_ids = [int(e) for e in filtro_etiquetas]

                tarefas = [
                    t for t in tarefas if all(e_id in [etq.id for etq in t.etiquetas] for e_id in filtro_etiquetas_ids)
                ]

            if filtro_palavras_chave:
                return f"Está filtrando meu quirido{filtro_palavras_chave}"
    
    # Sitema de filtro por palavra chave

    # Verificando se sistema de busca por palavra chave está ativo
    modo_filtro_palavras_chave = session.get('filtro_palavra_chave_modo')

    if modo_filtro_palavras_chave:
        palavras_chave = session.get('filtro_palavra_chave', [])

        if palavras_chave:
            tarefas = [
                    t for t in tarefas if palavras_chave.lower() in t.titulo.lower() or palavras_chave.lower() in t.descricao.lower()
                ]


    
    return render_template('./user/index.html', ordem=ordem, listas=listas, tarefas=tarefas, etiquetas=etiquetas)




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
        status = formulario.status.data
        lista_id = formulario.lista_id.data
        etiquetas = formulario.etiquetas.data


        # Registrando tarefa no banco de dados 
        nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, data_limite=data_limite, prioridade=prioridade, status=status, lista_id=lista_id, usuario_id=current_user.id)
         # Dando um valor automático para o campo de ordem
        ultima_tarefa = Tarefa.query.filter_by(usuario_id = current_user.id).order_by(Tarefa.ordem.desc()).first()
        # Aqui ele procura a ultima tarefa cadastrada. Se houver, o indice dessa nova tarefa será o da antiga +1. Caso não haja, o indice será 0
        # No banco existem várias tarefas de diferentes usuários. O diferencial daqui é que ele procura por tarefas existente do USUÁRIO LOGADO nessa sessão
        # Se não houver, ele sempre criará uma que tem indice inicial 0. Permitindo lá na frente ele manusear a ordem de suas próprias tarefas
        nova_tarefa.ordem = (ultima_tarefa.ordem +1) if ultima_tarefa else 0

        # Relacionando as etiquetas com a tarefa criada 
        if etiquetas:
            for etiqueta_id in etiquetas:
                etiqueta = Etiqueta.query.filter_by(id=int(etiqueta_id)).first()
                nova_tarefa.etiquetas.append(etiqueta)
            
            pass

        # Adicionando nova tarefa ao banco ;)
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

    # Preenchendo os checkbox com as opções do usuário
    # Aqui é importante submeter a condicional GET, porque se não, quando for salvar, as informações presentes aqui irão sobscrever as 
    # Informações vindas através do POST
    if request.method == 'GET':
        formulario.etiquetas.data = [e.id for e in tarefa.etiquetas]

    if formulario.validate_on_submit():
        titulo = formulario.titulo.data
        descricao = formulario.descricao.data
        data_limite = formulario.data_limite.data
        prioridade = formulario.prioridade.data
        status = formulario.status.data
        lista_id = formulario.lista_id.data

        # Atualizando a tarefa

        # Adicionando novos valores 
        tarefa.titulo = titulo
        tarefa.descricao = descricao
        tarefa.data_limite = data_limite
        tarefa.prioridade = prioridade
        tarefa.status = status
        tarefa.lista_id = lista_id

        # Atualizando as etiquetas 
        # Aqui substituimos a lista antiga de etiquetas por uma nova lista
        nova_lista_etiquetas = Etiqueta.query.filter(Etiqueta.id.in_(formulario.etiquetas.data)).all()
        tarefa.etiquetas = nova_lista_etiquetas


        # Confirmando alterações através do banco de dados
        db.session.commit()

        # Redirecionando o meliate para a sua respectiva rota 
        return redirect(url_for('user.index'))
    
    return render_template('./user/makers/edit_task.html', id=id, formulario=formulario)



# Excluir tarefa

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


# Concluir tarefa
# Aqui é bem simples, somente atualizar os status de atividade 

@user_bp.route('/concluir_tareda/<int:id>', methods=['GET'])
@login_required
def concluir_tarefa(id):

    # carregando tarefa 
    tarefa = Tarefa.query.get_or_404(id)

    # Verificando se já está conlcuida 
    # Se estiver, ela volta a ser pendente
    if tarefa.status == 'concluida':
        tarefa.status = 'pendente'
        # Salvando alteração no banco 
        db.session.commit()
        # Rediracionando para rota principal de user
        return redirect(url_for('user.index'))
    
    else:

        # Atualizando status 
        tarefa.status = 'concluida'

        # Salvando alterações no banco 
        db.session.commit()

        # Redirecionando para a rota principal de user
        return redirect(url_for('user.index'))


# Colocar tarefa em andamento 
@user_bp.route('/iniciar_tarefa/<int:id>', methods=['GET'])
@login_required
def iniciar_tarefa(id):

    # Carregando tarefa 
    tarefa = Tarefa.query.get_or_404(id)

    # Atualizando status
    tarefa.status = "em andamento"

    # Salvando alterações no banco 
    db.session.commit()

    # Redirecionando para a rota principal
    return redirect(url_for('user.index'))



# Ordenamento de tarefa 
@user_bp.route('/ordenar_tarefa', methods=['POST'])
@login_required
def ordenar_tarefa():

    ordem = request.form.get('ordem')

    # Criando (ou atualizando se não houver) o cookie de ordenamento 

    resposta = make_response(redirect(url_for('user.index')))
    resposta.set_cookie('ordem', f'{ordem}')

    # Retorna o cookie para o navegador, e a resposta dele já é dada automáticamente: redirecionar para a rota principal de usuário
    return resposta



# Ordenamento manual de tarefa
@user_bp.route('ordenar_manualmente', methods=['POST'])
@login_required
def ordenar_manualmente():
    dados = request.get_json()
    # Aqui eles vem em forma de dicionário lá do front-end 
    # Eu pego cada item do dicionário e ele terá um id e um numero de ordem
    # Agora é só pegar e atualizar cada tarefa pertencente a esse usuário no banco de dados 
    for item in dados['ordem']:
        tarefa = Tarefa.query.get_or_404(item['id'])
        if tarefa and tarefa.usuario_id == current_user.id:
            tarefa.ordem = item['ordem']

    # Salvando alterações 
    db.session.commit()

    return redirect(url_for('user.index'))




# MECANISMOS DE FILTRAGEM

# Adicionar filtro
@user_bp.route('/filtrar_tarefas', methods=['POST'])
@login_required
def filtrar_tarefas():
    status = request.form.get('status')
    lista = request.form.get('lista')
    etiquetas = request.form.getlist('etiqueta_filtro')

    if not status and not lista and not etiquetas:
        # Se ele não marcar nada e quiser filtrar, ele é redirecionado para a rota principal de usuários sem ativar o filtro 
        return redirect(url_for('user.index'))

    # Preenchendo a lista de filtro com as opções enviadas pelo usuário
    session['filtros'] = [{'status':status, 'lista':lista, 'etiquetas': etiquetas}]

    # Ativando o modo de filtração
    session['filtro'] = True

    # Redirecionando para a rota principal de usuários 
    return redirect(url_for('user.index'))

# Limpar filtro 
@user_bp.route('/limpar_filtro', methods=['GET'])
@login_required
def limpar_filtro():
    # Desligando modo de filtração 
    session['filtro'] = False

    # Limpando filtros 
    session.pop('filtros', None)

    # Retornando rota para rota principal de usuário 
    return redirect(url_for('user.index'))


# Pesquisando por palavras-chave
@user_bp.route('/filtrar_tarefas_by_palavras_chave', methods=['POST'])
@login_required
def filtrar_tarefas_by_palavras_chave():

    palavras_chave = request.form.get('barra_pesquisa')

    if not palavras_chave.replace(" ", ""):
        # Como ele não digitou nada, ou só enviou espaço, ele volta para a página sem ativar o filtro
        return redirect(url_for('user.index'))

    session['filtro_palavra_chave'] = palavras_chave

    session['filtro_palavra_chave_modo'] = True

    # Redirecionando para a rota principal de usuário
    return redirect(url_for('user.index'))

# Apagando palavras chave
@user_bp.route('/apagar_filtro_de_palavras_chave', methods = ['GET'])
@login_required
def apagar_filtro_de_palavras_chave():

    # Desligando o filtro
    session['filtro_palavra_chave_modo'] = False

    # Apagando as palavras chave
    session.pop('filtro_palavra_chave', None)

    # Retornando para a rota principal de usuários 
    return redirect(url_for('user.index'))



# MECANISMOS DE ETIQUETA 

# Criar etiqueta
@user_bp.route('/criar_etiqueta', methods=['POST', 'GET'])
@login_required
def criar_etiqueta():
    formulario = EtiquetaForm()

    if formulario.validate_on_submit():
        nome = formulario.nome.data

        # Criando nova etiqueta 
        nova_etiqueta = Etiqueta(nome=nome, usuario_id=current_user.id)
        # Adicionando no banco 
        db.session.add(nova_etiqueta)
        # Salvando no banco 
        db.session.commit()

        # Redirecionando para a rota principal de usuário
        return redirect(url_for('user.index'))
    
    return render_template('./user/makers/etiqueta.html', formulario=formulario)


# Atualizar etiqueta 
@user_bp.route('/atualizar_etiqueta/<int:id>', methods=['POST', 'GET'])
@login_required
def atualizar_etiqueta(id):
    # Procurando etiqueta a ser atualizada
    etiqueta = Etiqueta.query.get_or_404(id)
    # Carregando formulário já preenchido com os dados atuais 
    formulario = EtiquetaForm(obj=etiqueta)

    if formulario.validate_on_submit():
        nome = formulario.nome.data

        # Se ele existir 
        if etiqueta:
            etiqueta.nome = nome

            # Salvando alteração no banco de dados 
            db.session.commit()
        
            # Redirecionando para a rota principal de usuário
            return redirect(url_for('user.index'))
        
    return render_template('./user/makers/edit_etiqueta.html', id=id, formulario=formulario)


# Excluir etiqueta 
@user_bp.route('/excluir_etiqueta/<int:id>', methods=['GET'])
@login_required
def excluir_etiqueta(id):
    # Procurando etiqueta 
    etiqueta = Etiqueta.query.get_or_404(id)

    # Verificando se existe
    if etiqueta:
        # Deletando 
        db.session.delete(etiqueta)
        # Salvando alteração
        db.session.commit()

        # Redirecionando para a rota principal de usuários 
        return redirect(url_for('user.index'))
    
    # Caso não tenha achado etiqueta, redireciona para a rota principal mesmo assim
    return redirect(url_for('user.index'))







