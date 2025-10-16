from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user, login_required
# Importando banco de dados para a análise e processamento de dados
from models.models import Tarefa, Etiqueta, Lista, db
# Importando bibliotecas para criação de gráficos
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
# Importando recursos do datetime e sqlalchemy para medir os dias da semana e levantar gráficos
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date




# Configurando meu blueprint
dashboard_bp = Blueprint(
    'dashboard', 
    __name__,
    url_prefix='/dashboard'
    )



@dashboard_bp.route('/')
@login_required
def index():
    
    # Na página principal apresentaremos os dados gerais e principais sobre as atividades. Para isso utilizaremos de um total de 4 
    # gráficos que serão apresentados logo a seguir 

    # Carregando as tarefas do usuário
    all_tasks = Tarefa.query.filter_by(usuario_id=current_user.id).all()


    # TAXA DE CONCLUSÃO - BARRA DE PROGRESSO
    realised_tasks = [t for t in all_tasks if t.status == 'concluida']

    progresso = (len(realised_tasks)/len(all_tasks)) * 100 if all_tasks else 0
    progresso = round(progresso, 2)

    fig = go.Figure()

    # Parte concluída (verde)
    fig.add_trace(go.Bar(
        x=[progresso],
        y=["Progresso"],
        orientation='h',
        marker=dict(color='limegreen'),
        showlegend=False
    ))

    # Parte restante (cinza)
    fig.add_trace(go.Bar(
        x=[100 - progresso],
        y=["Progresso"],
        orientation='h',
        marker=dict(color='lightgray'),
        showlegend=False
    ))

    # Layout
    fig.update_layout(
        barmode='stack',
        xaxis=dict(range=[0, 100], showticklabels=False),
        yaxis=dict(showticklabels=False),
        height=150,
        margin=dict(l=20, r=20, t=40, b=20),
        title=f'Progresso: {progresso}%'
    )

    grafico_conclusao_html = fig.to_html(full_html=False, include_plotlyjs='cdn')




    # TAXA POR STATUS - GRÁFICO DE PIZZA
    pendentes = len([t for t in all_tasks if t.status == 'pendente']) 
    em_andamento = len([t for t in all_tasks if t.status == 'em andamento']) 
    concluidas = len([t for t in all_tasks if t.status == 'concluida']) 

    fig2 = go.Figure(data=[go.Pie(
    labels=['Pendente', 'Em Andamento', 'Concluída'],
    values=[pendentes if pendentes else 0, em_andamento if em_andamento else 0, concluidas if concluidas else 0],
    hole=0.4,  # Tamanho do buraco central
    marker=dict(colors=['#ff6b6b', '#ffd93d', '#6bcf7f']),
    textinfo='label+percent',
    textposition='outside'
    )])

    fig2.update_layout(
        title="Status das Tarefas",
        annotations=[dict(text=f'{len(all_tasks)}<br>Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    grafico_status_html = fig2.to_html(full_html=False, include_plotlyjs=False)



    # TAREFA CONCLUIDAS VS CRIADAS
    hoje = datetime.today()

    # Dias da semana 
    semana = []

    # Preenchendo os dias da semana atual
    for i in range(7):
        dia = hoje - timedelta(days=hoje.weekday()) + timedelta(days=i)
        semana.append(dia)

    # Pegando quantidade de tarefas por dia da semana
    tarefas_criadas_por_dia = []
    for dia in semana:
        tarefas_por_dia = Tarefa.query.filter(
            Tarefa.usuario_id == current_user.id,
            func.date(Tarefa.criada_em) == dia.date()
            ).all()
        tarefas_criadas_por_dia.append(len(tarefas_por_dia))

    # Pegando quantidade de tarefas concluidas naquele dia 
    tarefas_concluidas_por_dia = []
    for dia in semana:
        concluida_por_dia = Tarefa.query.filter(
            Tarefa.usuario_id == current_user.id,
            Tarefa.status == 'concluida',
            func.date(Tarefa.concluida_em) == dia.date()
        ).all()
        tarefas_concluidas_por_dia.append(len(concluida_por_dia))

    # Configurando os dias da semana para evitar repetição
    dias_da_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    

    fig3 = go.Figure(data=[
        go.Bar(name='Criadas', x=dias_da_semana, y=tarefas_criadas_por_dia),
        go.Bar(name='Concluídas', x=dias_da_semana, y=tarefas_concluidas_por_dia)
    ])

    fig3.update_layout(
        barmode='group',
        title="Tarefas Criadas vs Concluídas",
        xaxis_title="Dia da Semana",
        yaxis_title="Quantidade"
    )

    grafico_comparativas_html = fig3.to_html(full_html=False, include_plotlyjs=False)

    
    # Retornando na página 
    return render_template('user/dashboard/index.html', 
                           grafico_conclusao_html=grafico_conclusao_html, 
                           grafico_status_html=grafico_status_html,
                           grafico_comparativas_html=grafico_comparativas_html)


# ROTAS PARA MENUS 

# Análise temporal 
@dashboard_bp.route('/analisar_por_tempo')
@login_required
def analisar_por_tempo():

    # GRÁFICO DE LINHAS 

    # Calculando o inicio e o fim da semana atual 
    hoje = datetime.today().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    # Aqui, eu converto para datetime para fins de comparação
    inicio_datetime = datetime.combine(inicio_semana, datetime.min.time())
    fim_datetime = datetime.combine(fim_semana, datetime.max.time())

    # Buscando todas as tarefas concluidas durante a semana
    tarefas_semana = Tarefa.query.filter(
        Tarefa.usuario_id == current_user.id,
        Tarefa.status == 'concluida',
        Tarefa.concluida_em.isnot(None),
        Tarefa.concluida_em >= inicio_datetime,
        Tarefa.concluida_em <= fim_datetime
    ).all()
    
    # Aqui eu processo os dados coletados tendo de um dicionário 
    dados_dict = {}
    for tarefa in tarefas_semana:
        dia = tarefa.concluida_em.date()
        dados_dict[str(dia)] = dados_dict.get(str(dia), 0) + 1

    # Gerando lista com os dias da semana e quantidade de tarefas 
    dias_semana = []
    quantidades = []
    nomes_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    for i in range(7):
        data = inicio_semana + timedelta(days=i)
        dias_semana.append(nomes_dias[i])
        quantidades.append(dados_dict.get(str(data), 0))



    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=dias_semana,
        y=quantidades,
        mode='lines+markers',
        line=dict(color='green', width=3),
        marker=dict(size=8),
        name="Tarefas Concluídas"
    ))

    fig1.update_layout(
        title=f"Tarefas Concluídas - Semana Atual",
        xaxis_title="Dia da semana",
        yaxis_title="Quantidade",
        height=300,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    grafico_linha_html = fig1.to_html(full_html=False, include_plotlyjs='cdn')


    # HEATMAP

    tarefas_concluidas  = Tarefa.query.filter(
        Tarefa.usuario_id == current_user.id,
        Tarefa.status == 'concluida').all()
    
    if tarefas_concluidas:
        dias_portugues = {
            'Mon': 'Segunda',
            'Tue': 'Terça',
            'Wed': 'Quarta',
            'Thu': 'Quinta',
            'Fri': 'Sexta',
            'Sat': 'Sábado',
            'Sun': 'Domingo'
        }
        dados = [{
            'dia_semana': dias_portugues[t.concluida_em.strftime('%a')],
            'hora': t.concluida_em.hour
        } for t in tarefas_concluidas]

        df = pd.DataFrame(dados)

        heatmap_data = df.groupby(['dia_semana', 'hora']).size().unstack(fill_value=0)

        fig2 = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Greens'
        ))

        fig2.update_layout(
            title="Mapa de Atividade (Tarefas Concluídas)",
            xaxis_title="Hora do Dia",
            yaxis_title="Dia da Semana",
            height=300,
            margin=dict(l=40, r=40, t=50, b=40)
        )
    else:
        fig2 = go.Figure()
        fig2.update_layout(title="Sem dados suficientes para o Heatmap")

    grafico_heatmap_html = fig2.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('./user/dashboard/menus/tempo.html', 
                           grafico_linha_html=grafico_linha_html,
                           grafico_heatmap_html=grafico_heatmap_html)

