import streamlit as st
from ultralytics import YOLO
from PIL import Image
import random
from io import BytesIO
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
h2, h3 { color: #000000!important; }
p, span, label, div[data-testid="stMarkdownContainer"] p { color: #000000!important; font-weight: 600!important; }
.stButton > button { background: #FF6600; color: white; border-radius: 12px; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db():
    conn = sqlite3.connect('atacadao.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY AUTOINCREMENT, cpf TEXT, inicio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS carrinho (sessao_id INTEGER, produto TEXT, preco REAL, ean TEXT)')
    return conn
conn = get_db()

if 'sessao_id' not in st.session_state:
    st.session_state.sessao_id = None
if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]
if 'cpf' not in st.session_state:
    st.session_state.cpf = ""

st.title("🛒 CLIENTE ATACADÃO")
cpf = st.text_input("CPF Cliente:", value=st.session_state.cpf, placeholder="11 dígitos")

if st.button("Iniciar Compra") and cpf:
    cur = conn.cursor()
    cur.execute("INSERT INTO sessoes (cpf, inicio) VALUES (?,?)", (cpf, datetime.now().isoformat()))
    st.session_state.sessao_id = cur.lastrowid
    st.session_state.cpf = cpf
    conn.commit()
    st.rerun()

if not st.session_state.sessao_id:
    st.warning("Digite o CPF e inicie a compra")
    st.stop()

st.info(f"Cliente: {st.session_state.cpf} | Sessão: {st.session_state.sessao_id}")

@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt") # CORRIGIDO: n = nano, leve pro cloud

model = load_model()

produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015","yolo":["bottle"]},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517","yolo":["bottle"]},
    {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481","yolo":["bottle","cup"]},
    {"nome":"Requeijão Canto
