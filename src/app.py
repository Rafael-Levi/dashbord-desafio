import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Buscar variáveis de ambiente
SHEET_ID = st.secrets["SHEET_ID"]
EXCEL_URL = st.secrets["EXCEL_URL"]


response = requests.get(EXCEL_URL)
response.raise_for_status()  

excel_file = BytesIO(response.content)

df_resumo = pd.read_excel(excel_file, sheet_name="Resumo Executivo", engine="openpyxl")
df_analise = pd.read_excel(excel_file, sheet_name="Análise CH por Escola", engine="openpyxl")


st.set_page_config(page_title="Dashboard CH - TOM", layout="wide")
st.title("📊 Dashboard Interativo - Repasse de Carga Horária")


st.sidebar.header("Filtros")
meses = st.sidebar.multiselect("Selecione o(s) mes(es):", options=df_resumo["Meses"].unique(), default=df_resumo["Meses"].unique())
escolas = st.sidebar.multiselect("Selecione a(s) escola(s):", options=df_analise["Escola"].unique(), default=df_analise["Escola"].unique())


df_resumo_f = df_resumo[df_resumo["Meses"].isin(meses)]
df_analise_f = df_analise[df_analise["Escola"].isin(escolas)]


for col in df_resumo.columns:
    if df_resumo[col].dtype == "object":
        df_resumo[col] = pd.to_numeric(df_resumo[col].astype(str).str.replace(",", "."), errors="ignore")

for col in df_analise.columns:
    if df_analise[col].dtype == "object":
        df_analise[col] = pd.to_numeric(df_analise[col].astype(str).str.replace(",", "."), errors="ignore")


st.subheader("Comparação VR2 - CH Pago TOM vs CH Contratada Governo")


df_vr2 = df_resumo_f.melt(id_vars=["Meses"], 
                          value_vars=["*CH Pago Tom (Conversão Gov)", "CH Contratada Gov"],
                          var_name="Fonte", value_name="Carga Horária")

fig1 = px.bar(df_vr2, x="Meses", y="Carga Horária", color="Fonte",
              barmode="group", title="CH Pago (Conversão Gov) vs CH Contratada (Gov)",
              labels={"Carga Horária": "Carga Horária (h)", "Meses": "Mês"})
st.plotly_chart(fig1, use_container_width=True)


fig2 = px.line(df_resumo_f, x="Meses", y="% Divergência", markers=True,
               title="% Divergência por Mês (VR2)",
               labels={"% Divergência": "% Divergência", "Meses": "Mês"})
st.plotly_chart(fig2, use_container_width=True)


st.subheader("Análise de CH por Escola (Regência e Não Regência)")


df_escola = df_analise_f.groupby("Escola", as_index=False).agg({
    "CH Regência": "sum",
    "CH Sem Regência": "sum",
    "Valor CH Mensal": "sum"
})

fig3 = px.bar(df_escola, x="Escola", y=["CH Regência", "CH Sem Regência"],
              barmode="stack", title="Distribuição de Carga Horária por Escola",
              labels={"value": "Carga Horária", "variable": "Categoria"})
st.plotly_chart(fig3, use_container_width=True)


fig4 = px.bar(df_escola, x="Escola", y="Valor CH Mensal",
              title="Valor Total (R$) de Carga Horária por Escola",
              labels={"Valor CH Mensal": "Valor Total (R$)"})
st.plotly_chart(fig4, use_container_width=True)


st.subheader("📄 Dados Detalhados")
with st.expander("Ver Resumo Executivo"):
    st.dataframe(df_resumo_f)

with st.expander("Ver Análise CH por Escola"):
    st.dataframe(df_analise_f)
