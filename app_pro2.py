import streamlit as st
from ultralytics import YOLO
from PIL import Image

st.set_page_config(layout="centered")
st.markdown("<style>header,footer,#MainMenu,[data-testid='stToolbar'],[data-testid='stFileUploaderPreview'],[data-testid='stBottom'],[data-testid='stBottomBlockContainer']{display:none!important}*{border:none!important;box-shadow:none!important}</style>", unsafe_allow_html=True)

@st.cache_resource
def load(): return YOLO("best.pt")
model = load()

f = st.file_uploader("", type=["jpg","png","jpeg"], label_visibility="collapsed")
if f:
    st.markdown("<style>[data-testid='stFileUploader']{display:none!important}</style>", unsafe_allow_html=True)
    im = Image.open(f).convert("RGB")
    r = model(im, verbose=False)[0]
    st.image(r.plot()[:,:,::-1], width=380)
    if st.button("Outra foto"): st.rerun()
