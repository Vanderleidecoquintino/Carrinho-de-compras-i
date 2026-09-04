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
    return YOLO("yolo11n.pt")

model = load_model()

produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015","yolo":["bottle"]},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517","yolo":["bottle"]},
    {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481","yolo":["bottle","cup"]},
    {"nome":"Requeijão Canto Minas 400g","preco":13.90,"ean":"7896908200015","yolo":["bottle","cup","bowl"]},
    {"nome":"Óleo Soya 900ml","preco":6.90,"ean":"7892300000014","yolo":["bottle"]},
    {"nome":"Ketchup Quero 400g","preco":8.90,"ean":"7896004700014","yolo":["bottle"]},
    {"nome":"Limpador Limpol 500ml","preco":2.99,"ean":"7896039710015","yolo":["bottle"]},
    {"nome":"Energético Baly 473ml","preco":5.49,"ean":"7898915120040","yolo":["bottle","can"]},
    {"nome":"[BULNEZ] Macarrão 500g","preco":2.99,"ean":"7898915120022","yolo":["box","book"]},
    {"nome":"[BULNEZ] Massa Fresca 500g","preco":7.90,"ean":"7898915120050","yolo":["box","bowl"]},
    {"nome":"[BULNEZ] Tortilha 400g","preco":8.50,"ean":"7898915120060","yolo":["box"]},
    {"nome":"Arroz Tio João 5kg","preco":27.90,"ean":"7893500010001","yolo":["box","book"]},
    {"nome":"Biscoito Vitarella 350g","preco":4.99,"ean":"7896004000010","yolo":["box","book"]},
    {"nome":"Café Bom Jesus 250g","preco":12.98,"ean":"7896045500012","yolo":["box","cup"]},
    {"nome":"Chocolate Harald 500g","preco":59.90,"ean":"7896063800011","yolo":["box","book"]},
    {"nome":"Suco Subello 200ml","preco":1.49,"ean":"7898951000015","yolo":["box"]},
    {"nome":"[BULNEZ] Esponja 3un","preco":2.49,"ean":"7898915120039","yolo":["box"]},
    {"nome":"Feijão Kicaldo 1kg","preco":7.50,"ean":"7896101000013","yolo":["box","book"]},
]

foto = st.camera_input("📸 Aponte pro produto e bipa")

if foto:
    img = Image.open(foto)
    res = model(img, verbose=False, conf=0.4)
    visto = set(model.names[int(b.cls)] for r in res for b in r.boxes) if res[0].boxes else set()
    if visto:
        st.success(f"BIP! Detectei: {', '.join(visto)}")
        sugestoes = [p for p in produtos if any(v in p['yolo'] for v in visto)]
        if not sugestoes: sugestoes = produtos[:8]
        cols = st.columns(2)
        for i,p in enumerate(sugestoes[:8]):
            with cols[i%2]:
                if st.button(f"➕ {p['ean'][-4:]} | {p['nome'][:20]}", key=f"s{i}_{p['ean']}"):
                    st.session_state.carrinho.append(p)
                    conn.execute("INSERT INTO carrinho VALUES (?,?,?,?)", (st.session_state.sessao_id, p['nome'], p['preco'],
