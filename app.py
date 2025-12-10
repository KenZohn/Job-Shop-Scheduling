import copy
import math
import pandas as pd
import random
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import io

# ==============================
# FUNÇÕES BÁSICAS EXISTENTES
# ==============================

def resetar_variavel():
    if "solucao_inicial" in st.session_state:
        del st.session_state["solucao_inicial"]

def gerar_problema_aleatorio(num_jobs, num_maquinas):
    maquinas = [f"M{i+1}" for i in range(num_maquinas)]
    dados = []

    for _ in range(num_jobs):
        ordem_maquinas = random.sample(maquinas, len(maquinas))
        operacoes = [(maquina, random.randint(1, 10)) for maquina in ordem_maquinas]
        dados.append(operacoes)

    return dados

def gerar_solucao_inicial_aleatoria(dados, tamanho_problema):
    disponibilidade_maquinas = {}
    cronograma = []

    for job in dados:
        for maquina, _ in job:
            disponibilidade_maquinas[maquina] = 0

    todas_operacoes = []
    for job_id, operacoes in enumerate(dados, start=1):
        for op_index, (maquina, duracao) in enumerate(operacoes, start=1):
            todas_operacoes.append((job_id, op_index, maquina, duracao))

    random.shuffle(todas_operacoes)

    tempo_jobs = {job_id: 0 for job_id in range(1, len(dados)+1)}

    for job_id, op_index, maquina, duracao in todas_operacoes:
        inicio = max(tempo_jobs[job_id], disponibilidade_maquinas[maquina])
        fim = inicio + duracao
        disponibilidade_maquinas[maquina] = fim
        tempo_jobs[job_id] = fim

        cronograma.append({
            "Job": f"J{job_id}",
            "Operação": f"Op{op_index}",
            "Máquina": maquina,
            "Início": inicio,
            "Fim": fim
        })
    
    dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
    df = pd.DataFrame(dados_formatados, columns=[f"Op{i+1}" for i in range(len(dados[0]))], index=[f"J{i+1}" for i in range(tamanho_problema)])

    return cronograma, df

def avalia(cronograma):
    if not cronograma:
        return 0
    tempos_finais = [op["Fim"] for op in cronograma]
    makespan = max(tempos_finais)
    return makespan

def mostrar_solucao_fixa(dados):
    dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]
    df = pd.DataFrame(dados_formatados, columns=["Op1", "Op2", "Op3"], index=["J1", "J2", "J3"])

    st.subheader("Problema")
    st.dataframe(df)

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

    st.session_state.dados_problema = dados
    st.session_state.solucao_inicial = cronograma
    st.session_state.makespan_inicial = makespan
    st.session_state.df = df

def mostrar_solucao_inicial_aleatoria(dados, cronograma, df):
    st.subheader("Problema")
    st.dataframe(df)

    df_cronograma = pd.DataFrame(cronograma)
    st.subheader("Solução Inicial")
    st.dataframe(df_cronograma)

    makespan = avalia(cronograma)
    st.metric("Makespan", f"{makespan} unidades de tempo")

    st.session_state.dados_problema = dados
    st.session_state.solucao_inicial = cronograma
    st.session_state.makespan_inicial = makespan
    st.session_state.df = df

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

def gerar_vizinho(maquina_ops):
    novo = copy.deepcopy(maquina_ops)
    maquina = random.choice(list(novo.keys()))
    if len(novo[maquina]) >= 2:
        i, j = random.sample(range(len(novo[maquina])), 2)
        novo[maquina][i], novo[maquina][j] = novo[maquina][j], novo[maquina][i]
    return novo

def construir_cronograma(dados, maquina_ops):
    disponibilidade_maquinas = {m: 0 for m in maquina_ops}
    disponibilidade_jobs = [0] * len(dados)
    cronograma = []

    for maquina, ops in maquina_ops.items():
        for op in ops:
            job_id = op["job_id"]
            op_index = op["op_index"]
            duracao = op["duracao"]

            inicio = max(disponibilidade_maquinas[maquina], disponibilidade_jobs[job_id])
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

def subida_de_encosta(dados, solucao_inicial):
    maquina_ops = construir_lista_por_maquina(dados)
    melhor_cronograma = solucao_inicial
    melhor_makespan = avalia(melhor_cronograma)

    while True:
        vizinho_ops = gerar_vizinho(maquina_ops)
        cronograma_vizinho = construir_cronograma(dados, vizinho_ops)
        makespan_vizinho = avalia(cronograma_vizinho)

        if makespan_vizinho < melhor_makespan:
            maquina_ops = vizinho_ops
            melhor_cronograma = cronograma_vizinho
            melhor_makespan = makespan_vizinho
        else:
            break

    return melhor_cronograma, melhor_makespan

def subida_de_encosta_com_tentativas(dados, solucao_inicial, tmax=3):
    maquina_ops = construir_lista_por_maquina(dados)
    melhor_cronograma = solucao_inicial
    melhor_makespan = avalia(melhor_cronograma)

    t = 0
    while t < tmax:
        vizinho_ops = gerar_vizinho(maquina_ops)
        cronograma_vizinho = construir_cronograma(dados, vizinho_ops)
        makespan_vizinho = avalia(cronograma_vizinho)

        if makespan_vizinho < melhor_makespan:
            maquina_ops = vizinho_ops
            melhor_cronograma = cronograma_vizinho
            melhor_makespan = makespan_vizinho
            t = 0
        else:
            t += 1

    return melhor_cronograma, melhor_makespan

def tempera_simulada(dados, solucao_inicial, temp_inicial=500, temp_final=0.1, fator=0.8):
    maquina_ops = construir_lista_por_maquina(dados)
    melhor_cronograma = solucao_inicial
    melhor_makespan = avalia(melhor_cronograma)
    atual_makespan = melhor_makespan
    temperatura = temp_inicial

    while temperatura > temp_final:
        vizinho_ops = gerar_vizinho(maquina_ops)
        cronograma_vizinho = construir_cronograma(dados, vizinho_ops)
        makespan_vizinho = avalia(cronograma_vizinho)

        delta = makespan_vizinho - atual_makespan

        if delta < 0:
            atual_makespan = makespan_vizinho
            if makespan_vizinho < melhor_makespan:
                melhor_cronograma = cronograma_vizinho
                melhor_makespan = makespan_vizinho
        else:
            prob = math.exp(-delta / temperatura)
            if random.random() < prob:
                atual_makespan = makespan_vizinho

        temperatura *= fator

    return melhor_cronograma, melhor_makespan

def criar_arquivo_download(cronograma, nome_arquivo="cronograma_jobshop"):
    """Cria um arquivo CSV para download formatado corretamente"""
    df = pd.DataFrame(cronograma)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, sep=';', encoding='utf-8')
    buffer.seek(0)
    return buffer.getvalue()

# ==============================
# ALGORITMO GENÉTICO
# ==============================

def pop_ini_jobshop(dados, tamanho_pop):
    n_jobs = len(dados)
    n_ops = [len(job) for job in dados]
    cromossomo_base = []
    for j, ops in enumerate(n_ops):
        cromossomo_base += [j] * ops  # cada job aparece tantas vezes quanto suas operações
    
    pop = []
    for _ in range(tamanho_pop):
        individuo = cromossomo_base.copy()
        random.shuffle(individuo)
        pop.append(individuo)
    
    return pop


def decodificar_individuo_simples(individuo, dados):
    """
    Decodifica um indivíduo em cronograma detalhado.
    Retorna lista de dicionários: Job, Operação, Máquina, Início, Fim
    """
    cronograma = []
    tempo_maquinas = {maq: 0 for maq in {op[0] for job in dados for op in job}}
    tempo_jobs = {j: 0 for j in range(len(dados))}
    contagem_ops = {j: 0 for j in range(len(dados))}
    
    # 1. Percorre cromossomo
    for job_idx in individuo:
        op_idx = contagem_ops[job_idx]
        if op_idx < len(dados[job_idx]):
            maquina, duracao = dados[job_idx][op_idx]
            inicio = max(tempo_maquinas[maquina], tempo_jobs[job_idx])
            fim = inicio + duracao
            tempo_maquinas[maquina] = fim
            tempo_jobs[job_idx] = fim
            contagem_ops[job_idx] += 1
            cronograma.append({
                "Job": f"J{job_idx+1}",
                "Operação": f"Op{op_idx+1}",
                "Máquina": maquina,
                "Início": inicio,
                "Fim": fim
            })
    
    # 2. Força inclusão das operações restantes (se o cromossomo não percorreu todas)
    for job_idx, job in enumerate(dados):
        while contagem_ops[job_idx] < len(job):
            op_idx = contagem_ops[job_idx]
            maquina, duracao = job[op_idx]
            inicio = max(tempo_maquinas[maquina], tempo_jobs[job_idx])
            fim = inicio + duracao
            tempo_maquinas[maquina] = fim
            tempo_jobs[job_idx] = fim
            contagem_ops[job_idx] += 1
            cronograma.append({
                "Job": f"J{job_idx+1}",
                "Operação": f"Op{op_idx+1}",
                "Máquina": maquina,
                "Início": inicio,
                "Fim": fim
            })
    
    return cronograma


def aptidao_jobshop_simples(pop, dados):
    """Calcula aptidão (versão simplificada)"""
    fit = []
    for individuo in pop:
        cronograma = decodificar_individuo_simples(individuo, dados)
        makespan = avalia(cronograma)
        # Quanto menor o makespan, melhor (usar 1/makespan)
        if makespan > 0:
            fit.append(1.0 / makespan)
        else:
            fit.append(0.0)
    
    # Normalizar
    soma = sum(fit)
    if soma > 0:
        fit = [f / soma for f in fit]
    else:
        fit = [1.0 / len(fit) for _ in fit]
    
    return fit

def selecao_roleta_simples(fit):
    """Seleção por roleta (versão simplificada)"""
    if not fit:
        return 0
    
    soma = sum(fit)
    if soma == 0:
        return random.randint(0, len(fit) - 1)
    
    ale = random.random() * soma
    acumulado = 0
    
    for i, f in enumerate(fit):
        acumulado += f
        if acumulado >= ale:
            return i
    
    return len(fit) - 1

def cruzamento_ponto_unico(pai1, pai2):
    """Cruzamento em ponto único"""
    n = len(pai1)
    
    if n < 2:
        return pai1.copy(), pai2.copy()
    
    ponto = random.randint(1, n - 1)
    
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    
    return filho1, filho2

def mutacao_troca_simples(individuo):
    """Mutação por troca de posições"""
    n = len(individuo)
    
    if n < 2:
        return individuo
    
    # Criar cópia
    mutado = individuo.copy()
    
    # Escolher duas posições diferentes
    pos1, pos2 = random.sample(range(n), 2)
    
    # Trocar
    mutado[pos1], mutado[pos2] = mutado[pos2], mutado[pos1]
    
    return mutado

def algoritmo_genetico_simples(dados, tp=30, ng=50, tc=0.8, tm=0.1, ig=0.2):
    pop = pop_ini_jobshop(dados, tp)
    fit = aptidao_jobshop_simples(pop, dados)

    melhor_individuo = None
    melhor_makespan = float('inf')
    historico = []

    for geracao in range(ng):
        nova_pop = []
        while len(nova_pop) < tp:
            pai1_idx = selecao_roleta_simples(fit)
            pai2_idx = selecao_roleta_simples(fit)
            pai1, pai2 = pop[pai1_idx], pop[pai2_idx]

            if random.random() < tc:
                filho1, filho2 = cruzamento_ponto_unico(pai1, pai2)
            else:
                filho1, filho2 = pai1.copy(), pai2.copy()

            if random.random() < tm:
                filho1 = mutacao_troca_simples(filho1)
            if random.random() < tm:
                filho2 = mutacao_troca_simples(filho2)

            nova_pop.append(filho1)
            if len(nova_pop) < tp:
                nova_pop.append(filho2)

        # >>> Aplicar elitismo com IG
        elite = int(ig * tp)
        pop_ordenada = [x for _, x in sorted(zip(fit, pop), key=lambda z: z[0], reverse=True)]
        fit_desc = aptidao_jobshop_simples(nova_pop, dados)
        desc_ordenada = [x for _, x in sorted(zip(fit_desc, nova_pop), key=lambda z: z[0], reverse=True)]
        pop = pop_ordenada[:elite] + desc_ordenada[:tp-elite]
        fit = aptidao_jobshop_simples(pop, dados)

        # Atualizar melhor
        for individuo in pop:
            cronograma = decodificar_individuo_simples(individuo, dados)
            makespan = avalia(cronograma)
            if makespan < melhor_makespan:
                melhor_makespan = makespan
                melhor_individuo = individuo.copy()

        historico.append(melhor_makespan)

    cronograma_final = decodificar_individuo_simples(melhor_individuo, dados)
    return cronograma_final, melhor_makespan, historico

# ==============================
# TELAS DA APLICAÇÃO
# ==============================

def tela_metodos_basicos():
    st.header("Métodos Básicos")

    col1, col2 = st.columns(2)

    with col1:
        tipo_execucao = st.selectbox("Tipo de execução", ["Fixo", "Aleatório"], on_change=resetar_variavel)

        if tipo_execucao == "Aleatório":
            tamanho_problema = st.number_input("Tamanho do problema", min_value=1, step=1, value=3)
            num_maquinas = st.number_input("Número de máquinas", min_value=1, step=1, value=3)
        else:
            tamanho_problema = None
            num_maquinas = 3

        mostrar_solucao = st.button("Solução Inicial")
    
        if tipo_execucao == "Fixo":
            dados = [
                [("M1", 3), ("M2", 5), ("M3", 7)],
                [("M2", 9), ("M3", 1), ("M1", 4)],
                [("M3", 4), ("M1", 6), ("M2", 2)]
            ]

            if mostrar_solucao:
                mostrar_solucao_fixa(dados)
                st.session_state.dados_problema = dados

            elif "solucao_inicial" in st.session_state:
                mostrar_solucao_fixa(st.session_state.dados_problema)

        elif tipo_execucao == "Aleatório":
            if mostrar_solucao:
                dados = gerar_problema_aleatorio(num_jobs=tamanho_problema, num_maquinas=num_maquinas)
                cronograma, df = gerar_solucao_inicial_aleatoria(dados, tamanho_problema)
                mostrar_solucao_inicial_aleatoria(dados, cronograma, df)
                st.session_state.dados_problema = dados
                st.session_state.solucao_inicial = cronograma
                st.session_state.df = df
            
            elif "solucao_inicial" in st.session_state:
                mostrar_solucao_inicial_aleatoria(st.session_state.dados_problema, st.session_state.solucao_inicial, st.session_state.df)

    with col2:
        metodo = st.selectbox("Método", ["Subida de encosta", "Subida de encosta com tentativas", "Têmpera simulada"])

        if metodo == "Subida de encosta com tentativas":
            tentativas = st.number_input("Número de Tentativas", min_value=1, value=3)
        elif metodo == "Têmpera simulada":
            col_temp1, col_temp2, col_temp3 = st.columns(3)
            with col_temp1:
                temp_inicial = st.number_input("Temperatura Inicial", value=500)
            with col_temp2:
                temp_final = st.number_input("Temperatura Final", value=0.1)
            with col_temp3:
                fator_resfriamento = st.number_input("Fator de Resfriamento", value=0.8)

        executar = st.button("Executar")
        
        if executar:
            if ("dados_problema" not in st.session_state or 
                "solucao_inicial" not in st.session_state or
                "makespan_inicial" not in st.session_state):
                st.warning(" Por favor, clique em 'Solução Inicial' primeiro para gerar uma solução inicial.")
                return
            
            dados = st.session_state.dados_problema
            solucao_inicial = st.session_state.solucao_inicial
            makespan_inicial = st.session_state.makespan_inicial

            if metodo == "Subida de encosta":
                cronograma_otimizado, melhor_makespan = subida_de_encosta(dados, solucao_inicial)
                st.subheader("Solução (Subida de Encosta)")
                st.dataframe(pd.DataFrame(cronograma_otimizado))
                st.metric("Makespan Otimizado", f"{melhor_makespan} unidades de tempo")

            elif metodo == "Subida de encosta com tentativas":
                cronograma_otimizado, melhor_makespan = subida_de_encosta_com_tentativas(dados, solucao_inicial, tmax=tentativas)
                st.subheader("Solução (Subida de Encosta com Tentativas)")
                st.dataframe(pd.DataFrame(cronograma_otimizado))
                st.metric("Makespan Otimizado", f"{melhor_makespan} unidades de tempo")

            elif metodo == "Têmpera simulada":
                cronograma_otimizado, melhor_makespan = tempera_simulada(
                    dados, solucao_inicial, temp_inicial=temp_inicial, temp_final=temp_final, fator=fator_resfriamento
                )
                st.subheader("Solução (Têmpera Simulada)")
                st.dataframe(pd.DataFrame(cronograma_otimizado))
                st.metric("Makespan Otimizado", f"{melhor_makespan} unidades de tempo")
            
            ganho = (100 * (makespan_inicial - melhor_makespan) / makespan_inicial)
            st.metric("Ganho", f"{ganho:.2f} %")
            
            # BOTÃO DE DOWNLOAD
            st.subheader("Download da Solução")
            csv_data = criar_arquivo_download(cronograma_otimizado, f"solucao_{metodo.lower().replace(' ', '_')}")
            
            st.download_button(
                label="Baixar Cronograma",
                data=csv_data,
                file_name=f"cronograma_{metodo.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"download_{random.randint(1000, 9999)}"
            )

        # BOTÃO RELATÓRIO COMPARATIVO
        if st.button("COMPARAR TODOS OS MÉTODOS"):
            if "dados_problema" in st.session_state and "solucao_inicial" in st.session_state:
                st.session_state.pagina_atual = "Relatório Comparativo"
                st.rerun()
            else:
                st.warning("Por favor, clique em 'Solução Inicial' primeiro!")

def gerar_relatorio_comparativo():
    st.header("RELATÓRIO COMPARATIVO - TODOS OS MÉTODOS")
    
    # Verificar se existe solução inicial
    if "dados_problema" not in st.session_state or "solucao_inicial" not in st.session_state:
        st.warning("Por favor, vá para 'Métodos Básicos' e gere uma solução inicial primeiro!")
        return
    
    dados = st.session_state.dados_problema
    solucao_inicial = st.session_state.solucao_inicial
    makespan_inicial = st.session_state.makespan_inicial
    n = len(dados)  # Número de jobs
    
    st.subheader("Problema Atual")
    st.dataframe(st.session_state.df)
    
    st.subheader("Solução Inicial")
    st.dataframe(pd.DataFrame(solucao_inicial))
    st.metric("Makespan Inicial", f"{makespan_inicial} unidades de tempo")
    
    st.subheader("Resultados dos Métodos de Otimização")
    
    # Executar todos os métodos
    resultados = []
    
    # Subida de Encosta Simples
    with st.spinner("Executando Subida de Encosta..."):
        cronograma_se, makespan_se = subida_de_encosta(dados, solucao_inicial)
        ganho_se = (100 * (makespan_inicial - makespan_se) / makespan_inicial)
        resultados.append(["SE", "---", f"{ganho_se:.2f}%"])
    
    # Subida de Encosta com Tentativas
    with st.spinner("Executando Subida com Tentativas..."):
        cronograma_set1, makespan_set1 = subida_de_encosta_com_tentativas(dados, solucao_inicial, tmax=n)
        ganho_set1 = (100 * (makespan_inicial - makespan_set1) / makespan_inicial)
        resultados.append(["SET", f"TMAX={n}", f"{ganho_set1:.2f}%"])
    
    # Têmpera Simulada
    with st.spinner("Executando Têmpera Simulada..."):
        cronograma_te1, makespan_te1 = tempera_simulada(dados, solucao_inicial, temp_inicial=500, temp_final=0.1, fator=0.8)
        ganho_te1 = (100 * (makespan_inicial - makespan_te1) / makespan_inicial)
        resultados.append(["TE", "TI=500 TF=0.1 FR=0.8", f"{ganho_te1:.2f}%"])
    
    # Cria DataFrame com os resultados
    df_resultados = pd.DataFrame(resultados, columns=["Método", "Observação", "Ganho"])
    
    # Exibir tabela
    st.subheader("Tabela de Resultados")
    st.table(df_resultados.style.hide(axis="index"))
    
    # Encontrar o melhor resultado
    melhor_ganho = max(float(resultado[2].replace('%', '')) for resultado in resultados)
    melhor_metodo = next(resultado for resultado in resultados if float(resultado[2].replace('%', '')) == melhor_ganho)
    
    st.success(f"**MELHOR MÉTODO**: {melhor_metodo[0]} - {melhor_metodo[1]} com ganho de {melhor_metodo[2]}")
    
    # BOTÃO DE DOWNLOAD
    st.subheader("Download do Relatório Completo")
    
    # Cria relatório 
    relatorio_data = []
    relatorio_data.append(["PROBLEMA", "", ""])
    for i, job in enumerate(dados):
        relatorio_data.append([f"Job {i+1}", str(job), ""])
    
    relatorio_data.append(["", "", ""])
    relatorio_data.append(["SOLUÇÃO INICIAL", f"Makespan: {makespan_inicial}", ""])
    
    relatorio_data.append(["", "", ""])
    relatorio_data.append(["MÉTODO", "OBSERVAÇÃO", "GANHO"])
    
    for linha in resultados:
        relatorio_data.append(linha)
    
    relatorio_data.append(["", "", ""])
    relatorio_data.append(["MELHOR MÉTODO", f"{melhor_metodo[0]} - {melhor_metodo[1]}", melhor_metodo[2]])
    
    # Converte para CSV
    df_relatorio = pd.DataFrame(relatorio_data, columns=["Método", "Observação", "Ganho"])
    csv_relatorio = df_relatorio.to_csv(index=False, sep=';', encoding='utf-8')
    
    # Botão de download
    st.download_button(
        label="Baixar Relatório Completo",
        data=csv_relatorio,
        file_name=f"relatorio_completo_jobshop_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key="download_relatorio_completo"
    )

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
    """Tela do Algoritmo Genético - VERSÃO CORRIGIDA E ÚNICA"""
    st.header("Algoritmos Genéticos - Job Shop Scheduling")
    
    # Inicializar estado
    if "ag_problema_carregado" not in st.session_state:
        st.session_state.ag_problema_carregado = False
    
    # Layout principal
    col_config, col_exec = st.columns(2)
    
    with col_config:
        st.subheader("Configuração do Problema")
        
        # Tipo de problema
        tipo_problema = st.radio(
            "Selecione o tipo de problema:",
            ["Usar problema fixo (exemplo)", "Usar problema aleatório"],
            index=0,
            key="tipo_problema_ag"
        )
        
        if tipo_problema == "Usar problema fixo (exemplo)":
            if st.button("Carregar Problema Fixo", width='stretch', key="btn_fixo"):
                # Problema fixo
                dados_fixo = [
                    [("M1", 3), ("M2", 5), ("M3", 7)],
                    [("M2", 9), ("M3", 1), ("M1", 4)],
                    [("M3", 4), ("M1", 6), ("M2", 2)]
                ]
                
                st.session_state.dados_ag = dados_fixo
                st.session_state.ag_problema_carregado = True
                
                # Mostrar o problema
                dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados_fixo]
                df_fixo = pd.DataFrame(dados_formatados, 
                                      columns=["Op1", "Op2", "Op3"], 
                                      index=["J1", "J2", "J3"])
                st.session_state.df_ag = df_fixo
                
                # Calcular makespan inicial
                cronograma_inicial, _ = gerar_solucao_inicial_aleatoria(dados_fixo, 3)
                st.session_state.makespan_inicial_ag = avalia(cronograma_inicial)

                st.session_state.mostrar_resultados_ag = False
                if 'ag_resultados' in st.session_state:
                    del st.session_state.ag_resultados
                
                st.rerun()  # Força atualização para mostrar o problema
        
        elif tipo_problema == "Usar problema aleatório":
            col_rand1, col_rand2 = st.columns(2)
            with col_rand1:
                n_jobs = st.number_input("Número de Jobs", min_value=2, max_value=10, value=3, key="n_jobs_ag")
            with col_rand2:
                n_maquinas = st.number_input("Número de Máquinas", min_value=2, max_value=10, value=3, key="n_maq_ag")
            
            if st.button("Gerar Problema Aleatório", width='stretch', key="btn_aleatorio"):
                dados_aleatorio = gerar_problema_aleatorio(n_jobs, n_maquinas)
                st.session_state.dados_ag = dados_aleatorio
                st.session_state.ag_problema_carregado = True
                
                # Mostrar o problema
                cronograma_ini, df_aleatorio = gerar_solucao_inicial_aleatoria(dados_aleatorio, n_jobs)
                st.session_state.df_ag = df_aleatorio
                st.session_state.makespan_inicial_ag = avalia(cronograma_ini)

                st.session_state.mostrar_resultados_ag = False
                if 'ag_resultados' in st.session_state:
                    del st.session_state.ag_resultados

                st.rerun()  # Força atualização
        
        # Mostrar problema se carregado
        if st.session_state.ag_problema_carregado and "df_ag" in st.session_state:
            st.divider()
            st.subheader("Problema Carregado")
            st.dataframe(st.session_state.df_ag, width='stretch')
            
            if "makespan_inicial_ag" in st.session_state:
                st.metric("Makespan da Solução Inicial", 
                         f"{st.session_state.makespan_inicial_ag} unidades")
    
    with col_exec:
        st.subheader("Parâmetros do Algoritmo")
        
        # Parâmetros do AG
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            tp = st.number_input("Tamanho da População (TP)", 
                                min_value=10, max_value=100, value=20,
                                key="tp_input")
            ng = st.number_input("Número de Gerações (NG)", 
                                min_value=10, max_value=200, value=30,
                                key="ng_input")
        with col_param2:
            tc = st.slider("Taxa de Cruzamento (TC)", 
                          min_value=0.0, max_value=1.0, value=0.8, step=0.05,
                          key="tc_slider")
            tm = st.slider("Taxa de Mutação (TM)", 
                          min_value=0.0, max_value=0.3, value=0.1, step=0.01,
                          key="tm_slider")
            ig = st.slider("Taxa de Elitismo (IG)", 
                          min_value=0.0, max_value=0.5, value=0.2, step=0.05,
                          key="ig_slider")
        
        # Botão de execução
        executar_disabled = not st.session_state.ag_problema_carregado
        
        # Verificar se o botão foi clicado
        if st.button("Executar Algoritmo Genético", 
                    type="primary", 
                    width='stretch',
                    disabled=executar_disabled,
                    key="executar_ag"):
            
            if not st.session_state.ag_problema_carregado:
                st.error("Por favor, carregue um problema primeiro!")
                st.stop()
            
            # Container para mostrar progresso
            progress_container = st.container()
            
            with progress_container:
                with st.spinner("Executando Algoritmo Genético... Aguarde!"):
                    # Executar AG
                    cronograma_otimizado, makespan_otimizado, historico = algoritmo_genetico_simples(
                        st.session_state.dados_ag,
                        tp=tp,
                        ng=ng,
                        tc=tc,
                        tm=tm,
                        ig=ig
                    )
                
                # Armazenar resultados no session_state
                st.session_state.ag_resultados = {
                    'cronograma': cronograma_otimizado,
                    'makespan': makespan_otimizado,
                    'historico': historico
                }
            
            # Marcar que temos resultados para mostrar
            st.session_state.mostrar_resultados_ag = True
            
            # Forçar rerun para mostrar resultados
            st.rerun()
        
        # Mostrar resultados se existirem
        if st.session_state.get('mostrar_resultados_ag', False) and 'ag_resultados' in st.session_state:
            resultados = st.session_state.ag_resultados
            
            # Métricas
            makespan_inicial = st.session_state.makespan_inicial_ag
            makespan_otimizado = resultados['makespan']
            ganho = ((makespan_inicial - makespan_otimizado) / makespan_inicial) * 100 if makespan_inicial > 0 else 0
            
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.metric("Makespan Inicial", f"{makespan_inicial}")
            with col_res2:
                st.metric("Makespan Otimizado", f"{makespan_otimizado}")
            with col_res3:
                st.metric("Ganho", f"{ganho:.1f}%", 
                         delta=f"{ganho:.1f}%" if ganho > 0 else None,
                         delta_color="normal" if ganho > 0 else "off")
            
            # Tabs para diferentes visualizações
            tab1, tab2, tab3 = st.tabs(["📅 Cronograma", "📈 Convergência", "💾 Download"])
            
            with tab1:
                st.subheader("Cronograma Otimizado")
                df_cronograma = pd.DataFrame(resultados['cronograma'])
                st.dataframe(df_cronograma, width='stretch')
            
            with tab2:
                st.subheader("Convergência do Algoritmo")
                if resultados['historico']:
                    df_historico = pd.DataFrame({
                        "Geração": range(1, len(resultados['historico']) + 1),
                        "Makespan": resultados['historico']
                    })
                    st.line_chart(df_historico.set_index("Geração"))
                    
                    # Estatísticas
                    st.write("**Estatísticas:**")
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("Melhor", f"{min(resultados['historico'])}")
                    with col_stat2:
                        st.metric("Pior", f"{max(resultados['historico'])}")
                    with col_stat3:
                        if len(resultados['historico']) >= 10:
                            st.metric("Média (últimas 10)", f"{np.mean(resultados['historico'][-10:]):.1f}")
            
            with tab3:
                st.subheader("Download da Solução")
                csv_data = criar_arquivo_download(resultados['cronograma'])
                
                st.download_button(
                    label="Baixar Cronograma (CSV)",
                    data=csv_data,
                    file_name=f"cronograma_ag_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch',
                    key="download_ag"
                )
        
        elif executar_disabled:
            st.info("ℹCarregue um problema na coluna à esquerda para habilitar a execução.")
    
    # Seção de explicação
    st.divider()
    with st.expander("📖 Como funciona o Algoritmo Genético"):
        st.markdown("""
        ### Conceito Básico
        O Algoritmo Genético é inspirado na evolução natural:
        
        1. **População**: Conjunto de soluções candidatas
        2. **Seleção**: As melhores soluções "sobrevivem"
        3. **Reprodução**: Soluções combinam para gerar "filhos"
        4. **Mutação**: Pequenas alterações aleatórias
        5. **Substituição**: Nova geração substitui a anterior
        
        ### Parâmetros Importantes
        
        | Parâmetro | Significado | Recomendação |
        |-----------|-------------|--------------|
        | **TP** | Tamanho da população | 20-50 (maior = mais diverso, mas mais lento) |
        | **NG** | Número de gerações | 30-100 (maior = mais tempo para convergir) |
        | **TC** | Taxa de cruzamento | 0.7-0.9 (alta para boa exploração) |
        | **TM** | Taxa de mutação | 0.05-0.15 (baixa para evitar desvio) |
        
        ### Para este problema
        - Cada solução é uma **sequência de jobs**
        - **Aptidão = 1 / makespan** (quanto menor o makespan, melhor)
        - **Cruzamento**: Combina duas sequências
        - **Mutação**: Troca posições na sequência
        
        **Dica**: Comece com TP=20, NG=30 para testes rápidos!
        """)

# ==============================
# CONFIGURAÇÃO PRINCIPAL
# ==============================

# Configurar página
st.set_page_config(
    page_title="Job Shop Scheduling",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar variáveis de sessão
if "menu_anterior" not in st.session_state:
    st.session_state.menu_anterior = None
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Início"
if "ag_problema_carregado" not in st.session_state:
    st.session_state.ag_problema_carregado = False
if "mostrar_resultados_ag" not in st.session_state:
    st.session_state.mostrar_resultados_ag = False

# Menu principal
with st.sidebar:
    escolha = option_menu(
        menu_title="Menu",
        options=["Início", "Métodos Básicos", "Relatório Comparativo", "Algoritmos Genéticos", "Sobre"],
        icons=["house", "calculator", "trophy", "shuffle", "info-circle"],
        menu_icon="list",
        default_index=["Início", "Métodos Básicos", "Relatório Comparativo", "Algoritmos Genéticos", "Sobre"].index(
            st.session_state.pagina_atual
        ) if st.session_state.pagina_atual in ["Início", "Métodos Básicos", "Relatório Comparativo", "Algoritmos Genéticos", "Sobre"] else 0,
        orientation="vertical",
        styles={
            "nav-link-selected": {
                "background-color": "#464646",
                "color": "white",
                "font-weight": "bold"
            }
        }
    )

# Atualizar a página atual
st.session_state.pagina_atual = escolha

# Navegação entre telas
if st.session_state.pagina_atual == "Métodos Básicos":
    tela_metodos_basicos()
elif st.session_state.pagina_atual == "Relatório Comparativo":
    gerar_relatorio_comparativo()
elif st.session_state.pagina_atual == "Algoritmos Genéticos":
    tela_algoritmos_geneticos()
elif st.session_state.pagina_atual == "Sobre":
    tela_sobre()
else:
    st.title("Job Shop Scheduling")
    st.markdown("---")
    st.markdown("""
    ## Bem-vindo ao Sistema de Otimização de Job Shop Scheduling!
    
    Este sistema permite otimizar o escalonamento de tarefas em um ambiente de produção onde:
    
    - **Jobs** precisam passar por várias **máquinas**
    - Cada job tem uma sequência específica de operações
    - Cada operação tem uma duração em uma máquina específica
    
    ### Objetivo
    Minimizar o **makespan** (tempo total para completar todos os jobs).
    
    ### Funcionalidades
    
    1. **Métodos Básicos**: Heurísticas de otimização local
    2. **Algoritmos Genéticos**: Meta-heurística inspirada na evolução natural
    3. **Relatório Comparativo**: Comparação entre diferentes métodos
    
    ### Como começar
    
    1. Vá para **"Métodos Básicos"** para gerar um problema e testar otimizações simples
    2. Experimente **"Algoritmos Genéticos"** para uma abordagem evolutiva
    3. Use **"Relatório Comparativo"** para comparar todos os métodos
    
    ### Desenvolvido por
    - Johnny Keniti Mukai
    - Thais Ferreira Capucho
    
    ---
    """)
    
    # Quick links
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ir para Métodos Básicos", width='stretch'):
            st.session_state.pagina_atual = "Métodos Básicos"
            st.rerun()
    with col2:
        if st.button("Ir para Algoritmos Genéticos", width='stretch'):
            st.session_state.pagina_atual = "Algoritmos Genéticos"
            st.rerun()
    with col3:
        if st.button("Ver Sobre", width='stretch'):
            st.session_state.pagina_atual = "Sobre"
            st.rerun()

# Reiniciar variáveis
if escolha != st.session_state.menu_anterior:
    if "solucao_inicial" in st.session_state:
        del st.session_state["solucao_inicial"]
    st.session_state.menu_anterior = escolha