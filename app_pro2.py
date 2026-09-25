import streamlit as st
from ultralytics import YOLO
from PIL import Image
import random, os, json
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒", layout="centered")
st.markdown("<style>#MainMenu, footer, header {visibility:hidden}</style>", unsafe_allow_html=True)

if "cpf" not in st.session_state: st.session_state.cpf=None
if "carrinho" not in st.session_state: st.session_state.carrinho={}

if not st.session_state.cpf:
    st.title("🛒 CLIENTE ATACADÃO")
    cpf=st.text_input("CPF 11 números", max_chars=11)
    if st.button("ENTRAR", type="primary", use_container_width=True):
        if len(cpf)==11 and cpf.isdigit():
            st.session_state.cpf=cpf
            if os.path.exists(f"cesta_{cpf}.json"):
                with open(f"cesta_{cpf}.json","r") as f: st.session_state.carrinho=json.load(f)
            st.rerun()
    st.stop()

cpf=st.session_state.cpf
def salvar():
    with open(f"cesta_{cpf}.json","w") as f: json.dump(st.session_state.carrinho,f)
def add_produto(p):
    ean=p['ean']
    if ean in st.session_state.carrinho: st.session_state.carrinho[ean]['qtd']+=1
    else: st.session_state.carrinho[ean]={"dados":p,"qtd":1}
    salvar()

@st.cache_resource
def load_model(): return YOLO("best.pt")
model=load_model()

produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015"},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517"},
    {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481"},
    {"nome":"Requeijão Canto Minas 400g","preco":13.90,"ean":"7896908200015"},
    {"nome":"Óleo Soya 900ml","preco":6.90,"ean":"7892300000014"},
    {"nome":"Ketchup Quero 400g","preco":8.90,"ean":"7896004700014"},
    {"nome":"Limpador Limpol 500ml","preco":2.99,"ean":"7896039710015"},
    {"nome":"Energético Baly 473ml","preco":5.49,"ean":"7898915120040"},
    {"nome":"[BULNEZ] Macarrão 500g","preco":2.99,"ean":"7898915120022"},
    {"nome":"[BULNEZ] Massa Fresca 500g","preco":7.90,"ean":"7898915120050"},
    {"nome":"[BULNEZ] Tortilha 400g","preco":8.50,"ean":"7898915120060"},
    {"nome":"Arroz Tio João 5kg","preco":27.90,"ean":"7893500010001"},
    {"nome":"Biscoito Vitarella 350g","preco":4.99,"ean":"7896004000010"},
    {"nome":"Café Bom Jesus 250g","preco":12.98,"ean":"7896045500012"},
    {"nome":"Chocolate Harald 500g","preco":59.90,"ean":"7896063800011"},
    {"nome":"Suco Subello 200ml","preco":1.49,"ean":"7898951000015"},
    {"nome":"[BULNEZ] Esponja 3un","preco":2.49,"ean":"7898915120039"},
    {"nome":"Feijão Kicaldo 1kg","preco":7.50,"ean":"7896101000013"},
]

st.title("🛒 CLIENTE ATACADÃO")
if st.button("Sair"): st.session_state.cpf=None; st.rerun()

st.subheader("📸 Bipar com câmera que vira")
components.html("""
<div style="text-align:center; font-family:sans-serif">
  <video id="video" autoplay playsinline style="width:100%; max-height:320px; border-radius:12px; background:black; object-fit:cover"></video>
  <div style="margin-top:10px">
    <button id="flip" style="padding:12px 18px; background:#ff6b00; color:white; border:none; border
