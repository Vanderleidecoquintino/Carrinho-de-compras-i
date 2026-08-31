import streamlit as st
from ultralytics import YOLO
from PIL import Image

st.set_page_config(page_title="Carrinho PRO", layout="centered")
st.title("🛒 Carrinho PRO")

PRODUTOS = {
    "bottle": {"nome": "Ketchup Quero 400g", "preco": 8.90, "codigo": "7896102500825"},
    "cup": {"nome": "Maionese 500g", "preco": 12.50, "codigo": "7896102500658"},
    "bowl": {"nome": "Molho Tomate 340g", "preco": 4.50, "codigo": "7896102500111"},
    "banana": {"nome": "Banana kg", "preco": 5.99, "codigo": "7890000000011"},
    "apple": {"nome": "Maca kg", "preco": 7.99, "codigo": "7890000000028"},
}
CODIGO_PARA_PRODUTO = {v["codigo"]: v for v in PRODUTOS.values()}

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()
st.write("✅ Modelo OK - pode usar!")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
    st.session_state.total = 0.0

# Tenta pyzbar sem quebrar
try:
    from pyzbar.pyzbar import decode
    HAS_BARCODE = True
except:
    HAS_BARCODE = False

foto = st.camera_input("Tira a foto")

if foto:
    imagem = Image.open(foto)
    achou = None

    # 1. BARCODE
    if HAS_BARCODE:
        codigos = decode(imagem)
        if codigos:
            codigo = codigos[0].data.decode("utf-8")
            st.success(f"Codigo lido: {codigo}")
            if codigo in CODIGO_PARA_PRODUTO:
                achou = CODIGO_PARA_PRODUTO[codigo]

    # 2. YOLO
    if not achou:
        results = model(imagem, verbose=False)
        if len(results[0].boxes) > 0:
            melhor = max(results[0].boxes, key=lambda x: float(x.conf))
            classe = results[0].names[int(melhor.cls)]
            if classe in PRODUTOS:
                achou = PRODUTOS[classe]
                st.info(f"Detectado: {classe}")

    if achou:
        st.markdown(f"### {achou['nome']} - R$ {achou['preco']:.2f}")
        if st.button("Adicionar ao carrinho"):
            st.session_state.carrinho.append(achou)
            st.session_state.total += achou['preco']
            st.rerun()

st.divider()
st.subheader(f"Carrinho: R$ {st.session_state.total:.2f}")

for p in st.session_state.carrinho:
    st.write(f"- {p['nome']} - R$ {p['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("Limpar carrinho"):
        st.session_state.carrinho = []
        st.session_state.total = 0.0
        st.rerun()
