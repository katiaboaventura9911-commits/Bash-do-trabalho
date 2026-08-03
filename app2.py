import os
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

PASTA_DADOS = "./Logistica-Reversa"

# Configuração da página
st.set_page_config(
    page_title="Portal de Logística Reversa",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Portal de Logística Reversa - Central de Arquivos")
st.caption("Varredura automática e geração de dashboards a partir de planilhas Excel e arquivos CSV.")
st.markdown("---")

# Verifica se a pasta existe
pasta_path = Path(PASTA_DADOS)

# Feedback sobre a existência da pasta
st.sidebar.header("📁 Configurações da Pasta")
st.sidebar.write(f"**Caminho completo da pasta:**  \n`{PASTA_DADOS}`")

if pasta_path.exists() and pasta_path.is_dir():
    st.sidebar.success(f"✅ Pasta conectada:\n`{pasta_path.absolute()}`")
else:
    st.sidebar.error(f"❌ Pasta não encontrada:\n`{pasta_path.absolute()}`")
    # Tenta criar a pasta local
    pasta_path.mkdir(parents=True, exist_ok=True)
    st.sidebar.info("📁 A pasta './dados' foi criada automaticamente no seu projeto.")

# ---------------------------------------------------------
# DETECÇÃO DE ARQUIVOS EXCEL E CSV
# ---------------------------------------------------------
lista_arquivos = []

if pasta_path.exists():
    # Varre a pasta e subpastas procurando por extensão .xlsx, .xls ou .csv
    # Ignora arquivos temporários do Excel (que começam com ~$ )
    for arquivo in pasta_path.rglob("*"):
        if arquivo.is_file() and arquivo.suffix.lower() in [".xlsx", ".xls", ".csv", ".xlsm"] and not arquivo.name.startswith("~$"):
            # Adiciona o arquivo à lista com o caminho relativo
            caminho_relativo = arquivo.relative_to(pasta_path)
            lista_arquivos.append((str(caminho_relativo), arquivo))

st.sidebar.markdown("---")
st.sidebar.header("📁 Seleção de Arquivo")

if lista_arquivos:
    # Cria o menu suspenso ordenado pelo nome dos arquivos
    opcoes = [item[0] for item in lista_arquivos]
    arquivo_escolhido_rel = st.sidebar.selectbox(
        f"Selecione um arquivo ({len(lista_arquivos)} encontrados):",
        opcoes
    )

    # Recupera o caminho real do arquivo selecionado
    caminho_arquivo_real = dict(lista_arquivos)[arquivo_escolhido_rel]

    # ---------------------------------------------------------
    # LEITURA DO ARQUIVO (EXCEL OU CSV) E NAVEGAÇÃO
    # ---------------------------------------------------------
    df = None
    extensao = caminho_arquivo_real.suffix.lower()

    try:
        # Se for Excel, permite escolher qual Aba (Sheet) abrir
        if extensao in [".xlsx", ".xls", ".xlsm"]:
            xls = pd.ExcelFile(caminho_arquivo_real)
            sheet_names = xls.sheet_names
            
            aba_selecionada = st.sidebar.selectbox("Selecione a Aba (Sheet):", sheet_names)
            df = pd.read_excel(caminho_arquivo_real, sheet_name=aba_selecionada)
            nome_exibicao = f"{arquivo_escolhido_rel} ➡️ Aba: [{aba_selecionada}]"

        # Se for CSV
        elif extensao == ".csv":
            # Tenta ler com UTF-8 ou ISO-8859-1 (comum em Excel em português)
            try:
                df = pd.read_csv(caminho_arquivo_real, sep=None, engine='python')
            except Exception:
                df = pd.read_csv(caminho_arquivo_real, encoding="latin1", sep=";")
            
            nome_exibicao = f"{arquivo_escolhido_rel} (Arquivo CSV)"

        # ---------------------------------------------------------
        # DASHBOARD AUTOMÁTICO
        # ---------------------------------------------------------
        if df is not None:
            st.success(f"📊 **Arquivo Selecionado:** `{nome_exibicao}`")

            # Métrica rápida
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Linhas", f"{len(df):,}".replace(",", "."))
            col2.metric("Total de Colunas", len(df.columns))

            colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
            colunas_texto = df.select_dtypes(include=['object', 'category']).columns.tolist()

            if colunas_numericas:
                soma = df[colunas_numericas[0]].sum()
                col3.metric(f"Soma Total de ({colunas_numericas[0]})", f"{soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.markdown("---")

            # Gráficos Dinâmicos
            st.header("📈 Dashboard de Indicadores")
            g_col1, g_col2 = st.columns(2)

            with g_col1:
                st.subheader("Gráfico de Barras")
                if colunas_texto and colunas_numericas:
                    eixo_x = st.selectbox("Eixo X (Categoria):", colunas_texto, index=0, key="x1")
                    eixo_y = st.selectbox("Eixo Y (Valores/Qtd):", colunas_numericas, index=0, key="y1")

                    df_grouped = df.groupby(eixo_x)[eixo_y].sum().reset_index().sort_values(by=eixo_y, ascending=False).head(10)
                    fig1 = px.bar(df_grouped, x=eixo_x, y=eixo_y, text=eixo_y, color=eixo_y, color_continuous_scale="Blues")
                    fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("Para visualização em gráfico de barras, a planilha precisa de ao menos uma coluna de texto e uma numérica.")

            with g_col2:
                st.subheader("Gráfico de Proporção (Pizza)")
                if colunas_texto and colunas_numericas:
                    eixo_pizza = st.selectbox("Categoria:", colunas_texto, index=min(1, len(colunas_texto)-1), key="p1")
                    valor_pizza = st.selectbox("Valor:", colunas_numericas, index=0, key="p2")

                    df_pie = df.groupby(eixo_pizza)[valor_pizza].sum().reset_index()
                    fig2 = px.pie(df_pie, names=eixo_pizza, values=valor_pizza, hole=0.4)
                    fig2.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Para visualização em gráfico de pizza, a planilha precisa de ao menos uma coluna de texto e uma numérica.")

            st.markdown("---")

            # Exibição dos Dados Brutos
            st.header("📋 Visualização dos Dados da Planilha")
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erro ao abrir o arquivo: {e}")

else:
    st.warning("⚠️ Nenhum arquivo Excel (.xlsx, .xls) ou CSV foi localizado no diretório.")
    st.info(f"💡 **Dica:** Coloque seus arquivos na pasta `{PASTA_DADOS}` para que apareçam aqui automaticamente.")