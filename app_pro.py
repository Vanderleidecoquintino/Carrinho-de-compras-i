import streamlit as st
from ultralytics import YOLO
from PIL import Image

st.set_page_config(page_title="Carrinho PRO + Barcode", layout="centered")
st.title("🛒 Carrinho PRO + Barcode")
st.caption("Detecta objeto + lê código de barras")

# --- SUA LISTA ---
PRODUTOS = {
    "bottle": {"nome": "Ketchup Quero 400g", "preco": 8.90, "codigo": "7896102500825"},
    "cup": {"nome": "Maionese Quero 500g", "preco": 12.50, "codigo": "7896102500658"},
    "bowl": {"nome": "Molho de Tomate Quero 340g", "preco": 4.50, "codigo": "7896102500111"},
    "banana": {"nome": "Banana Prata kg", "preco": 5.99, "codigo": "7890000000011"},
    "apple": {"nome": "Maçã Gala kg", "preco": 7.99, "codigo": "7890000000028"},
}

# Mapa de código de barras -> produto (pra quando ler o barcode)
CODIGO_PARA_PRODUTO = {v["codigo"]: v for v in PRODUTOS.values()}

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

try:
    model = load_model()
    st.success("✅ YOLO OK - deu certo bj na bunda")
except Exception as e:
    st.error(f"Erro YOLO: {e}")
    st.stop()

# Tenta carregar leitor de barcode (se não tiver, continua sem)
try:
    from pyzbar.pyzbar import decode
    HAS_BARCODE = True
except:
    HAS_BARCODE = False
    st.warning("Barcode não instalado ainda, vai só com YOLO por enquanto")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
    st.session_state.total = 0.0

# --- CÂMERA ---
foto = st.camera_input("📸 Aponta pro produto ou pro código de barras")

if foto:
    imagem = Image.open(foto)

    # 1º TENTA BARCODE (mais preciso)
    produto_encontrado = None

    if HAS_BARCODE:
        try:
            barcodes = decode(imagem)
            if barcodes:
                codigo_lido = barcodes[0].data.decode("utf-8")
                st.info(f"📦 Código lido: {codigo_lido}")
                if codigo_lido in CODIGO_PARA_PRODUTO:
                    produto_encontrado = CODIGO_PARA_PRODUTO[codigo_lido]
                    st.success(f"Achado pelo código: {produto_encontrado['nome']}")
                else:
                    st.warning(f"Código {codigo_lido} não está na sua lista CODIGO_PARA_PRODUTO")
        except Exception as e:
            st.write(f"Erro barcode: {e}")

    # 2º SE NÃO ACHOU POR BARCODE, TENTA YOLO
    if not produto_encontrado:
        with st.spinner("Tentando por visão..."):
            results = model(imagem, verbose=False)
            if len(results[0].boxes) > 0:
                melhor = max(results[0].boxes, key=lambda x: float(x.conf))
                classe = results[0].names[int(melhor.cls)]
                conf = float(melhor.conf)

                if classe in PRODUTOS and conf > 0.4:
                    produto_encontrado = PRODUTOS[classe]
                    st.image(results[0].plot(), caption=f"Detectado por visão: {classe} {conf:.0%}", use_container_width=True)
                else:
                    st.image(results[0].plot(), use_container_width=True)
                    st.info(f"Vi '{classe}' mas não está na lista")
            else:
                st.warning("Não detectei nada")

    # 3º ADICIONA NO CARRINHO
    if produto_encontrado:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(produto_encontrado['nome'], f"R$ {produto_encontrado['preco']:.2f}")
            st.caption(f"Código: {produto_encontrado['codigo']}")
        with col2:
            if st.button("➕ Adicionar", type="primary", use_container_width=True):
                st.session_state.carrinho.append(produto_encontrado)
                st.session_state.total += produto_encontrado['preco']
                st.toast("Adicionado!")
                st.balloons()

# --- CARRINHO ---
st.divider()
st.subheader(f"🧾 Carrinho ({len(st.session_state.carrinho)}) - Total: R$ {st.session_state.total:.2f}")

for i, p in enumerate(st.session_state.carrinho):
    st.write(f"{i+1}. {p['nome']} - R$ {p['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("🗑️ Limpar tudo"):
        st.session_state.carrinho = []
        st.session_state.total = 0.0
        st.rerun()
