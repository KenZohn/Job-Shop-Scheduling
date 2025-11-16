import copy
import math
import pandas as pd
import random
import streamlit as st
from streamlit_option_menu import option_menu
import io

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

#FUNÇÃO DE DOWNLOAD
def criar_arquivo_download(cronograma, nome_arquivo="cronograma_jobshop"):
    """Cria um arquivo CSV para download formatado corretamente"""
    
    # Criar DataFrame
    df = pd.DataFrame(cronograma)
    
    # Criar buffer em memória
    buffer = io.StringIO()
    
    # delimitador ponto e vírgula
    df.to_csv(buffer, index=False, sep=';', encoding='utf-8')
    
    # Resetar posição do buffer
    buffer.seek(0)
    
    return buffer.getvalue()

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
            
            #BOTÃO DE DOWNLOAD
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
    
    # Subida de Encosta com Tentativas - diferentes valores de TMAX
    with st.spinner("Executando Subida com Tentativas (TMAX=N)..."):
        cronograma_set1, makespan_set1 = subida_de_encosta_com_tentativas(dados, solucao_inicial, tmax=n)
        ganho_set1 = (100 * (makespan_inicial - makespan_set1) / makespan_inicial)
        resultados.append(["SET", f"TMAX={n} ; TMAX=2*{n}", f"{ganho_set1:.2f}%"])
    
    with st.spinner("Executando Subida com Tentativas (TMAX=2*N)..."):
        cronograma_set2, makespan_set2 = subida_de_encosta_com_tentativas(dados, solucao_inicial, tmax=2*n)
        ganho_set2 = (100 * (makespan_inicial - makespan_set2) / makespan_inicial)
        resultados.append(["SET", f"TMAX={n//2} ; TMAX={n}", f"{ganho_set2:.2f}%"])
    
    with st.spinner("Executando Subida com Tentativas (TMAX=N/2)..."):
        cronograma_set3, makespan_set3 = subida_de_encosta_com_tentativas(dados, solucao_inicial, tmax=max(1, n//2))
        ganho_set3 = (100 * (makespan_inicial - makespan_set3) / makespan_inicial)
        resultados.append(["SET", f"TMAX={max(1, n//2)} ; TMAX={max(1, n//2)}", f"{ganho_set3:.2f}%"])
    
    # Têmpera Simulada - diferentes combinações de parâmetros
    with st.spinner("Executando Têmpera Simulada (TI=100, TF=0.1, FR=0.8)..."):
        cronograma_te1, makespan_te1 = tempera_simulada(dados, solucao_inicial, temp_inicial=100, temp_final=0.1, fator=0.8)
        ganho_te1 = (100 * (makespan_inicial - makespan_te1) / makespan_inicial)
        resultados.append(["TE", "TI=100 TF=0.1 FR=0.8", f"{ganho_te1:.2f}%"])
    
    with st.spinner("Executando Têmpera Simulada (TI=200, TF=0.1, FR=0.8)..."):
        cronograma_te2, makespan_te2 = tempera_simulada(dados, solucao_inicial, temp_inicial=200, temp_final=0.1, fator=0.8)
        ganho_te2 = (100 * (makespan_inicial - makespan_te2) / makespan_inicial)
        resultados.append(["TE", "TI=200 TF=0.1 FR=0.8", f"{ganho_te2:.2f}%"])
    
    with st.spinner("Executando Têmpera Simulada (TI=500, TF=0.1, FR=0.8)..."):
        cronograma_te3, makespan_te3 = tempera_simulada(dados, solucao_inicial, temp_inicial=500, temp_final=0.1, fator=0.8)
        ganho_te3 = (100 * (makespan_inicial - makespan_te3) / makespan_inicial)
        resultados.append(["TE", "TI=500 TF=0.1 FR=0.8", f"{ganho_te3:.2f}%"])
    
    with st.spinner("Executando Têmpera Simulada (TI=200, TF=0.1, FR=0.9)..."):
        cronograma_te4, makespan_te4 = tempera_simulada(dados, solucao_inicial, temp_inicial=200, temp_final=0.1, fator=0.9)
        ganho_te4 = (100 * (makespan_inicial - makespan_te4) / makespan_inicial)
        resultados.append(["TE", "TI=200 TF=0.1 FR=0.9", f"{ganho_te4:.2f}%"])
    
    with st.spinner("Executando Têmpera Simulada (TI=500, TF=0.1, FR=0.9)..."):
        cronograma_te5, makespan_te5 = tempera_simulada(dados, solucao_inicial, temp_inicial=500, temp_final=0.1, fator=0.9)
        ganho_te5 = (100 * (makespan_inicial - makespan_te5) / makespan_inicial)
        resultados.append(["TE", "TI=500 TF=0.1 FR=0.9", f"{ganho_te5:.2f}%"])
    
    with st.spinner("Executando Têmpera Simulada (TI=200, TF=0.01, FR=0.9)..."):
        cronograma_te6, makespan_te6 = tempera_simulada(dados, solucao_inicial, temp_inicial=200, temp_final=0.01, fator=0.9)
        ganho_te6 = (100 * (makespan_inicial - makespan_te6) / makespan_inicial)
        resultados.append(["TE", "TI=200 TF=0.01 FR=0.9", f"{ganho_te6:.2f}%"])
    
    with st.spinner("Executando Têmpera Simulada (TI=500, TF=0.01, FR=0.9)..."):
        cronograma_te7, makespan_te7 = tempera_simulada(dados, solucao_inicial, temp_inicial=500, temp_final=0.01, fator=0.9)
        ganho_te7 = (100 * (makespan_inicial - makespan_te7) / makespan_inicial)
        resultados.append(["TE", "TI=500 TF=0.01 FR=0.9", f"{ganho_te7:.2f}%"])
    
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
    st.header("Algoritmos Genéticos")
    st.info("Módulo em desenvolvimento.")

# Inicializar variáveis de sessão
if "menu_anterior" not in st.session_state:
    st.session_state.menu_anterior = None
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Início"

#mostrar qual página é baseado no session_state
if st.session_state.pagina_atual == "Relatório Comparativo":
    escolha_efetiva = "Relatório Comparativo"
else:
    escolha_efetiva = st.session_state.pagina_atual

# Menu principal
with st.sidebar:
    escolha = option_menu(
        menu_title="Menu",
        options=["Início", "Métodos Básicos", "Relatório Comparativo", "Sobre", "Algoritmos Genéticos"],
        icons=["house", "calculator", "trophy", "info-circle", "shuffle"],
        menu_icon="list",
        default_index=["Início", "Métodos Básicos", "Relatório Comparativo", "Sobre", "Algoritmos Genéticos"].index(escolha_efetiva),
        orientation="vertical",
        styles={
            "container": {"padding": "5px", "background-color": "#f0f2f6"},
            "icon": {"color": "#262730", "font-size": "16px"}, 
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "2px",
                "padding": "10px",
                "border-radius": "8px",
                "color": "#262730",
                "background-color": "#f0f2f6"
            },
            "nav-link:hover": {
                "background-color": "#e6e9ef",
                "color": "#262730"
            },
            "nav-link-selected": {
                "background-color": "#4e8cff",
                "color": "white",
                "font-weight": "bold"
            }
        }
    )

# Atualizar a página atual
if escolha != st.session_state.pagina_atual:
    st.session_state.pagina_atual = escolha

# Navegação entre telas
if st.session_state.pagina_atual == "Métodos Básicos":
    tela_metodos_basicos()
elif st.session_state.pagina_atual == "Relatório Comparativo":
    gerar_relatorio_comparativo()
elif st.session_state.pagina_atual == "Sobre":
    tela_sobre()
elif st.session_state.pagina_atual == "Algoritmos Genéticos":
    tela_algoritmos_geneticos()
else:
    st.title("Job Shop Scheduling")
    st.write("Use o menu lateral para navegar entre as opções.")
    st.info("**Dica**: Comece pela opção 'Métodos Básicos' para gerar uma solução inicial, depois use 'Relatório Comparativo' para comparar todos os métodos!")

# Reiniciar variáveis
if escolha != st.session_state.menu_anterior:
    if "solucao_inicial" in st.session_state:
        del st.session_state["solucao_inicial"]
    st.session_state.menu_anterior = escolha