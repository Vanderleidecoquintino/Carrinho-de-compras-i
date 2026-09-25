import streamlit as st
import pandas as pd
import os
from PIL import Image

st.set_page_config(page_title="Teste YOLO", layout="wide")
CSV_FILE = "produtos_atacadao.csv"

if not os.path.exists(CSV_FILE):
    st.error("CSV não encontrado, vai na aba 1 primeiro")
    st.stop()

df = pd.read_csv(CSV_FILE)

from ultralytics import YOLO

@st.cache_resource
def load_model():
    # COM FALLBACK - TESTE
    if os.path.exists("best.pt"):
        try:
            m = YOLO("best.pt")
            st.success("✅ Carregou seu best.pt de 7MB!")
            return m
        except Exception as e:
            st.warning(f"best.pt com erro: {e}")
            return YOLO("yolov8n.pt")
    else:
        st.info("best.pt não achado, usando yolov8n.pt")
        return YOLO("yolov8n.pt")

model = load_model()

st.write(f"Classes do modelo: {model.names}")

img_file = st.camera_input("Testa aí o ketchup")

if img_file:
    img = Image.open(img_file)
    results = model(img, verbose=False)
    st.image(img, width=300)
    for r in results:
        st.write(r.boxes)
        st.image(r.plot(), caption="Detecção")
