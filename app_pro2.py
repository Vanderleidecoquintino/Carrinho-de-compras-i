import streamlit as st, os, pandas as pd
from PIL import Image, ImageDraw
from ultralytics import YOLO

st.set_page_config(page_title="Atacadão", layout="centered")

# CSS pra tirar aquele espaço de sub-pasta
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
img { max-height: 400px; object-fit: contain; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return YOLO("best.pt") if os.path.exists("best.pt") else YOLO("yolov8n.pt")

model = load_model()

arquivo = st.file_uploader("📸 Foto do produto", type=["jpg","png","jpeg"])

if arquivo:
    im = Image.open(arquivo).convert("RGB")
    # deixa a imagem pequena pra não empurrar o app pra baixo
    im.thumbnail((600,600))

    res = model(im, conf=0.25, verbose=False)[0]

    draw = ImageDraw.Draw(im)
    for box in res.boxes:
        x1,y1,x2,y2 = box.xyxy[0].tolist()
        draw.rectangle([x1,y1,x2,y2], outline="#FF0000", width=3)
        draw.text((x1, y1), f"{model.names[int(box.cls)]}", fill="#FF0000")

    st.image(im, width=350) # width fixo = fica na frente, sem rolar
    st.success(f"{len(res.boxes)} produto(s) detectado(s)")

    # Botão já aparece logo embaixo da foto, sem precisar rolar
    if len(res.boxes) > 0:
        if st.button("➕ ADICIONAR NO CARRINHO", type="primary", use_container_width=True):
            st.balloons()
            st.write("Adicionado! R$ 8,90")
else:
    st.info("👆 Escolhe a foto que já aparece na frente")
