import streamlit as st
from ultralytics import YOLO
from PIL import Image
import random, os, json
from io import BytesIO

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒", layout="centered")
st.markdown("""
<style>
header[data-testid='stHeader'], #MainMenu, footer,
[data-testid='stToolbar'], [data-testid='stStatusWidget'],
[data-testid='stBottom'], [data-testid='stBottomBlockContainer'],
[data-testid='stFileUploaderPreview'], [data-testid='stFileUploaderFile'] {display:none!important}
.block-container {padding-top: 1rem!important; padding-bottom: 0!important}
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
h2, h3 { color: #000000!important; }
p, span, label, div[data-testid="stMarkdownContainer"] p { color: #000000!important; font-weight: 600!important; }
.stButton > button { background: #FF6600; color: white; border-radius: 12px; font-weight: bold; border: none; }
.cesta-box { background:white; padding:10px; border-radius:10px; border:2px solid #FF6600; margin-bottom:5px;}
</style>
""", unsafe_allow_html=True)

if "cpf" not in st.session_state: st.session_state.cpf = None
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

if not st.session_state.cpf:
    st.title("🛒 CLIENTE ATACADÃO")
    st.subheader("👤 Digite seu CPF para entrar")
    cpf = st.text_input("CPF (11 números)", max_chars=11, label_visibility="collapsed", placeholder="CPF 11 números")
    if st.button("ENTRAR", type="primary", use_container_width=True):
        if len(cpf)==11 and cpf.isdigit():
            st.session_state.cpf = cpf
            arq = f"cesta_{cpf}.json"
            if os.path.exists(arq):
                with open(arq,"r") as f: st.session_state.carrinho = json.load(f)
            st.rerun()
        else: st.error("CPF inválido, 11 números")
    st.stop()

cpf = st.session_state.cpf

def salvar():
    with open(f"cesta_{cpf}.json","w") as f: json.dump(st.session_state.carrinho, f)

def add_produto(p):
    ean = p['ean']
    if ean in st.session_state.carrinho: st.session_state.carrinho[ean]['qtd'] += 1
    else: st.session_state.carrinho[ean] = {"dados": p, "qtd": 1}
    salvar()

def bip():
    st.markdown('<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3"></audio>', unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return YOLO("best.pt")
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

col_top1, col_top2 = st.columns([3,1])
with col_top1: st.title("🛒 CLIENTE ATACADÃO")
with col_top2:
    st.write(f"CPF: **{cpf}**")
    if st.button("Sair"): st.session_state.cpf=None; st.session_state.carrinho={}; st.rerun()

foto = st.camera_input("📸 Aponte pro produto e bipa", label_visibility="collapsed")

if foto:
    img = Image.open(foto).convert("RGB")
    res = model(img, verbose=False, conf=0.4)
    visto = set(model.names[int(b.cls)] for r in res for b in r.boxes) if res[0].boxes else set()
    if visto:
        bip()
        st.success(f"BIP! Detectei: {', '.join(visto)}")
        sugestoes = [p for p in produtos if any(v in p['yolo'] for v in visto)]
        if not sugestoes: sugestoes = produtos[:8]
        cols = st.columns(2)
        for i,p in enumerate(sugestoes[:8]):
            with cols[i%2]:
                if st.button(f"➕ {p['nome'][:22]}", key=f"s{i}_{p['ean']}"):
                    add_produto(p); bip(); st.rerun()
    else: st.warning("Não detectei - use a lista abaixo")

st.divider()
st.subheader("📋 Todos os Produtos - Combo Box")
mapa = {f"{p['ean']} - {p['nome']} - R$ {p['preco']:.2f}": p for p in produtos}
sel = st.selectbox("Escolha:", list(mapa.keys()), label_visibility="collapsed")
if st.button("➕ ADICIONAR", use_container_width=True):
