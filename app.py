import streamlit as st
from streamlit_option_menu import option_menu

# Funções para cada tela
def tela_metodos_basicos():
    st.header("Métodos Básicos")

    tipo_execucao = st.selectbox("Tipo de execução", ["Fixo", "Aleatório"])

    if tipo_execucao == "Aleatório":
        tamanho_problema = st.number_input("Tamanho do problema", min_value=1, step=1)
    else:
        tamanho_problema = None

    if st.button("Solução Inicial"):
        st.info("Função de solução inicial ainda não implementada.")

    metodo = st.selectbox(
        "Método",
        ["Subida de encosta", "Subida de encosta com tentativas", "Têmpera simulada"]
    )

    if st.button("Executar"):
        if tipo_execucao == "Aleatório" and tamanho_problema is None:
            st.warning("Por favor, defina o tamanho do problema.")
        else:
            st.info("Módulo em desenvolvimento.")

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
    st.title("Bem-vindo ao sistema de otimização")
    st.write("Use o menu lateral para navegar entre as opções.")
