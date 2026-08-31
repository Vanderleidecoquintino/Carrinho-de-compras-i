import streamlit as st
from ultralytics import YOLO
from PIL import Image

st.set_page_config(page_title="Carrinho PRO", layout="centered")
st.title("🛒 Carrinho PRO - OK")

PRODUTOS = {
    "bottle": {"nome": "Ketchup Quero 400g", "preco": 8.90, "codigo": "7896102500825"},
    "cup": {"nome": "Maionese Quero 500g", "preco": 12.50, "codigo": "7896102500658"},
    "bowl": {"nome": "Molho Tomate Quero", "preco": 4.50, "codigo": "7896102500111"},
    "banana": {"nome": "Banana kg", "preco": 5.99, "codigo": "7890000000011"},
    "apple": {"nome": "Maca kg", "preco": 7.99, "codigo": "7890000000028"},
}
MAP_CODIGO = {v["codigo"]: v for v in PRODUTOS.values()}

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()
st.success("Deu certo bj na bunda - Modelo carregado!")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
    st.session_state.total = 0.0

from pyzbar.pyzbar import decode

foto = st.camera_input("Tire a foto do produto")

if foto:
    imagem = Image.open(foto)
    achou = None

    # 1 - BARCODE
    codigos = decode(imagem)
    if codigos:
        cod = codigos[0].data.decode("utf-8")
        st.info(f"Codigo: {cod}")
        if cod in MAP_CODIGO:
            achou = MAP_CODIGO[cod]

    # 2 - YOLO
    if not achou:
        results = model(imagem, verbose=False)
        if len(results[0].boxes) > 0:
            melhor = max(results[0].boxes, key=lambda x: float(x.conf))
            classe = results[0].names[int(melhor.cls)]
            if classe in PRODUTOS:
                achou = PRODUTOS[classe]
                st.write(f"Visao detectou: {classe}")

    if achou:
        st.markdown(f"### {achou['nome']} - R$ {achou['preco']:.2f}")
        if st.button("Adicionar ao carrinho"):
            st.session_state.carrinho.append(achou)
            st.session_state.total += achou['preco']
            st.rerun()

st.divider()
st.subheader(f"Total: R$ {st.session_state.total:.2f}")

for item in st.session_state.carrinho:
    st.write(f"- {item['nome']} - R$ {item['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("Limpar Carrinho"):
        st.session_state.carrinho = []
        st.session_state.total = 0.0
        st.rerun()
