import streamlit as st
import os
from PIL import Image

st.set_page_config(page_title="Teste Final")
st.write("App abriu OK")

from ultralytics import YOLO

@st.cache_resource
def load_model():
    if os.path.exists("best.pt"):
        try:
            m = YOLO("best.pt")
            st.success("best.pt de 7MB carregou!")
            return m
        except Exception as e:
            st.error(f"best.pt erro: {e}")
            return YOLO("yolov8n.pt")
    else:
        st.info("Sem best.pt, usando yolov8n.pt")
        return YOLO("yolov8n.pt")

model = load_model()
st.write(f"Classes: {model.names}")

# TROCA CAMERA POR UPLOAD - APARECE SEMPRE
arquivo = st.file_uploader("Escolha foto do ketchup", type=["jpg","jpeg","png"])

if arquivo:
    im = Image.open(arquivo)
    st.image(im, caption="Foto enviada", width=300)

    res = model(im, conf=0.25, verbose=False)[0]
    st.write(f"Achou {len(res.boxes)} objetos")

    # Mostra sem usar r.plot() que tava embolando
    for box in res.boxes:
        cls = int(box.cls)
        conf = float(box.conf)
        x1,y1,x2,y2 = box.xyxy[0].tolist()
        st.write(f"-> {model.names[cls]}: {conf*100:.0f}% em [{x1:.0f},{y1:.0f}]")
