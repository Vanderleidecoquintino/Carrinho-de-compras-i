import streamlit as st
from ultralytics import YOLO
import qrcode, io, json
from PIL import Image
from datetime import datetime

# MAPEIA O QUE O YOLO VÊ PRO EAN REAL DA LOJA
# depois você troca pelos produtos reais do Atacadão
PRODUTOS_DB = {
    "bottle": {"nome": "Óleo Soya 900ml", "ean": "7892300000011", "preco": 7.99},
    "cup": {"nome": "Arroz Camil 5kg", "ean": "7893500020132", "preco": 24.90},
    "book": {"nome": "Feijão Kicaldo 1kg", "ean": "7898903551025", "preco": 8.49},
}

@st.cache_resource
def load_yolo():
    return YOLO("yolov8n.pt") # modelo leve que roda no celular

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.set_page_config(page_title="Atacadão 1-Bip", layout="wide")
tab_cliente, tab_caixa = st.tabs(["📱 CLIENTE - Aponta", "💻 CAIXA - Recebe"])

with tab_cliente:
    st.title("📱 Cliente - Aponte pro produto")
    foto = st.camera_input("Aponte a câmera pro produto na gôndola")

    if foto:
        img = Image.open(foto)
        model = load_yolo()
        results = model(img)

        # desenha o que o YOLO viu
        st.image(results[0].plot(), caption="YOLO detectou")

        for box in results[0].boxes:
            classe = model.names[int(box.cls[0])]
            if classe in PRODUTOS_DB:
                prod = PRODUTOS_DB[classe]
                if st.button(f"➕ Adicionar {prod['nome']} - R$ {prod['preco']}", key=f"{classe}_{datetime.now()}"):
                    st.session_state.carrinho.append(prod)
                    st.toast(f"{prod['nome']} no carrinho!")

    if st.session_state.carrinho:
        st.divider()
        total = sum(p['preco'] for p in st.session_state.carrinho)
        st.subheader(f"Carrinho: {len(st.session_state.carrinho)} itens - R$ {total:.2f}")
        for p in st.session_state.carrinho:
            st.write(f"- {p['ean']} | {p['nome']}")

        if st.button("✅ GERAR BARCODE DA CESTA", type="primary", use_container_width=True):
            # Cria o payload que o caixa vai ler
            payload = {
                "loja": "ATACADAO",
                "hora": datetime.now().isoformat(),
                "itens": st.session_state.carrinho
            }
            texto_qr = json.dumps(payload)

            qr = qrcode.make(texto_qr)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, width=350, caption="MOSTRE ESSE QR NO CAIXA - 1 BIP SÓ")
            st.code(f"{len(st.session_state.carrinho)} produtos dentro desse QR")

with tab_caixa:
    st.title("💻 Caixa - Recebe cesta")
    st.write("Bipe o QR do cliente aqui (upload da foto do QR)")
    qr_foto = st.camera_input("Câmera do caixa lendo QR", key="caixa_cam")

    if qr_foto:
        # aqui você usaria pyzbar pra decodificar, simplifiquei pra demo
        # por enquanto mostra como seria a lista
        if st.session_state.carrinho:
            st.success(f"BIP RECEBIDO! {len(st.session_state.carrinho)} itens:")
            for p in st.session_state.carrinho:
                st.write(f"✅ {p['ean']} - {p['nome']} - R$ {p['preco']:.2f}")
            st.metric("TOTAL A PAGAR", f"R$ {sum(p['preco'] for p in st.session_state.carrinho):.2f}")
            if st.button("Finalizar venda"):
                st.session_state.carrinho = []
                st.rerun()
        else:
            st.warning("Carrinho vazio - gere um QR na aba Cliente primeiro")
