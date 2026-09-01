import streamlit as st
from PIL import Image
import random
import io
from barcode import Code128
from barcode.writer import ImageWriter

st.set_page_config(page_title="Carrinho PRO", layout="wide")
st.title("Carrinho de Compras PRO 🛒")

PRODUTOS = {
    "bottle": {"nome": "Ketchup Quero 400g", "preco": 8.90, "codigo": "7896102500825"},
    "cup": {"nome": "Maionese Quero 500g", "preco": 12.50, "codigo": "7896102500658"},
    "bowl": {"nome": "Molho Quero", "preco": 6.90, "codigo": "7896102500111"},
}

@st.cache_resource
def carregar_modelo():
    from ultralytics import YOLO
    return YOLO('yolov8n.pt')

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'detectados' not in st.session_state:
    st.session_state.detectados = []
if 'codigo_final' not in st.session_state:
    st.session_state.codigo_final = None
if 'total_final' not in st.session_state:
    st.session_state.total_final = 0
if 'buffer_final' not in st.session_state:
    st.session_state.buffer_final = None

modelo = carregar_modelo()

uploaded = st.file_uploader("Envie a foto", type=["jpg","png","jpeg"])
foto_camera = st.camera_input("Ou tire foto agora")
arquivo = uploaded or foto_camera

if arquivo:
    img = Image.open(arquivo)
    col1, col2 = st.columns(2)
    col1.image(img, caption="Original")

    with st.spinner("Analisando..."):
        results = modelo(img, conf=0.3)
        st.session_state.detectados = []
        for r in results:
            col2.image(r.plot(), caption="Detectado")
            for box in r.boxes:
                cls_nome = modelo.names[int(box.cls)]
                if cls_nome in PRODUTOS:
                    st.session_state.detectados.append(PRODUTOS[cls_nome])

# BOTOES FORA DO LOOP
if st.session_state.detectados:
    st.success(f"Encontrado: {len(st.session_state.detectados)} produto(s)")
    for idx, prod in enumerate(st.session_state.detectados):
        if st.button(f"➕ Adicionar {prod['nome']} - R$ {prod['preco']:.2f}", key=f"add_prod_{idx}"):
            st.session_state.carrinho.append(prod)
            st.success(f"{prod['nome']} adicionado!")
            st.rerun()

# --- CESTA ---
st.divider()
st.subheader(f"🛒 Sua Cesta ({len(st.session_state.carrinho)} itens)")

if len(st.session_state.carrinho) == 0:
    st.info("Cesta vazia. Tire uma foto.")
else:
    total = 0
    for i, item in enumerate(st.session_state.carrinho):
        c1, c2, c3 = st.columns([3,1,1])
        c1.write(f"{item['nome']}")
        c2.write(f"R$ {item['preco']:.2f}")
        total += item['preco']
        if c3.button("❌", key=f"del_{i}"):
            st.session_state.carrinho.pop(i)
            st.rerun()
    
    st.markdown(f"### **Total: R$ {total:.2f}**")

    if st.button("Finalizar Compra e Gerar Código de Barras", type="primary"):
        st.balloons()
        codigo_compra = f"200{random.randint(1000000,9999999)}"
        buffer = io.BytesIO()
        Code128(codigo_compra, writer=ImageWriter()).write(buffer)
        buffer.seek(0)
        st.session_state.codigo_final = codigo_compra
        st.session_state.buffer_final = buffer.getvalue()
        st.session_state.total_final = total

# MOSTRA BARCODE E TRAVA PRA NÃO SUMIR
if st.session_state.codigo_final:
    st.divider()
    st.success(f"Compra #{st.session_state.codigo_final} - Total R$ {st.session_state.total_final:.2f}")
    st.image(st.session_state.buffer_final, caption=f"Código: {st.session_state.codigo_final} - Passe no scanner")
    if st.button("🆕 Nova Compra"):
        st.session_state.carrinho = []
        st.session_state.detectados = []
        st.session_state.codigo_final = None
        st.session_state.buffer_final = None
        st.session_state.total_final = 0
        st.rerun()
