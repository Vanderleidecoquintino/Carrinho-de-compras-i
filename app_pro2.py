import streamlit as st
import streamlit.components.v1 as components
import os
import json
from PIL import Image

# --- CONFIG ---
st.set_page_config(page_title="Carrinho Atacadao", layout="centered")

# --- PRODUTOS (mantive os seus) ---
produtos = [
    {"ean": "7896004700014", "nome": "Ketchup Quero 400g", "preco": 4.99},
    {"ean": "7898915120015", "nome": "Agua Mineral 500ml", "preco": 2.50},
    {"ean": "7894900011517", "nome": "Coca Cola 350ml", "preco": 3.50},
    # adiciona o resto dos seus 18 aqui
]

def add_produto(prod):
    if "cesta" not in st.session_state:
        st.session_state.cesta = []
    st.session_state.cesta.append(prod)
    # salva
    with open("cesta.json", "w") as f:
        json.dump(st.session_state.cesta, f)

# --- MODELO (ja com fix do git grande) ---
@st.cache_resource
def load_model():
    model_path = "best.pt"
    if not os.path.exists(model_path):
        # SE SEU BEST.PT FOR GRANDE, COLOCA ID DO DRIVE AQUI
        # file_id = "SEU_ID_DO_DRIVE"
        # import gdown
        # gdown.download(f"https://drive.google.com/uc?id={file_id}", model_path, quiet=False)
        st.warning("best.pt nao encontrado, usando modo teste sem IA")
        return None
    try:
        from ultralytics import YOLO
        return YOLO(model_path)
    except Exception as e:
        st.error(f"Erro modelo: {e}")
        return None

model = load_model()

# --- HTML DA CAMERA COM BOTAO VIRAR (CORRIGIDO SEM EMOJI) ---
html_camera = """
<div style="position:relative; width:100%;">
  <video id="vid" autoplay playsinline style="width:100%; border-radius:12px; background:black;"></video>
  <button id="btnFlip" style="position:absolute; top:10px; right:10px; z-index:10; padding:10px 16px; border-radius:20px; border:none; background:#111; color:white; font-weight:bold;">VIRAR CAMERA</button>
</div>
<script>
let currentFacing = "environment";
let stream = null;
const video = document.getElementById('vid');
async function startCam(){
  if(stream){
    stream.getTracks().forEach(t=>t.stop());
  }
  try{
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: currentFacing },
      audio: false
    });
    video.srcObject = stream;
  }catch(e){
    console.log("Erro camera: " + e.message);
  }
}
document.getElementById('btnFlip').onclick = function(){
  currentFacing = currentFacing === "environment"? "user" : "environment";
  startCam();
};
startCam();
</script>
"""

st.title("Carrinho Atacadao - Bip")

# Mostra camera html
components.html(html_camera, height=450)

# Entrada de foto do Streamlit (funciona junto)
foto = st.camera_input("Bipar produto")

if foto:
    img = Image.open(foto).convert("RGB")
    if model is not None:
        res = model(img, verbose=False, conf=0.5)[0]
        if len(res.boxes) > 0:
            cls = int(res.boxes[0].cls[0])
            nome_classe = model.names[cls].lower()

            mapa_auto = {
                "ketchup": "7896004700014",
                "agua": "7898915120015",
                "coca": "7894900011517",
            }

            ean_detectado = None
            for chave, ean in mapa_auto.items():
                if chave in nome_classe:
                    ean_detectado = ean
                    break

            if ean_detectado:
                prod = next((p for p in produtos if p["ean"]==ean_detectado), None)
                if prod:
                    add_produto(prod)
                    st.success(f"BIP! {prod['nome']} ADICIONADO")
                    st.balloons()
                    st.rerun()
        else:
            st.warning("Nao detectou produto")
    else:
        # modo teste sem modelo
        st.info("Modelo nao carregado - modo teste")
        if st.button("Adicionar Ketchup Quero 400g (teste)"):
            prod = next(p for p in produtos if p["ean"]=="7896004700014")
            add_produto(prod)
            st.success("Adicionado!")
            st.rerun()

# Mostra cesta
st.divider()
st.subheader("Cesta")
if "cesta" in st.session_state and len(st.session_state.cesta)>0:
    total = sum([p["preco"] for p in st.session_state.cesta])
    for p in st.session_state.cesta:
        st.write(f"{p['nome']} - R$ {p['preco']}")
    st.write(f"**Total: R$ {total:.2f}**")
    if st.button("Limpar cesta"):
        st.session_state.cesta = []
        st.rerun()
else:
    st.write("Cesta vazia")
