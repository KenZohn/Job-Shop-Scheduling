import streamlit as st
import pandas as pd
import random
import copy

from streamlit_option_menu import option_menu

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
            if metodo == "Subida de encosta":
                # Gerar problema
                dados = st.session_state.dados_problema
                dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
                df = pd.DataFrame(dados_formatados, columns=[f"Op{i+1}" for i in range(3)], index=[f"J{i+1}" for i in range(tamanho_problema)])
                st.subheader("Problema")
                st.dataframe(df)

                # Executar subida de encosta
                cronograma_otimizado, melhor_makespan = subida_de_encosta(dados)

                # Exibir resultado
                df_otimizado = pd.DataFrame(cronograma_otimizado)
                st.subheader("Solução Otimizada (Subida de Encosta)")
                st.dataframe(df_otimizado)
                st.metric("Makespan Otimizado", f"{melhor_makespan} unidades de tempo")
            else:
                st.info("Módulo em desenvolvimento.")

    if tipo_execucao == "Fixo":
        # Problema fixo
        dados = [
            [("M1", 3), ("M2", 2), ("M3", 2)],
            [("M2", 2), ("M3", 1), ("M1", 4)],
            [("M3", 4), ("M1", 3), ("M2", 2)]
        ]

        dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
        df = pd.DataFrame(dados_formatados, columns=["Op1", "Op2", "Op3"], index=["J1", "J2", "J3"])

        st.subheader("Problema")
        st.dataframe(df)

        # Gera solução inicial fixa
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

            # Avaliar solução
            makespan = avalia(cronograma)
            st.subheader("Avalia")
            st.metric("Makespan", f"{makespan} unidades de tempo")

    elif tipo_execucao == "Aleatório":
        if "dados_problema" not in st.session_state:
                st.session_state.dados_problema = None

        if mostrar_solucao:
            # Gerar problema aleatório
            dados = gerar_problema_aleatorio(num_jobs=tamanho_problema, num_maquinas=3)
            st.session_state.dados_problema = dados
            dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
            df = pd.DataFrame(dados_formatados, columns=[f"Op{i+1}" for i in range(3)], index=[f"J{i+1}" for i in range(tamanho_problema)])
            st.subheader("Problema")
            st.dataframe(df)

            # Gerar solução inicial
            dados = gerar_problema_aleatorio(num_jobs=tamanho_problema, num_maquinas=3)
            cronograma = gerar_solucao_inicial(dados)
            df_cronograma = pd.DataFrame(cronograma)

            st.subheader("Solução Inicial")
            st.dataframe(df_cronograma)

            # Avaliar solução
            makespan = avalia(cronograma)
            st.subheader("Avalia")
            st.metric("Makespan", f"{makespan} unidades de tempo")

def tela_sobre():
    st.header("Sobre o Projeto")
    st.markdown("""
    ### Descrição
    O Job Shop Scheduling (ou escalonamento de oficina) é uma técnica usada para organizar e otimizar a produção em ambientes industriais onde diferentes tarefas (jobs) precisam passar por várias máquinas, cada uma com uma sequência específica.

    **Objetivos:**
    - Reduzir o tempo necessário para completar todos os trabalhos.
    - Garantir que duas tarefas não sejam atribuídas à mesma máquina ao mesmo tempo.

    ### Discentes
    - Johnny Keniti Mukai
    - Thais Ferreira Capucho
    """)

def tela_algoritmos_geneticos():
    st.header("Algoritmos Genéticos")
    st.info("Módulo em desenvolvimento.")

# Gera um problema aleatório
def gerar_problema_aleatorio(num_jobs, num_maquinas):
    maquinas = [f"M{i+1}" for i in range(num_maquinas)]
    dados = []

    for _ in range(num_jobs):
        # Embaralha a ordem das máquinas para cada job
        ordem_maquinas = random.sample(maquinas, len(maquinas))
        operacoes = [(maquina, random.randint(1, 10)) for maquina in ordem_maquinas]
        dados.append(operacoes)

    return dados

# Gera uma solução inicial
def gerar_solucao_inicial(dados):
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

# Retorna o makespan (tempo total de conclusão)
def avalia(cronograma):
    if not cronograma:
        return 0

    # Obtém o tempo de término das operações
    tempos_finais = [op["Fim"] for op in cronograma]

    # Obtém o maior tempo de término
    makespan = max(tempos_finais)
    return makespan

# 
def construir_lista_por_maquina(dados):
    maquina_ops = {}
    for job_id, operacoes in enumerate(dados):
        for op_index, (maquina, duracao) in enumerate(operacoes):
            if maquina not in maquina_ops:
                maquina_ops[maquina] = []
            maquina_ops[maquina].append({
                "job_id": job_id,
                "op_index": op_index,
                "duracao": duracao
            })
    return maquina_ops

#
def gerar_vizinho_maquina(maquina_ops):
    novo_maquina_ops = copy.deepcopy(maquina_ops)
    maquina = random.choice(list(novo_maquina_ops.keys()))
    ops = novo_maquina_ops[maquina]
    if len(ops) >= 2:
        i, j = random.sample(range(len(ops)), 2)
        ops[i], ops[j] = ops[j], ops[i]
    return novo_maquina_ops

#
def construir_cronograma_respeitando_ordem(dados, maquina_ops):
    disponibilidade_maquinas = {m: 0 for m in maquina_ops}
    disponibilidade_jobs = [0] * len(dados)
    cronograma = []

    # Para cada máquina, siga a ordem definida
    for maquina, ops in maquina_ops.items():
        for op in ops:
            job_id = op["job_id"]
            op_index = op["op_index"]
            duracao = op["duracao"]

            # Só pode começar após a operação anterior do job terminar
            tempo_job = disponibilidade_jobs[job_id]
            tempo_maquina = disponibilidade_maquinas[maquina]
            inicio = max(tempo_job, tempo_maquina)
            fim = inicio + duracao

            disponibilidade_maquinas[maquina] = fim
            disponibilidade_jobs[job_id] = fim

            cronograma.append({
                "Job": f"J{job_id+1}",
                "Operação": f"Op{op_index+1}",
                "Máquina": maquina,
                "Início": inicio,
                "Fim": fim
            })

    return cronograma

#
def subida_de_encosta(dados, max_iter=100):
    maquina_ops = construir_lista_por_maquina(dados)
    melhor_cronograma = construir_cronograma_respeitando_ordem(dados, maquina_ops)
    melhor_makespan = avalia(melhor_cronograma)

    for _ in range(max_iter):
        vizinho_ops = gerar_vizinho_maquina(maquina_ops)
        cronograma_vizinho = construir_cronograma_respeitando_ordem(dados, vizinho_ops)
        makespan_vizinho = avalia(cronograma_vizinho)

        if makespan_vizinho < melhor_makespan:
            maquina_ops = vizinho_ops
            melhor_cronograma = cronograma_vizinho
            melhor_makespan = makespan_vizinho

    return melhor_cronograma, melhor_makespan

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
