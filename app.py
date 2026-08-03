import os
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import os
PASTA_DADOS = "./Logistica-Reversa"
if not os.path.exists(PASTA_DADOS):
    os.makedirs(PASTA_DADOS)


# Configuração da página
st.set_page_config(
    page_title="Portal de Logística Reversa",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Portal de Logística Reversa - Central de Arquivos")
st.caption("Varredura automática e geração de dashboards a partir de planilhas Excel e arquivos CSV.")
st.markdown("---")

# ---------------------------------------------------------
# 1. CAMINHO DA PASTA ONDE FICAM OS ARQUIVOS
# ---------------------------------------------------------
# Você pode alterar a pasta padrão abaixo ou mudar pela barra lateral no navegador
PASTA_PADRAO = r"./dados"

st.sidebar.header("⚙️ Configurações da Pasta")

# Campo interativo para indicar ou trocar o caminho da pasta
caminho_digitado = st.sidebar.text_input("Caminho completo da pasta:", value=PASTA_PADRAO)
pasta_path = Path(caminho_digitado).resolve()

# Feedback sobre a existência da pasta
if pasta_path.exists() and pasta_path.is_dir():
    st.sidebar.success(f"✅ Pasta conectada:\n`{pasta_path}`")
else:
    st.sidebar.error(f"❌ Pasta não encontrada:\n`{pasta_path}`")
    # Tenta criar a pasta local caso seja a pasta padrão
    if caminho_digitado == PASTA_PADRAO:
        pasta_path.mkdir(parents=True, exist_ok=True)
        st.sidebar.info("A pasta './dados' foi criada automaticamente no seu projeto.")

# ---------------------------------------------------------
# 2. DETECÇÃO DE ARQUIVOS EXCEL E CSV
# ---------------------------------------------------------
lista_arquivos = []

if pasta_path.exists():
    # Varre a pasta e subpastas procurando por extensão .xlsx, .xls ou .csv
    # Ignora arquivos temporários do Excel (que começam com ~$ )
    for arquivo in pasta_path.rglob("*"):
        if arquivo.is_file() and arquivo.suffix.lower() in [".xlsx", ".xls", ".csv"]:
            if not arquivo.name.startswith("~$"):
                # Guarda o caminho relativo para exibição amigável
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
    # 3. LEITURA DO ARQUIVO (EXCEL OU CSV) E NAVEGAÇÃO
    # ---------------------------------------------------------
    df = None
    extensao = caminho_arquivo_real.suffix.lower()

    try:
        # Se for Excel, permite escolher qual Aba (Sheet) abrir
        if extensao in [".xlsx", ".xls"]:
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
        # 4. DASHBOARD AUTOMÁTICO
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
                    st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")

            # Exibição dos Dados Brutos
            st.header("📋 Visualização dos Dados da Planilha")
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao abrir o arquivo: {e}")

else:
    st.warning(f"⚠️ Nenhuma planilha foi encontrada na pasta `{PASTA_DADOS}`.")
    st.info("💡 **Dica:** Copie o caminho exato da pasta onde seus arquivos estão salvos e cole na caixa de texto na barra lateral esquerda.")
    st.info("Coloque suas planilhas de Logística Reversa (.xlsx) dentro da pasta para que apareçam aqui automaticamente.")

