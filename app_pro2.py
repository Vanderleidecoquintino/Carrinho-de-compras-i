%%writefile /content/app_pro2.py
import streamlit as st
from PIL import Image
from ultralytics import YOLO

st.set_page_config(page_title="Detector")
st.title("📸 Detector - App Corrigido")

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# AGORA ACEITA TUDO: jpg, png, webp, jpeg
arquivo = st.file_uploader("Manda a foto", type=["jpg","jpeg","png","webp","bmp"])

if arquivo:
    img = Image.open(arquivo).convert("RGB")
    st.image(img, caption="Original", use_container_width=True)

    if st.button("DETECTAR"):
        with st.spinner("Analisando..."):
            results = model(img)
            st.image(results[0].plot(), caption="Detectado", use_container_width=True)
else:
    st.info("Manda uma foto aí de cima 👆")
