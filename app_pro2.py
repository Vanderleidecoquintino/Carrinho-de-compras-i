import streamlit as st
import os
from ultralytics import YOLO
import glob

st.set_page_config(page_title="Detector Ketchup Quero", layout="centered")
st.title("🍅 Detector Ketchup Quero - 95%")

# ACHA O best.pt EM QUALQUER LUGAR
candidatos = glob.glob("/content/**/*.pt", recursive=True) + glob.glob("**/*.pt", recursive=True)
candidatos = list(set(candidatos))

if not candidatos:
    st.error("❌ Não achei nenhum.pt! Sobe seu best.pt de novo em /content")
    st.stop()

# pega o maior arquivo.pt (seu best tem ~50MB)
best_path = max(candidatos, key=lambda x: os.path.getsize(x))
st.success(f"✅ Modelo carregado: {best_path} ({os.path.getsize(best_path)/1024/1024:.1f} MB)")

# CARREGA O MODELO
@st.cache_resource
def load_model(path):
    return YOLO(path)

model = load_model(best_path)

# APP
uploaded = st.file_uploader("Manda foto da garrafa azul", type=["jpg","jpeg","png"])
cam = st.camera_input("Ou usa a câmera do cel")

img = uploaded or cam

if img:
    results = model(img, conf=0.25)
    st.image(results[0].plot(), caption="Detecção", use_column_width=True)

    for box in results[0].boxes:
        cls = model.names[int(box.cls[0])]
        conf = float(box.conf[0])*100
        st.write(f"**{cls}**: {conf:.2f}%")

else:
    st.info("👆 Manda uma foto pra testar")
