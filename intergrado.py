import streamlit as st
import sqlite3
import pandas as pd
import os

# --- Criação do banco e dados de teste ---
def criar_banco_e_inserir_dados():
    if not os.path.exists("biblioteca.db"):
        conn = sqlite3.connect("biblioteca.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_usuario TEXT NOT NULL,
            codigo_livro TEXT NOT NULL,
            titulo_livro TEXT NOT NULL,
            data_emprestimo TEXT NOT NULL,
            data_devolucao TEXT,
            status TEXT NOT NULL,
            multa REAL DEFAULT 0
        )
        """)

        dados = [
            ("Ana Paula", "L001", "O senhor dos Anéis - A sociedade do Anel", "2024-04-01", "2024-04-15", "Devolvido", 0.0),
            ("Carlos Silva", "L002", "Harry Potter e a Pedra Filosofal", "2024-04-10", None, "Em aberto", 0.0),
            ("João Souza", "L003", "Hábitos Atômicos", "2024-03-15", "2024-04-20", "Multa", 12.5),
            ("Marina Rocha", "L004", "Dom Quixote", "2024-04-05", "2024-04-22", "Devolvido", 0.0),
        ]

        cursor.executemany("""
        INSERT INTO emprestimos (nome_usuario, codigo_livro, titulo_livro, data_emprestimo, data_devolucao, status, multa)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, dados)

        conn.commit()
        conn.close()

# --- Conexão com o banco ---
def conectar_bd():
    return sqlite3.connect("biblioteca.db")

# --- Consulta de empréstimos ---
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

# --- INÍCIO DO APP ---
criar_banco_e_inserir_dados()

# --- INTERFACE ---
st.title("📚 Sistema da Biblioteca")

st.markdown("Filtre os acertos por usuário, código do livro ou status:")

nome_usuario = st.text_input("🔍 Nome do usuário")
codigo_livro = st.text_input("📕 Código do livro")
status = st.selectbox("📌 Status do empréstimo", ["Todos", "Em aberto", "Devolvido", "Multa"])

if st.button("Consultar Empréstimos"):
    dados = consultar_acertos(nome_usuario, codigo_livro, status)

    if dados:
        df = pd.DataFrame(dados, columns=["Usuário", "Código do Livro", "Título", "Data Empréstimo", "Data Devolução", "Status", "Multa"])
        st.success(f"{len(df)} resultado(s) encontrado(s).")
        st.dataframe(df)
    else:
        st.warning("Nenhum resultado encontrado com os filtros fornecidos.")
