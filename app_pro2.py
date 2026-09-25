import streamlit as st
from ultralytics import YOLO
from PIL import Image

st.set_page_config(layout="centered")
st.markdown("<style>*{border:none!important;box-shadow:none!important}[data-testid='stFileUploaderPreview']{display:none}</style>", unsafe_allow_html=True)

model = YOLO("best.pt")
foto = st.file_uploader("Foto", type=["jpg","png"])
if foto:
    img = Image.open(foto)
    r = model(img, verbose=False)[0]
    st.image(r.plot(), width=350)
