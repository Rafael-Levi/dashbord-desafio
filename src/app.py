import streamlit as st
import pandas as pd
import plotly.express as px

# --- Carregar os dados ---
file_path = "../assets/dados.xlsx"

df_resumo = pd.read_excel(file_path, sheet_name="Resumo Executivo")
df_analise = pd.read_excel(file_path, sheet_name="Análise CH por Escola")

# --- Título do app ---
st.set_page_config(page_title="Dashboard CH - TOM", layout="wide")
st.title("📊 Dashboard Interativo - Repasse de Carga Horária")

# --- Filtros interativos ---
st.sidebar.header("Filtros")
meses = st.sidebar.multiselect("Selecione o(s) mes(es):", options=df_resumo["Mes"].unique(), default=df_resumo["Mes"].unique())
escolas = st.sidebar.multiselect("Selecione a(s) escola(s):", options=df_analise["Escola"].unique(), default=df_analise["Escola"].unique())

# Filtrar dados
df_resumo_f = df_resumo[df_resumo["Mes"].isin(meses)]
df_analise_f = df_analise[df_analise["Escola"].isin(escolas)]

# --- Seção 1: Comparação VR2 ---
st.subheader("Comparação VR2 - CH Pago TOM vs CH Contratada Governo")

fig1 = px.bar(df_resumo_f, x="Mes", y=["CH Pago TOM (Conversão Gov)", "CH Contratada Gov"],
              barmode="group", title="CH Pago (Conversão Gov) vs CH Contratada (Gov)",
              labels={"value": "Carga Horária", "variable": "Fonte"})
st.plotly_chart(fig1, use_container_width=True)

# Divergência em percentual
fig2 = px.line(df_resumo_f, x="Mes", y="% Divergência", markers=True,
               title="% Divergência por Mes (VR2)",
               labels={"% Divergência": "% Divergência"})
st.plotly_chart(fig2, use_container_width=True)

# --- Seção 2: Análise por Escola ---
st.subheader("Análise de CH por Escola (Regência e Não Regência)")

# Agregar os valores da análise por escola
df_escola = df_analise_f.groupby("Escola", as_index=False).agg({
    "CH Regência": "sum",
    "CH sem regência": "sum",
    "Valor CH Mensal": "sum"
})

fig3 = px.bar(df_escola, x="Escola", y=["CH Regência", "CH sem regência"],
              barmode="stack", title="Distribuição de Carga Horária por Escola",
              labels={"value": "Carga Horária", "variable": "Categoria"})
st.plotly_chart(fig3, use_container_width=True)

# Valor financeiro total
fig4 = px.bar(df_escola, x="Escola", y="Valor CH Mensal",
              title="Valor Total (R$) de Carga Horária por Escola",
              labels={"Valor CH Mensal": "Valor Total (R$)"})
st.plotly_chart(fig4, use_container_width=True)

# --- Seção 3: Tabelas Detalhadas ---
st.subheader("📄 Dados Detalhados")
with st.expander("Ver Resumo Executivo"):
    st.dataframe(df_resumo_f)

with st.expander("Ver Análise CH por Escola"):
    st.dataframe(df_analise_f)
