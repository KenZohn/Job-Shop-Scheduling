import streamlit as st
import pandas as pd

# Matriz original com tuplas
dados = [
    [("M1", 3), ("M2", 2), ("M3", 2)],
    [("M2", 2), ("M3", 1), ("M1", 4)],
    [("M3", 4), ("M1", 3), ("M2", 2)]
]

# Converte cada tupla em string
dados_formatados = [[f"{maquina} - {tempo}" for maquina, tempo in linha] for linha in dados]

# Cria o DataFrame
df = pd.DataFrame(dados_formatados, columns=["Op1", "Op2", "Op3"], index=["J1", "J2", "J3"])

# Exibe no Streamlit
st.dataframe(df)






import streamlit as st
import pandas as pd

# Matriz inicial como strings
dados = [
    ["M1 - 3", "M2 - 2", "M3 - 2"],
    ["M2 - 2", "M3 - 1", "M1 - 4"],
    ["M3 - 4", "M1 - 3", "M2 - 2"]
]

df = pd.DataFrame(dados, columns=["Op1", "Op2", "Op3"], index=["J1", "J2", "J3"])

# Editor interativo
df_editado = st.data_editor(df, num_rows="dynamic")

# Exibe resultado
st.write("Matriz editada:")
st.dataframe(df_editado)
