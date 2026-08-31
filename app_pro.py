import streamlit as st
from PIL import Image

st.set_page_config(page_title="Carrinho PRO", layout="wide")

@st.cache_resource
def carregar_modelo():
    from ultralytics import YOLO
    return YOLO('yolov8n.pt')

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("Carrinho de Compras PRO 🛒")

with st.spinner("Carregando IA..."):
    modelo = carregar_modelo()

uploaded = st.file_uploader("Envie a foto", type=["jpg","png","jpeg"])
foto_camera = st.camera_input("Ou tire foto")

arquivo = uploaded or foto_camera

if arquivo:
    col1, col2 = st.columns(2)
    img = Image.open(arquivo)
    
    # CORRIGIDO - sem width, funciona em qualquer versão
    col1.image(img, caption="Foto Original")

    with st.spinner("Detectando..."):
        results = modelo(img)
        for r in results:
            im_plot = r.plot()
            col2.image(im_plot, caption="Detectado")
            
            for box in r.boxes:
                nome = modelo.names[int(box.cls)]
                if st.button(f"Adicionar {nome}", key=f"add_{id(box)}"):
                    st.session_state.carrinho.append({"nome": nome})
                    st.success(f"{nome} adicionado!")
                    st.rerun()

st.divider()
st.subheader(f"Seu Carrinho ({len(st.session_state.carrinho)})")
for i, item in enumerate(list(st.session_state.carrinho)):
    c1, c2 = st.columns([4,1])
    c1.write(item['nome'])
    if c2.button("❌", key=f"del_{i}"):
        st.session_state.carrinho.pop(i)
        st.rerun()
