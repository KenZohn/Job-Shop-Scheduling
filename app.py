import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import random

# Funções para cada tela
def tela_metodos_basicos():
    st.header("Métodos Básicos")

    tipo_execucao = st.selectbox("Tipo de execução", ["Fixo", "Aleatório"])

    if tipo_execucao == "Aleatório":
        tamanho_problema = st.number_input("Tamanho do problema", min_value=1, step=1)
    else:
        tamanho_problema = None

    # Botão sempre visível
    mostrar_solucao = st.button("Solução Inicial")

    metodo = st.selectbox(
        "Método",
        ["Subida de encosta", "Subida de encosta com tentativas", "Têmpera simulada"]
    )

    if st.button("Executar"):
        if tipo_execucao == "Aleatório" and tamanho_problema is None:
            st.warning("Por favor, defina o tamanho do problema.")
        else:
            st.info("Módulo em desenvolvimento.")

    # Exibe matriz se tipo for fixo
    if tipo_execucao == "Fixo":
        dados = [
            [("M1", 3), ("M2", 2), ("M3", 2)],
            [("M2", 2), ("M3", 1), ("M1", 4)],
            [("M3", 4), ("M1", 3), ("M2", 2)]
        ]

        dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
        df = pd.DataFrame(dados_formatados, columns=["Op1", "Op2", "Op3"], index=["J1", "J2", "J3"])

        st.subheader("Matriz de Operações")
        st.dataframe(df)

        # Gera solução inicial apenas se botão for clicado
        if mostrar_solucao:
            disponibilidade_maquinas = {"M1": 0, "M2": 0, "M3": 0}
            cronograma = []

            for job_id, operacoes in enumerate(dados, start=1):
                tempo_atual = 0
                for op_index, (maquina, duracao) in enumerate(operacoes, start=1):
                    inicio = max(tempo_atual, disponibilidade_maquinas[maquina])
                    fim = inicio + duracao
                    disponibilidade_maquinas[maquina] = fim
                    tempo_atual = fim

                    cronograma.append({
                        "Job": f"J{job_id}",
                        "Operação": f"Op{op_index}",
                        "Máquina": maquina,
                        "Início": inicio,
                        "Fim": fim
                    })

            df_cronograma = pd.DataFrame(cronograma)
            st.subheader("Solução Inicial")
            st.dataframe(df_cronograma)

            makespan = avalia(cronograma)
            st.metric("Makespan", f"{makespan} unidades de tempo")

    elif tipo_execucao == "Aleatório":
        if mostrar_solucao:
            # Gerar problema aleatório
            dados = gerar_problema_aleatorio(num_jobs=tamanho_problema, num_maquinas=3)
            dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
            df = pd.DataFrame(dados_formatados, columns=[f"Op{i+1}" for i in range(3)], index=[f"J{i+1}" for i in range(tamanho_problema)])
            st.subheader("Problema Aleatório Gerado")
            st.dataframe(df)

            # Gerar solução inicial
            dados = gerar_problema_aleatorio(num_jobs=tamanho_problema, num_maquinas=3)
            cronograma = gerar_solucao_inicial(dados)
            df_cronograma = pd.DataFrame(cronograma)

            st.subheader("Solução Inicial Aleatória")
            st.dataframe(df_cronograma)

            makespan = avalia(cronograma)
            st.metric("Makespan", f"{makespan} unidades de tempo")



def tela_sobre():
    st.header("Sobre o Projeto")
    st.markdown("""
    ### Descrição do Problema
    Este projeto tem como objetivo aplicar algoritmos de Job Shop Scheduling.
                
    O Job Shop Scheduling (ou escalonamento de oficina) é uma técnica usada para organizar e otimizar a produção em ambientes industriais onde diferentes tarefas (jobs) precisam passar por várias máquinas, cada uma com uma sequência específica.
    
    - Minimiza o tempo total de produção (makespan): Busca reduzir o tempo necessário para completar todos os trabalhos.
    - Evita conflitos de recursos: Garante que duas tarefas não sejam atribuídas à mesma máquina ao mesmo tempo.

    ### Discentes
    - Johnny Keniti Mukai
    - Thais Ferreira Capucho
    """)

def tela_algoritmos_geneticos():
    st.header("Algoritmos Genéticos")
    st.info("Módulo em desenvolvimento.")

def gerar_problema_aleatorio(num_jobs, num_maquinas):
    """
    Gera um problema aleatório de Job Shop Scheduling.
    
    Parâmetros:
    - num_jobs: número de jobs
    - num_maquinas: número de máquinas (e operações por job)
    
    Retorno:
    - dados: lista de listas com tuplas (máquina, duração)
    """
    maquinas = [f"M{i+1}" for i in range(num_maquinas)]
    dados = []

    for _ in range(num_jobs):
        # Embaralha a ordem das máquinas para cada job
        ordem_maquinas = random.sample(maquinas, len(maquinas))
        operacoes = [(maquina, random.randint(1, 10)) for maquina in ordem_maquinas]
        dados.append(operacoes)

    return dados

def gerar_solucao_inicial(dados):
    """
    Gera a solução inicial para um problema de Job Shop Scheduling.
    
    Parâmetro:
    - dados: lista de listas com tuplas (máquina, duração) para cada job.
    
    Retorno:
    - cronograma: lista de dicionários com início e fim de cada operação.
    """
    disponibilidade_maquinas = {}
    cronograma = []

    # Inicializa disponibilidade das máquinas
    for job in dados:
        for maquina, _ in job:
            disponibilidade_maquinas[maquina] = 0

    # Processa cada job
    for job_id, operacoes in enumerate(dados, start=1):
        tempo_atual = 0
        for op_index, (maquina, duracao) in enumerate(operacoes, start=1):
            inicio = max(tempo_atual, disponibilidade_maquinas[maquina])
            fim = inicio + duracao
            disponibilidade_maquinas[maquina] = fim
            tempo_atual = fim

            cronograma.append({
                "Job": f"J{job_id}",
                "Operação": f"Op{op_index}",
                "Máquina": maquina,
                "Início": inicio,
                "Fim": fim
            })

    return cronograma

def avalia(cronograma):
    """
    Avalia o cronograma de um Job Shop Scheduling.
    Retorna o makespan (tempo total de conclusão).
    
    Parâmetro:
    - cronograma: lista de dicionários com chaves 'Início' e 'Fim' para cada operação.
    
    Retorno:
    - makespan: int
    """
    if not cronograma:
        return 0

    # Extrai o tempo de término de todas as operações
    tempos_finais = [op["Fim"] for op in cronograma]

    # O makespan é o maior tempo de término
    makespan = max(tempos_finais)
    return makespan

# Menu lateral com streamlit_option_menu
with st.sidebar:
    escolha = option_menu(
        menu_title="Menu",
        options=["Início", "Métodos Básicos", "Sobre", "Algoritmos Genéticos"],
        icons=["house", "calculator", "info-circle", "shuffle"],
        menu_icon="list",
        default_index=0,
        orientation="vertical",
        styles={
            "nav-link-selected": {
                "background-color": "#464646",
                "color": "white",
                "font-weight": "bold"
            }
        }
    )

# Navegação entre telas
if escolha == "Métodos Básicos":
    tela_metodos_basicos()
elif escolha == "Sobre":
    tela_sobre()
elif escolha == "Algoritmos Genéticos":
    tela_algoritmos_geneticos()
else:
    st.title("Job Shop Scheduling")
    st.write("Use o menu lateral para navegar entre as opções.")
