import streamlit as st
import sqlite3
import pandas as pd
import requests

# --- Conexão com o banco de dados ---
def conectar_bd():
    return sqlite3.connect("biblioteca.db")

# --- Consulta de empréstimos no banco ---
def consultar_acertos(nome_usuario, codigo_livro, status):
    conn = conectar_bd()
    cursor = conn.cursor()

    query = "SELECT nome_usuario, codigo_livro, titulo_livro, data_emprestimo, data_devolucao, status, multa FROM emprestimos WHERE 1=1"
    params = []

    if nome_usuario:
        query += " AND nome_usuario LIKE ?"
        params.append(f"%{nome_usuario}%")
    
    if codigo_livro:
        query += " AND codigo_livro LIKE ?"
        params.append(f"%{codigo_livro}%")
    
    if status != "Todos":
        query += " AND status = ?"
        params.append(status)

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    
    return resultados

# --- Consulta de livros da API ---
def consultar_livros_api():
    try:
        resposta = requests.get("http://localhost:5000/Livros")
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return []
    except Exception as e:
        st.error(f"Erro ao consultar API: {e}")
        return []

# --- INTERFACE ---
st.title("📚 Sistema da Biblioteca")

st.markdown("Filtre os acertos por usuário, código do livro ou status:")

# Filtros
nome_usuario = st.text_input("🔍 Nome do usuário")
codigo_livro = st.text_input("📕 Código do livro")
status = st.selectbox("📌 Status do empréstimo", ["Todos", "Em aberto", "Devolvido", "Multa"])

# Botão para consultar empréstimos
if st.button("Consultar Empréstimos"):
    dados = consultar_acertos(nome_usuario, codigo_livro, status)

    if dados:
        df = pd.DataFrame(dados, columns=["Usuário", "Código do Livro", "Título", "Data Empréstimo", "Data Devolução", "Status", "Multa"])
        st.success(f"{len(df)} resultado(s) encontrado(s).")
        st.dataframe(df)
    else:
        st.warning("Nenhum resultado encontrado com os filtros fornecidos.")

# --- Nova seção para mostrar livros disponíveis ---
st.markdown("---")
st.header("📖 Livros disponíveis na Biblioteca (via API)")

livros = consultar_livros_api()

if livros:
    df_livros = pd.DataFrame(livros)
    st.dataframe(df_livros)
else:
    st.info("Nenhum livro encontrado ou API indisponível.")
