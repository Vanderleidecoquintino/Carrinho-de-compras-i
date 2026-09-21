import os
for root, dirs, files in os.walk("/content"):
    if "best.pt" in files:
        caminho_best = os.path.join(root, "best.pt")
        print(f"ACHEI: {caminho_best}")

code = f'''
import streamlit as st
from PIL import Image
from ultralytics import YOLO

st.set_page_config(page_title="Detector Ketchup")
st.title("🍅 Detector - Só aceita KETCHUP")

@st.cache_resource
def load_model():
    return YOLO("{caminho_best}")

model = load_model()
st.write(f"Modelo: {caminho_best} | Classes: {{model.names}}")

conf = st.slider("Sensibilidade", 0.1, 0.9, 0.25)

tab1, tab2 = st.tabs(["📁 Galeria", "📷 Câmera"])
img = None

with tab1:
    arquivo = st.file_uploader("Foto", type=["jpg","jpeg","png","webp","bmp"])
    if arquivo:
        img = Image.open(arquivo).convert("RGB")
with tab2:
    foto = st.camera_input("Tirar foto")
    if foto:
        img = Image.open(foto).convert("RGB")

if img:
    st.image(img, use_container_width=True)
    if st.button("VERIFICAR", type="primary"):
        results = model(img, conf=conf)
        boxes = results[0].boxes

        if len(boxes) == 0:
            st.error("⛔ NADA DETECTADO - Não é ketchup válido!")
        else:
            encontrou_ketchup = False
            for box in boxes:
                cls_nome = model.names[int(box.cls[0])].lower()
                if "ketchup" in cls_nome:
                    encontrou_ketchup = True

            st.image(results[0].plot(), use_container_width=True)

            if encontrou_ketchup:
                st.success("✅ OK - É KETCHUP!")
            else:
                st.error("⛔ ERRO - ISSO É CANDIDA! NÃO É KETCHUP! Produto reprovado!")
                st.warning("Detectado candida, não pode passar.")
'''

with open("/content/app_pro2.py", "w") as f:
    f.write(code)

print("✅ AGORA DÁ ERRO SE FOR CANDIDA")
