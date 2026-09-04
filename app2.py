import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Atacadão Inteligente")

# --- BANCO DENTRO DO STREAMLIT ---
@st.cache_resource
def get_db():
    conn = sqlite3.connect('atacadao.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY AUTOINCREMENT, cpf TEXT, inicio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS carrinho (sessao_id INTEGER, produto TEXT, preco REAL, ean TEXT)')
    return conn

conn = get_db()

# --- ESTADO QUE NÃO PERDE NO RELOAD ---
if 'sessao_id' not in st.session_state:
    st.session_state.sessao_id = None
if 'cpf' not in st.session_state:
    st.session_state.cpf = ""

st.title("🛒 Atacadão")

# --- TOPO COM CPF ---
cpf = st.text_input("CPF Cliente:", value=st.session_state.cpf, placeholder="11 dígitos")

if st.button("Iniciar / Continuar Compra") and cpf:
    cur = conn.cursor()
    # se já tem sessão, só atualiza CPF
    if st.session_state.sessao_id is None:
        cur.execute("INSERT INTO sessoes (cpf, inicio) VALUES (?,?)", (cpf, datetime.now().isoformat()))
        st.session_state.sessao_id = cur.lastrowid
    st.session_state.cpf = cpf
    conn.commit()
    st.success(f"Sessão {st.session_state.sessao_id} ativa")

# --- SE TEM SESSÃO, MOSTRA PRODUTOS ---
if st.session_state.sessao_id:
    st.divider()
    st.write(f"**Cliente:** {st.session_state.cpf} | **Sessão:** {st.session_state.sessao_id}")

    produtos = [
        {"nome":"Ketchup Quero 400g","preco":8.90,"ean":"7896004700014","yolo":["bottle"]},
        {"nome":"Óleo Soya 900ml","preco":6.90,"ean":"7892300000014","yolo":["bottle"]},
        {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481","yolo":["bottle","cup"]},
        {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517","yolo":["bottle"]},
    ]

    for p in produtos:
        if st.button(f"Adicionar {p['nome']} - R$ {p['preco']}", key=p['ean']):
            conn.execute("INSERT INTO carrinho VALUES (?,?,?,?)", (st.session_state.sessao_id, p['nome'], p['preco'], p['ean']))
            conn.commit()
            st.toast("Adicionado!")

    # MOSTRA CESTA ATUAL
    st.divider()
    cur = conn.cursor()
    cur.execute("SELECT produto, preco FROM carrinho WHERE sessao_id=?", (st.session_state.sessao_id,))
    itens = cur.fetchall()
    if itens:
        st.subheader(f"Cesta ({len(itens)} itens)")
        total = sum([i[1] for i in itens])
        for nome, preco in itens:
            st.write(f"- {nome}: R$ {preco}")
        st.metric("Total", f"R$ {total:.2f}")
