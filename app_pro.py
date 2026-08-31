import streamlit as st
from PIL import Image

st.set_page_config(page_title="Carrinho PRO", layout="wide")
st.title("Carrinho de Compras PRO 🛒")

@st.cache_resource
def carregar_modelo():
    from ultralytics import YOLO
    return YOLO('yolov8n.pt')

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

modelo = carregar_modelo()

uploaded = st.file_uploader("Envie a foto", type=["jpg","png","jpeg"])
foto_camera = st.camera_input("Ou tire foto agora")
arquivo = uploaded or foto_camera

if arquivo:
    img = Image.open(arquivo)
    col1, col2 = st.columns(2)
    col1.image(img, caption="Original")

    with st.spinner("Analisando..."):
        results = modelo(img, conf=0.3) # confiança baixa pra pegar tudo
        for r in results:
            im_plot = r.plot()
            col2.image(im_plot, caption="Detectado")

            for i, box in enumerate(r.boxes):
                nome = modelo.names[int(box.cls)]
                conf = float(box.conf)
                # Mostra o botão SEMPRE
                if col1.button(f"➕ Adicionar {nome} ({conf:.0%}) no carrinho", key=f"add_{i}"):
                    st.session_state.carrinho.append({"nome": "Ketchup Quero 400g", "conf": conf})
                    st.success("Adicionado!")
                    st.rerun()

# CESTA - ESSA PARTE AGORA SEMPRE APARECE
st.divider()
st.subheader(f"🛒 Sua Cesta ({len(st.session_state.carrinho)} itens)")

if len(st.session_state.carrinho) == 0:
    st.info("A cesta está vazia. Tire uma foto e clique em Adicionar.")
else:
    total = 0
    for i, item in enumerate(st.session_state.carrinho):
        c1, c2 = st.columns([4,1])
        c1.write(f"{i+1}. {item['nome']}")
        if c2.button("❌ Remover", key=f"del_{i}"):
            st.session_state.carrinho.pop(i)
            st.rerun()
    
    if st.button("Finalizar Compra"):
        st.balloons()
        st.success("Compra finalizada!")
        st.session_state.carrinho = []
