# Job Shop Scheduling

O Job Shop Scheduling (ou escalonamento de oficina) é uma técnica usada para organizar e otimizar a produção em ambientes industriais onde diferentes tarefas (jobs) precisam passar por várias máquinas, cada uma com uma sequência específica.

**Objetivos:**
- Reduzir o tempo necessário para completar todos os trabalhos.
- Garantir que duas tarefas não sejam atribuídas à mesma máquina ao mesmo tempo.

## Versão do Python
O desenvolvimento foi realizado nas versões 3.13.4 e 3.13.7 do Python.

## Instalação das Dependências
### Crie um ambiente virtual
No terminal, vá até o diretório do projeto e execute o comando abaixo para criar um ambiente virtual para não gerar conflitos com bibliotecas de outros projetos.
```
python -m venv venv
```
### Ative o ambiente virtual

Windows (cmd):
```
venv\Scripts\activate
```
Windows (PowerShell):
```
.\venv\Scripts\Activate.ps1
```
macOS/Linux:
```
source venv/bin/activate
```

### Instale as bibliotecas
É possível instalar todas as bibliotecas necessárias de uma vez utilizando o comando abaixo:
```
pip install -r requirements.txt
```

Ou instalar separadamente:
```
pip install streamlit
pip install streamlit_option_menu
pip install pandas
```

## Execução da Aplicação

Para executar a aplicação, utilize o seguinte comando:
```
streamlit run app.py
```

A aplicação será aberta em um navegador.

Caso a aplicação não abra, copie e cole a URL exibida no terminal em seu navegador, ou utilize a URL abaixo:
```
http://localhost:8501
```
