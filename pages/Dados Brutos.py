# -----------------------------
# IMPORTAÇÕES
# -----------------------------
import requests
import pandas as pd
import streamlit as st
import time


# -----------------------------
# CONFIGURAÇÃO DO APP
# -----------------------------
@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon= '✅')
    time.sleep(5)
    sucesso.empty()
    return 


st.set_page_config(layout='wide')
st.title("Dados Brutos")

# -----------------------------
# COLETA E TRATAMENTO DOS DADOS
# -----------------------------
url = "http://labdados.com/produtos"
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')
dados_csv = dados.to_csv()


# -----------------------------
# MENU ACIMA DA TABELA
# -----------------------------
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns),list(dados.columns))

# -----------------------------
# MENU LATERAL PARA FILTRAGEM
# -----------------------------

st.sidebar.title('Filtros')
## filtros do sidebar
with st.sidebar.expander('Nome do produto'):
    opcoes_produtos = ['Todos os produtos'] + sorted(dados['Produto'].unique().tolist())

    selecionados = st.multiselect(
        'Selecione os produtos',
        options=opcoes_produtos,
        default=['Todos os produtos']
    )

    # Se 'Todos os produtos' estiver selecionado, usa todos
    if 'Todos os produtos' in selecionados:
        produtos = dados['Produto'].unique().tolist()
    else:
        produtos = selecionados

with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# -----------------------------
# FILTROS
# -----------------------------

query= '''
`Categoria do Produto` in @categoria and \
Produto in @produtos and \
@preco[0] <=  Preço <= @preco[1] and \
@data_compra [0] <= `Data da Compra` <= @data_compra [1] and\
@frete[0] <=  Frete <= @frete[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0] <=  `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <=  `Quantidade de parcelas` <= @qtd_parcelas[1]

'''

# -----------------------------
# TABELA
# -----------------------------

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]



st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :red[{dados_filtrados.shape[0]}] linhas e :red[{dados_filtrados.shape[1]}] colunas filtradas')

st.markdown('Defina um nome para o arquivo:')
col1,col2 = st.columns(2)
with col1:
    nome_arquivo = st.text_input('', label_visibility= 'collapsed', value= 'dados')
    nome_arquivo +='.csv'
with col2:
    st.download_button('Fazer Download da tabela em csv',
                    data=converte_csv(dados_filtrados),
                    file_name= nome_arquivo,
                    mime= 'text/csv',
                    on_click= mensagem_sucesso)
