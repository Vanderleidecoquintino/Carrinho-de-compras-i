import streamlit as st
from ultralytics import YOLO
from PIL import Image
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Atacadao", page_icon="🛒")

@st.cache_resource
def get_db():
    c = sqlite3.connect('atacadao.db', check_same_thread=False)
    c.execute('CREATE TABLE IF NOT EXISTS carrinho (sessao INTEGER, nome TEXT, preco REAL, ean TEXT)')
    return c
conn = get_db()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt")
model = load_model()

produtos = [
    {"nome":"Agua 500ml","preco":1.29,"ean":"7898915120015"},
    {"nome":"Coca 2L","preco":9.50,"ean":"7894900011517"},
    {"nome":"Arroz 5kg","preco":27.90,"ean":"7893500010001"},
    {"nome":"Feijao 1kg","preco":7.50,"ean":"7896101000013"},
    {"nome":"Oleo 900ml","preco":6.90,"ean":"7892300000014"},
    {"nome":"Macarrao 500g","preco":2.99,"ean":"7898915120022"},
]

st.title("🛒 ATACADAO - BIP")

foto = st.camera_input("Bipa o produto")

if foto:
    img = Image.open(foto)
    img.thumbnail((320, 320))
    r = model(img, verbose=False, conf=0.4)
    det = []
    if r[0].boxes:
        det = [model.names[int(b.cls)] for b in r[0].boxes]
    if det:
        st.success(f"Vi: {', '.join(det)}")

st.divider()
op = st.selectbox("Produto:", [f"{p['ean']} - {p['nome']} - R$ {p['preco']}" for p in produtos])
p_sel = produtos[[f"{p['ean']} - {p['nome']} - R$ {p['preco']}" for p in produtos].index(op)]

if st.button("ADICIONAR", use_container_width=True):
    st.session_state.carrinho.append(p_sel)
    conn.execute("INSERT INTO carrinho VALUES (?,?,?,?)", (1, p_sel['nome'], p_sel['preco'], p_sel['ean']))
    conn.commit()
    st.toast("Adicionado!")
    st.rerun()

if st.button("Limpar carrinho"):
    st.session_state.carrinho = []
    conn.execute("DELETE FROM carrinho WHERE sessao=1")
    conn.commit()
    st.rerun()

total = sum(x['preco'] for x in st.session_state.carrinho)
st.subheader(f"Itens: {len(st.session_state.carrinho)} - Total R$ {total:.2f}")
for i in st.session_state.carrinho:
    st.write(f"- {i['nome']} R$ {i['preco']}")
