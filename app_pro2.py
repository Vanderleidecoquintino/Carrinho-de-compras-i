import streamlit as st
from ultralytics import YOLO
from PIL import Image
import random, os, json
from io import BytesIO

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- 1. CPF LOGIN ---
if "cpf" not in st.session_state:
    st.session_state.cpf = None
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

if not st.session_state.cpf:
    st.title("🛒 CLIENTE ATACADÃO")
    cpf = st.text_input("CPF (11 números)", max_chars=11)
    if st.button("ENTRAR", type="primary", use_container_width=True):
        if len(cpf)==11 and cpf.isdigit():
            st.session_state.cpf = cpf
            st.rerun()
        else:
            st.error("CPF inválido, 11 números")
    st.stop()

cpf = st.session_state.cpf

def add_produto(p):
    ean = p['ean']
    if ean in st.session_state.carrinho:
        st.session_state.carrinho[ean]['qtd'] += 1
    else:
        st.session_state.carrinho[ean] = {"dados": p, "qtd": 1}
    st.toast(f"BIP! {p['nome'][:25]} adicionado")

@st.cache_resource
def load_model():
    # Já deixa pronto pra YOLO27: é só trocar aqui
    return YOLO("yolo26n.pt") # antes tava yolo11m.pt que é muito pesado

model = load_model()

produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015","yolo":["bottle"]},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517","yolo":["bottle"]},
    {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481","yolo":["bottle","cup"]},
    #... seus outros produtos
]

# TOPO
col1, col2 = st.columns([3,1])
with col1: st.title("🛒 CLIENTE ATACADÃO")
with col2:
    st.write(f"CPF: **{cpf}**")
    if st.button("Sair"):
        st.session_state.cpf=None
        st.session_state.carrinho={}
        st.rerun()

foto = st.camera_input("📸 Aponte pro produto e bipa")

if foto:
    img = Image.open(foto).convert("RGB")
    res = model(img, verbose=False, conf=0.4)
    visto = set(model.names[int(b.cls)] for r in res for b in r.boxes) if res[0].boxes else set()
    if visto:
        st.success(f"BIP! Detectei: {', '.join(visto)}")
        sugestoes = [p for p in produtos if any(v in p['yolo'] for v in visto)]
        if not sugestoes: sugestoes = produtos[:8]
        cols = st.columns(2)
        for i,p in enumerate(sugestoes[:8]):
            with cols[i%2]:
                if st.button(f"➕ {p['nome'][:22]}", key=f"s{i}_{p['ean']}"):
                    add_produto(p)
                    st.rerun()
    else:
        st.warning("Não detectei - use a lista abaixo")
