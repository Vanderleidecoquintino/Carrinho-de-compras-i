import os

# acha o best.pt
for root, dirs, files in os.walk("/content"):
    if "best.pt" in files:
        caminho = os.path.join(root, "best.pt")
        print(f"ACHEI: {caminho}")

# já reescreve o app pra usar seu best.pt
caminho_best = caminho # pega o que achou acima

code = f'''
import streamlit as st
from PIL import Image
from ultralytics import YOLO

st.set_page_config(page_title="Detector com seu modelo")
st.title("📸 Detector - Seu best.pt")

@st.cache_resource
def load_model():
    return YOLO("{caminho_best}")

model = load_model()
st.success(f"Modelo carregado: {caminho_best}")

arquivo = st.file_uploader("Manda a foto", type=["jpg","jpeg","png","webp","bmp"])

if arquivo:
    img = Image.open(arquivo).convert("RGB")
    st.image(img, caption="Original", use_container_width=True)
    if st.button("DETECTAR"):
        with st.spinner("Analisando..."):
            results = model(img)
            st.image(results[0].plot(), caption="Detectado", use_container_width=True)
'''

with open("/content/app_pro2.py", "w") as f:
    f.write(code)

print("✅ app_pro2.py ATUALIZADO pro seu best.pt")
