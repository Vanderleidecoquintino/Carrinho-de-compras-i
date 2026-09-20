import streamlit as st
from ultralytics import YOLO
from PIL import Image
import os, json

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
.cesta-box { background:white; padding:10px; border-radius:10px; border:2px solid #FF6600; margin-bottom:5px;}
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
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
            arq = f"cesta_{cpf}.json"
            if os.path.exists(arq):
                with open(arq,"r") as f:
                    st.session_state.carrinho = json.load(f)
            st.rerun()
    st.stop()

def salvar():
    with open(f"cesta_{st.session_state.cpf}.json","w") as f:
        json.dump(st.session_state.carrinho, f)

def add_produto(p):
    ean = p['ean']
    if ean in st.session_state.carrinho:
        st.session_state.carrinho[ean]['qtd'] += 1
    else:
        st.session_state.carrinho[ean] = {"dados": p, "qtd": 1}
    salvar()

@st.cache_resource
def load_models():
    modelo_geral = YOLO("yolo11m.pt")
    modelo_ketchup = None
    if os.path.exists("best.pt"):
        modelo_ketchup = YOLO("best.pt") # SEU MODELO 95%
    return modelo_geral, modelo_ketchup

model_geral, model_ketchup = load_models()

produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015","yolo":["bottle"]},
    {"nome":"Ketchup Quero 400g","preco":8.90,"ean":"7896004700014","yolo":["bottle"],"custom":True},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517","yolo":["bottle"]},
    #... resto dos seus produtos
]

# --- CÂMERA ---
foto = st.camera_input("📸 Aponte pro produto")

if foto:
    img = Image.open(foto)
    ketchup_detectado = False
    conf_ketchup = 0

    # 1. TESTA SEU MODELO 95% PRIMEIRO
    if model_ketchup:
        res_k = model_ketchup(img, conf=0.25, verbose=False)
        if len(res_k[0].boxes) > 0:
            ketchup_detectado = True
            conf_ketchup = float(res_k[0].boxes.conf[0])
            st.image(res_k[0].plot(), caption=f"KETCHUP QUERO {conf_ketchup*100:.1f}% - SEU MODELO!")
            st.success(f"🍅 KETCHUP QUERO 95% DETECTADO! {conf_ketchup*100:.2f}%")
            st.balloons()
            # adiciona direto
            p_ketchup = next(p for p in produtos if "Ketchup Quero" in p['nome'])
            if st.button(f"➕ ADICIONAR {p_ketchup['nome']} - R$ {p_ketchup['preco']}", type="primary", use_container_width=True):
                add_produto(p_ketchup)
                st.rerun()

    # 2. Se não é ketchup, usa modelo geral
    if not ketchup_detectado:
        res = model_geral(img, verbose=False, conf=0.4)
        visto = set(model_geral.names[int(b.cls)] for r in res for b in r.boxes) if res[0].boxes else set()
        if visto:
            st.success(f"BIP! {', '.join(visto)}")
            sugestoes = [p for p in produtos if any(v in p['yolo'] for v in visto)]
            for p in sugestoes[:6]:
                if st.button(f"➕ {p['nome']}", key=p['ean']):
                    add_produto(p)
                    st.rerun()
