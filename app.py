import os
import streamlit as st
import pandas as pd
import plotly.express as px

PASTA_DADOS = r"C:/Users/User/Desktop/Automação do trabalho/Bash do trabalho/Logistica reversa"

if not os.path.exists(PASTA_DADOS):
    os.makedirs(PASTA_DADOS)

st.set_page_config(
    page_title="Portal de Logística Reversa",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Portal de Logística Reversa - Central de Arquivos")
st.caption(f"Lendo automaticamente os arquivos da pasta: `{PASTA_DADOS}`")
st.markdown("---")

arquivos_disponiveis = [
    f for f in os.listdir(PASTA_DADOS) 
    if f.endswith(('.xlsx', '.xls', '.xlsm','csv'))
]

st.sidebar.header("📁 Seleção de Arquivos")

if arquivos_disponiveis:
    arquivo_selecionado = st.sidebar.selectbox(
        "Selecione um arquivo da pasta:",
        arquivos_disponiveis
    )
    
    caminho_completo = os.path.join(PASTA_DADOS, arquivo_selecionado)
    
    df = None
    if arquivo_selecionado.endswith(('.xlsx', '.xls', '.xlsm','csv')):
        xls = pd.ExcelFile(caminho_completo)
        aba_selecionada = st.sidebar.selectbox("Selecione a Aba (Sheet):", xls.sheet_names)
        df = pd.read_excel(caminho_completo, sheet_name=aba_selecionada)
        nome_exibicao = f"{arquivo_selecionado} 👉 [{aba_selecionada}]"
    else:
        df = pd.read_csv(caminho_completo)
        nome_exibicao = arquivo_selecionado

   
    if st.sidebar.button("🔄 Atualizar Lista de Arquivos"):
        st.rerun()

    st.success(f"📊 **Arquivo Aberto:** `{nome_exibicao}`")


    col1, col2, col3 = st.columns(3)
    col1.metric("Linhas (Registros)", len(df))
    col2.metric("Colunas", len(df.columns))
    
    colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
    colunas_texto = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if colunas_numericas:
        soma = df[colunas_numericas[0]].sum()
        col3.metric(f"Total de {colunas_numericas[0]}", f"{soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    
    st.header("📈 Indicadores do Arquivo")
    
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        st.subheader("Gráfico de Barras")
        if colunas_texto and colunas_numericas:
            eixo_x = st.selectbox("Eixo X (Categoria):", colunas_texto, index=0, key="x1")
            eixo_y = st.selectbox("Eixo Y (Valor/Qtd):", colunas_numericas, index=0, key="y1")

            df_grouped = df.groupby(eixo_x)[eixo_y].sum().reset_index().sort_values(by=eixo_y, ascending=False).head(10)

            fig1 = px.bar(
                df_grouped, x=eixo_x, y=eixo_y, text=eixo_y, 
                title=f"Top 10 - {eixo_y} por {eixo_x}",
                color=eixo_y, color_continuous_scale="Blues"
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("O arquivo precisa ter colunas de texto e de números para gerar o gráfico.")

    with g_col2:
        st.subheader("Gráfico de Pizza / Proporção")
        if colunas_texto and colunas_numericas:
            eixo_pizza = st.selectbox("Categoria:", colunas_texto, index=min(1, len(colunas_texto)-1), key="p1")
            valor_pizza = st.selectbox("Valor:", colunas_numericas, index=0, key="p2")

            df_pie = df.groupby(eixo_pizza)[valor_pizza].sum().reset_index()
            fig2 = px.pie(df_pie, names=eixo_pizza, values=valor_pizza, title=f"Distribuição de {valor_pizza}", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
   
    st.header("📋 Visualização dos Dados Brutos")
    st.dataframe(df, use_container_width=True)

else:
    st.warning(f" Nenhuma planilha foi encontrada na pasta `{PASTA_DADOS}`.")
    st.info(" Coloque suas planilhas de Logística Reversa (.xlsx) dentro da pasta para que apareçam aqui automaticamente.")
    