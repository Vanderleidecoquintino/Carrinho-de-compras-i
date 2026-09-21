# apaga o arquivo com erro
import os
if os.path.exists("/content/app_pro2.py"):
    os.remove("/content/app_pro2.py")

# cria o arquivo NOVO já certo, SEM o %%writefile dentro
code = '''
import streamlit as st
from PIL import Image
from ultralytics import YOLO
import os

st.set_page_config(page_title="Detector")
st.title("📸 Detector - Seu modelo")

# acha seu best.pt automaticamente
caminho = "/content/best.pt"
if not os.path.exists(caminho):
    for r,d,f in os.walk("/content"):
        if "best.pt" in f:
            caminho = os.path.join(r, "best.pt")
            break

@st.cache_resource
def load_model():
    return YOLO(caminho)

model = load_model()
st.success(f"Modelo: {caminho}")

arquivo = st.file_uploader("Envia a foto", type=["jpg","jpeg","png","webp","bmp"])

if arquivo:
    img = Image.open(arquivo).convert("RGB")
    st.image(img, use_container_width=True)
    if st.button("DETECTAR"):
        results = model(img)
        st.image(results[0].plot(), caption="Resultado", use_container_width=True)
'''

with open("/content/app_pro2.py", "w") as f:
    f.write(code)

print("✅ Arquivo corrigido! Agora pode rodar o ngrok de novo.")
