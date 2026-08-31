import streamlit as st
from ultralytics import YOLO
from PIL import Image
from pyzbar.pyzbar import decode
import csv
import os

st.set_page_config(page_title="Carrinho Quero")
st.title("🛒 Carrinho Quero")
st.success("Deu certo bj na bunda")

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")
model = load_model()

@st.cache_data
def load_produtos():
    mapa = {}
    try:
        with open("produtos.csv", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
            for row in reader:
                cod = str(row.get("codigo") or row.get("ean") or row.get("cod") or "").strip()
                nome = row.get("nome") or row.get("produto") or row.get("descricao") or "Produto Quero"
                preco_txt = str(row.get("preco") or row.get("valor") or "0").replace(",", ".")
                try:
                    preco = float(preco_txt)
                except:
                    preco = 0.0
                if cod:
                    mapa[cod] = {"codigo": cod, "nome": nome, "preco": preco}
    except FileNotFoundError:
        mapa["7896102500825"] = {"codigo":"7896102500825","nome":"Ketchup Quero","preco":8.90}
    return mapa

MAPA = load_produtos()

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "total" not in st.session_state:
    st.session_state.total = 0.0

foto = st.camera_input("Aponte para o código de barras")

if foto:
    img = Image.open(foto)
    leitura = decode(img)

    if leitura:
        cod_lido = leitura[0].data.decode()
        st.info(f"Código lido: {cod_lido}")
        prod = MAPA.get(cod_lido)
        if prod:
            st.markdown(f"## {prod['nome']}")
            st.markdown(f"### R$ {prod['preco']:.2f}")
            if st.button("Adicionar ao carrinho", type="primary", key=f"add_{cod_lido}"):
                st.session_state.carrinho.append(prod)
                st.session_state.total += prod['preco']
                st.toast(f"{prod['nome']} adicionado!")
                st.rerun()
        else:
            st.error(f"Código {cod_lido} não está no produtos.csv")
    else:
        st.warning("Não li o barcode, tentando YOLO...")
        result = model(img, verbose=False)
        # CORRIGIDO AQUI
        st.image(result[0].plot())

st.divider()
st.subheader(f"Carrinho - Total R$ {st.session_state.total:.2f}")

if not st.session_state.carrinho:
    st.write("Carrinho vazio")
else:
    for i, item in enumerate(st.session_state.carrinho):
        st.write(f"{i+1}. {item['nome']} - R$ {item['preco']:.2f}")

    if st.button("Limpar carrinho"):
        st.session_state.carrinho = []
        st.session_state.total = 0.0
        st.rerun()
