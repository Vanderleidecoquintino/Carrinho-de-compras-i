import streamlit as st
import pandas as pd
import os
import requests
from PIL import Image
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Atacadão PRO", layout="wide", page_icon="🛒")
CSV_FILE = "produtos_atacadao.csv"

# --- FUNÇÃO BUSCA ATACADÃO ---
@st.cache_data(ttl=3600)
def buscar_atacadao(termo, cep="02170901"):
    try:
        url = f"https://www.atacadao.com.br/api/catalog_system/pub/products/search?ft={termo}&_from=0&_to=4"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "PostalCode": cep.replace("-","")}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code!= 200: return None, f"Erro {resp.status_code}"
        produtos = []
        for p in resp.json():
            try:
                item = p['items'][0]
                offer = item['sellers'][0]['commertialOffer']
                produtos.append({"nome": p['productName'],"marca": p.get('brand',''),"preco": offer['Price'],"imagem": item['images'][0]['imageUrl'] if item['images'] else None,})
            except: continue
        return produtos, None
    except Exception as e: return None, str(e)

if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'total' not in st.session_state: st.session_state.total = 0.0

tab1, tab2 = st.tabs(["🔍 Buscar Preços", "📷 Carrinho YOLO"])

with tab1:
    st.title("🛒 Buscador Atacadão")
    c1, c2 = st.columns([3,1])
    with c1: termo = st.text_input("Produto", "Arroz 5kg")
    with c2: cep = st.text_input("CEP", "02170-901")
    if st.button("🔍 BUSCAR", type="primary", use_container_width=True):
        with st.spinner("Buscando..."):
            res, erro = buscar_atacadao(termo, cep.replace("-",""))
            if erro: st.error(erro)
            elif not res: st.warning("Nada")
            else:
                for prod in res:
                    col1, col2, col3 = st.columns([1,3,1])
                    with col1:
                        if prod['imagem']: st.image(prod['imagem'], width=90)
                    with col2: st.write(f"**{prod['nome']}** - R$ {prod['preco']:.2f}")
                    with col3:
                        if st.button("💾 Salvar", key=f"s_{prod['nome']}_{prod['preco']}
