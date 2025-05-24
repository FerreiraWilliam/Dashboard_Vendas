# -----------------------------
# AUTENTICAÇÃO COM USUÁRIO E SENHA
# -----------------------------
import streamlit as st

# Dicionário de usuários e senhas (poderia vir de um arquivo seguro)
USERS = {
    "admin": "9d0cb87a",
    "keyvilla": "aguiar123",
    "ana": "minhasenha789"
}

def login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("Login 🔒")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if USERS.get(username) == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success(f"Bem-vindo, {username}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        st.stop()

login()

# -----------------------------
# IMPORTAÇÕES
# -----------------------------
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

# -----------------------------
# CONFIGURAÇÃO DO APP
# -----------------------------
st.set_page_config(
    page_title="Vendas",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Dashboard de Vendas 🛒")

# -----------------------------
# COLETA E TRATAMENTO DOS DADOS
# -----------------------------
url = "http://labdados.com/produtos"
regioes = ['Brasil','Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regioes = st.sidebar.selectbox('Filtro de Estados', regioes)

if regioes == 'Brasil':
    regioes = ''

todos_ano = st.sidebar.checkbox('Dados de todo o periodo',value=True)
if todos_ano:
    ano = ''
else:
    ano = st.sidebar.slider('Ano',2020,2023)

query_string = {'regiao': regioes.lower(), 'ano':ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# -----------------------------
# FUNÇÕES AUXILIARES
# -----------------------------
def formatar_valores(valor):
    if valor >= 1_000_000_000:
        return f"R$ {valor / 1_000_000_000:.2f} bilhões"
    elif valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} milhões"
    elif valor >= 1_000:
        return f"R$ {valor / 1_000:.2f} mil"
    else:
        return f"R$ {valor:.2f}"

# -----------------------------
# MÉTRICAS GERAIS
# -----------------------------
receita_total = dados['Preço'].sum()
quantidade_total = len(dados)

# -----------------------------
# TABELAS
# -----------------------------

## Receita por estado
receita_estados = dados.groupby('Local da compra')['Preço'].sum().reset_index()
receita_estados = dados[['Local da compra', 'lat', 'lon']].drop_duplicates().merge(
    receita_estados, on='Local da compra'
).sort_values('Preço', ascending=False)


## Receita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

## Receita por categoria
receita_por_categoria = dados.groupby('Categoria do Produto')['Preço'].sum().sort_values(ascending=False).reset_index()

## Receita e contagem por vendedor
receita_por_vendedor = dados.groupby('Vendedor')['Preço'].agg(total='sum', quantidade='count').sort_values('total', ascending=False)

## Quantidade de Vendas mensal
quantidade_vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].agg(quantidade = 'count').reset_index()
quantidade_vendas_mensal['Ano'] = quantidade_vendas_mensal['Data da Compra'].dt.year
quantidade_vendas_mensal['Mes'] = quantidade_vendas_mensal['Data da Compra'].dt.month_name()

## Quantidade de vendas por estado
quantidade_vendas_estado = dados.groupby('Local da compra')['Preço'].agg(quatidade_vendas = 'count')
quantidade_vendas_estado = dados[['Local da compra', 'lat', 'lon']].drop_duplicates().merge(
    quantidade_vendas_estado, on='Local da compra'
).sort_values('quatidade_vendas', ascending=False)

# Quantidade de vendas por Categoria

quantidade_vendas_categoria = dados.groupby('Categoria do Produto')['Preço'].agg(total='sum', quantidade='count').sort_values('total', ascending=False).reset_index()


# -----------------------------
# GRÁFICOS
# -----------------------------

## 1 Mapa de receita por local
fig_mapa_receita = px.scatter_geo(
    receita_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    hover_name='Local da compra',
    size='Preço',
    color='Preço',
    title="Receita por Local de Compra",
    template="seaborn"
)

## 2 Mapa de Quantidade de Vendas por local
fig_mapa_qtd_vendas = px.scatter_geo(
    quantidade_vendas_estado,
    lat='lat',
    lon='lon',
    scope='south america',
    hover_name='Local da compra',
    size='quatidade_vendas',
    color='quatidade_vendas',
    title="Quantidade de vendas por Local de Compra",
    template="seaborn"
)

## 3 Quantidade de vendas mensal
fig_qtd_vendas_mensal = px.line(
    quantidade_vendas_mensal,
    x='Mes',
    y='quantidade',
    markers=True,
    color='Ano',
    line_dash='Ano',
    line_shape='spline',
    title='Quantidade de Vendas Mensal'
)
fig_qtd_vendas_mensal.update_layout(yaxis_title='Qtd. vendas')


## 4 Receita mensal
fig_receita_mensal = px.line(
    receita_mensal,
    x='Mes',
    y='Preço',
    markers=True,
    color='Ano',
    line_dash='Ano',
    line_shape='spline',
    title='Receita Mensal'
)
fig_receita_mensal.update_layout(yaxis_title='Receita')

## 5 Top estados por receita
fig_receita_estados = px.bar(
    receita_estados.head(),
    x='Local da compra',
    y='Preço',
    text_auto=True,
    title='Top Estados (Receita)'
)
fig_receita_estados.update_layout(yaxis_title='Receita')

## 6 Receita por categoria
fig_receita_categorias = px.bar(
    receita_por_categoria,
    x='Categoria do Produto',
    y='Preço',
    text_auto=True,
    title='Receita por Categoria'
)
fig_receita_categorias.update_layout(yaxis_title='Receita')

## 37 Quantidade de vendas por categoria
fig_qtd_vendas_categoria = px.bar(
    quantidade_vendas_categoria,
    x='Categoria do Produto',
    y='quantidade',
    text_auto= True,
    title='Quantidade de Vendas por Categoria'
)
fig_qtd_vendas_categoria.update_layout(yaxis_title='Qtd. vendas')




# -----------------------------
# INTERFACE STREAMLIT
# -----------------------------
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

# Aba 1 - Receita
with aba1:
    st.header("Receita Geral 💰")
    col1, col2 = st.columns(2)

    col1.metric("Receita Total R$", formatar_valores(receita_total))
    col1.plotly_chart(fig_mapa_receita, use_container_width=True)
    col1.plotly_chart(fig_receita_estados, use_container_width=True)

    col2.metric("Quantidade Total de Produtos", formatar_valores(quantidade_total))
    col2.plotly_chart(fig_receita_mensal, use_container_width=True)
    col2.plotly_chart(fig_receita_categorias, use_container_width=True)



# Aba 2 - Quantidade de Vendas
with aba2:
    st.header("Distribuição das Vendas 📊")
    col1, col2 = st.columns(2)
    col1.metric("Receita Total R$", formatar_valores(receita_total))
    col1.plotly_chart(fig_qtd_vendas_mensal, use_container_width= True)
    top_estados = quantidade_vendas_estado.head(5)
    
    #Quantidade de Vendas por estado
    fig_top_quantidade_estados=px.bar(
        top_estados,
        x='Local da compra',
        y='quatidade_vendas',
        text_auto=True,
        title=f'Top 5 Estados Qtd Vendas'
    )
    fig_top_quantidade_estados.update_layout(yaxis_title='Qtd. vendas')
    col1.plotly_chart(fig_top_quantidade_estados, use_container_width=True)   

    col2.metric("Quantidade Total de Produtos", formatar_valores(quantidade_total))
    col2.plotly_chart(fig_mapa_qtd_vendas,use_container_width=True)
    col2.plotly_chart(fig_qtd_vendas_categoria, use_container_width=True)  



# Aba 3 - Vendedores
with aba3:
    st.header("Distribuição das Vendas por Vendedor 📊")
    qtd_vendedores = st.number_input("Quantidade de Vendedores", 2, 10, 5)
    col1, col2 = st.columns(2)

    ## Receita por vendedor
    top_vendedores = receita_por_vendedor.head(qtd_vendedores)
    fig_receita_por_vendedor = px.bar(
        top_vendedores,
        x='total',
        y=top_vendedores.index,
        text_auto=True,
        title=f'Top {qtd_vendedores} Vendedores (Receita R$)'
    )
    fig_receita_por_vendedor.update_layout(yaxis_title='Vendedor', xaxis_title='Receita')

    col1.metric("Receita Total R$", formatar_valores(receita_total))
    col1.plotly_chart(fig_receita_por_vendedor, use_container_width=True)

    col2.metric("Quantidade Total de Produtos", formatar_valores(quantidade_total))

     ## Qtd vendas por vendedor
    fig_qtd_vendas_por_vendedor = px.bar(
        top_vendedores,
        x='quantidade',
        y=top_vendedores.index,
        text_auto=True,
        title=f'Top {qtd_vendedores} Vendedores (Produtos Vendidos)'
    )
    fig_qtd_vendas_por_vendedor.update_layout(yaxis_title='Vendedor', xaxis_title='Receita')
    col2.plotly_chart(fig_qtd_vendas_por_vendedor, use_container_width=True)



