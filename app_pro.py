import streamlit as st
from ultralytics import YOLO
from PIL import Image
from pyzbar.pyzbar import decode
import csv, os

st.title("🛒 Carrinho PRO - Quero")
st.success("Deu certo bj na bunda - base estável")

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")
model = load_model()

@st.cache_data
def load_produtos():
    mapa = {}
    if os.path.exists("produtos.csv"):
        with open("produtos.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                mapa[r["codigo"].strip()] = {
                    "nome": r["nome"],
                    "preco": float(r["preco"]),
                    "codigo": r["codigo"]
                }
        st.toast(f"CSV com {len(mapa)} produtos")
    else:
        mapa = {
            "7896102500825": {"nome": "Ketchup Quero", "preco": 8.90, "codigo": "7896102500825"},
            "7896102500658": {"nome": "Maionese Quero", "preco": 12.50, "codigo": "7896102500658"},
        }
    return mapa

MAPA = load_produtos()

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
    st.session_state.total = 0.0

foto = st.camera_input("Escaneie o produto")
produto_achado = None

if foto:
    img = Image.open(foto)
    # 1. Tenta barcode primeiro
    cods = decode(img)
    if cods:
        cod = cods[0].data.decode()
        st.info(f"Código lido: {cod}")
        if cod in MAPA:
            produto_achado = MAPA[cod]
    # 2. Se não achou, tenta YOLO
    if not produto_achado:
        res = model(img, verbose=False)
        if len(res[0].boxes) > 0:
            st.image(res[0].plot(), caption="Objeto detectado")
            st.warning("Barcode não lido, usando YOLO como backup")

    if produto_achado:
        st.markdown(f"### {produto_achado['nome']} - R$ {produto_achado['preco']:.2f}")
        if st.button("✅ Adicionar ao carrinho", type="primary"):
            st.session_state.carrinho.append(produto_achado)
            st.session_state.total += produto_achado['preco']
            st.rerun()
    else:
        if cods or 'res' in locals():
            st.error("Produto não cadastrado no produtos.csv")

st.divider()
st.subheader(f"Total: R$ {st.session_state.total:.2f}")
for i, p in enumerate(st.session_state.carrinho):
    st.write(f"{i+1}. {p['nome']} - R$ {p['preco']:.2f}")

if st.button("Limpar carrinho"):
    st.session_state.carrinho = []
    st.session_state.total = 0.0
    st.rerun()
