import streamlit as st
import os
from PIL import Image
from ultralytics import YOLO

st.set_page_config(page_title="TESTE BEST.PT")

@st.cache_resource
def load_model():
    if os.path.exists("best.pt"):
        try:
            m = YOLO("best.pt")
            st.success("✅ SEU best.pt CARREGOU! 7MB OK")
            return m
        except Exception as e:
            st.error(f"ERRO no best.pt: {e}")
            return YOLO("yolov8n.pt")
    else:
        st.warning("best.pt não encontrado")
        return YOLO("yolov8n.pt")

model = load_model()
st.write("Classes:", model.names)

img = st.camera_input("Aponta pro ketchup")
if img:
    im = Image.open(img)
    res = model(im, verbose=False)
    st.image(res[0].plot())
    for box in res[0].boxes:
        st.write(f"Detectou: {model.names[int(box.cls)]} - {float(box.conf):.2f}")
