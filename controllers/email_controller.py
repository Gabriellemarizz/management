from flask import Blueprint, render_template
from models.models import Usuario, Tarefa
from datetime import datetime, timedelta
# Essas duas funções servem para filtrar tarefas com mais de uma característica, e também mudar mudar o campo 
# de datetime (data e hora) para apenas data
from sqlalchemy import or_, cast, Date
# Importando biblioteca de enviar email
import yagmail
# A seguinte biblioteca automatiza essa nossa tarefinha de enviar emails pro povo, hehehehehe 
from apscheduler.schedulers.background import BackgroundScheduler
# A seguinte biblioteca é muito simples e será usada apenas para verificar a conexão com internet antes de usar a função send_email()
import requests



# Configurando meu blueprint
email_bp = Blueprint(
    'email', 
    __name__,
    url_prefix='/email'
    )

yag = yagmail.SMTP('l.kevenmedeiros.c', 'ozgj viwb whju dmot')


# Criando função de verificar conexão com a internet que será usada antes de enviar email
def verificar_conexao():
    # Se a conexão der certo, retorna true
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    # Se a conexão falhar, retorna false
    except requests.ConnectionError:
        return False

# Crianco função de enviar emails manualmente 
# Essa função está fora do contexto de aplicação devido não está com o @ do seu blueprint, então temos que chamar ela dentro 
# do seu devido contexto
def send_email(app):
    with app.app_context():
        # Testando conexão antes de ativar a busca e envio dos emails
        if not verificar_conexao():
            print('⚠️ Erro: Sem conexão com internet. \n--- Não foi possível notificar aos usuarios sobre os prazos de suas atividades ---')
            return # Aqui ele não retorna nada, somente dá prosseguimento. Então a função foi só basicamente printar isso na tela
        
        # Marcador do tempo atual
        hoje = datetime.today().date()
        # Marcador do dia anterior 
        amanha = datetime.today().date() + timedelta(days=1)
        # Importando tarefas presentes no banco que tenham data limite ou para hoje ou para amanhã

        tarefas = Tarefa.query.filter(
        # Aqui está dizendo para pegar tarefas que tenham a data maior o igual ao começo da data de hoje
        # e menor que a data de começo minimo do dia depois de amanhã. Ou seja, um intervalo de 48 horas
        (Tarefa.data_limite >= datetime.combine(hoje, datetime.min.time())) &
        (Tarefa.data_limite < datetime.combine(hoje + timedelta(days=2), datetime.min.time()))
        ).all()
        


        if tarefas:

            for tarefa in tarefas:
                
                # Pegando usuário
                usuario = Usuario.query.filter_by(id=tarefa.usuario_id).first()

                # Formatando mensagem para tarefa de hoje
                if tarefa.data_limite.date() == hoje:
                    # Mensagem
                    mensagem = f"O prazo da tarefa: {tarefa.titulo} é até hoje"

                # Formatando mensagem para tarefa de amanhã
                if tarefa.data_limite.date() == amanha:
                    # Mensagem
                    mensagem = f"O prazo da tarefa: {tarefa.titulo} é até amanhã"


                # Enviando email
                yag.send(
                    to=usuario.email,
                    subject='Lembrete <3',
                    contents=mensagem
                )

                return True
            
        else:
            return False


# Criando as minhas rotas do controlador de email

# Rota de envio manual
@email_bp.route('/')
def enviar_email_manualmente():
    # Reescrevendo a função para evitar erros de importação circular
    if not verificar_conexao():
        mensagem ='⚠️ Erro: Sem conexão com internet. \n--- Não foi possível notificar aos usuarios sobre os prazos de suas atividades'
        return render_template('./email/email_response.html', mensagem=mensagem) # Aqui ele retorna a mensagem apontando o erro de coneção
 
    # Caso haja conexão

    # Marcador do tempo atual
    hoje = datetime.today().date()
    # Marcador do dia anterior 
    amanha = datetime.today().date() + timedelta(days=1)
    # Importando tarefas presentes no banco que tenham data limite ou para hoje ou para amanhã

    tarefas = Tarefa.query.filter(
    # Aqui está dizendo para pegar tarefas que tenham a data maior o igual ao começo da data de hoje
    # e menor que a data de começo minimo do dia depois de amanhã. Ou seja, um intervalo de 48 horas
    (Tarefa.data_limite >= datetime.combine(hoje, datetime.min.time())) &
    (Tarefa.data_limite < datetime.combine(hoje + timedelta(days=2), datetime.min.time()))
    ).all()
        

    if tarefas:

        for tarefa in tarefas:
                
            # Pegando usuário
            usuario = Usuario.query.filter_by(id=tarefa.usuario_id).first()

            # Formatando mensagem para tarefa de hoje
            if tarefa.data_limite.date() == hoje:
                # Mensagem
                mensagem = f"O prazo da tarefa: {tarefa.titulo} é até hoje"

            # Formatando mensagem para tarefa de amanhã
            if tarefa.data_limite.date() == amanha:
                # Mensagem
                mensagem = f"O prazo da tarefa: {tarefa.titulo} é até amanhã"


            # Enviando email
            yag.send(
                to=usuario.email,
                subject='Lembrete <3',
                contents=mensagem
            )

            # Retornando mensagem informando o exito da operação
            mensagem = "Emails enviados com sucesso"
            
            
    else:
        # Informando mensagem informando a falha na operação
        mensagem = "Não há atividades com data para hoje ou amanhã"
        
        
    
    return render_template('./email/email_response.html', mensagem=mensagem)



# Iniciando meu agendador conectado no contexto da aplicação 
# Aqui passo a aplicação como parâmetro que será dada chamada la em app.py
def iniciar_scheduler(app):
    "Iniciando o meu agendador para enviar esses emails automáticamente 1 vez por dia e em determinando horário"
    schudeler = BackgroundScheduler()
    # Agora vamos configurar para rodar todos os dias em um determinado horário específico 
    # Aqui eu escolhi rodar essa função todos os dias as 17h50

    # Aqui chamei lambada primeiro para não acabar chamando a função no exato momento em que eu for apenas registrar a mesma 
    schudeler.add_job(func=lambda: send_email(app), trigger='cron', hour=22, minute=48)
    # Inicializando
    schudeler.start()

    print('Funcionando galeraaaaaa, ihuuuuuuu')


    




            
