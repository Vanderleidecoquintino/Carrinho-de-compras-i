import streamlit as st
import pandas as pd
import os
import requests
import io
from PIL import Image
import qrcode
from datetime import datetime

st.set_page_config(page_title="Atacadão FINAL", layout="wide")
CSV_FILE = "produtos_atacadao.csv"

@st.cache_data(ttl=3600)
def buscar_atacadao(termo, cep="02170901"):
    try:
        url = f"https://www.atacadao.com.br/api/catalog_system/pub/products/search?ft={termo}&_from=0&_to=8"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "PostalCode": cep}
        resp = requests.get(url, headers=headers, timeout=15)
        produtos = []
        for p in resp.json():
            try:
                item = p['items'][0]
                offer = item['sellers'][0]['commertialOffer']
                ean_real = item.get('ean') or item.get('referenceId', {}).get('Value') or "7890000000000"
                if isinstance(ean_real, list): ean_real = ean_real[0]
                produtos.append({
                    "nome": p['productName'],
                    "preco": offer['Price'],
                    "codigo": str(ean_real)[:13],
                    "imagem": item['images'][0]['imageUrl'] if item['images'] else None,
                })
            except: continue
        return produtos, None
    except Exception as e:
        return None, str(e)

if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'total' not in st.session_state: st.session_state.total = 0.0

tab1, tab2 = st.tabs(["🔍 Buscar", "📦 Cesta Final"])

with tab1:
    st.title("🔍 Buscar no Atacadão")
    termo = st.text_input("Produto", "Arroz 5kg")
    if st.button("BUSCAR", type="primary", use_container_width=True):
        res, erro = buscar_atacadao(termo)
        if erro: st.error(erro)
        else:
            for prod in res:
                c1,c2,c3 = st.columns([1,3,1])
                c1.image(prod['imagem'], width=80) if prod['imagem'] else None
                c2.write(f"**{prod['nome']}**\nR$ {prod['preco']:.2f} | {prod['codigo']}")
                if c3.button("Salvar", key=f"s{prod['codigo']}"):
                    df_new = pd.DataFrame([prod])
                    if os.path.exists(CSV_FILE):
                        old = pd.read_csv(CSV_FILE)
                        df = pd.concat([old, df_new]).drop_duplicates('codigo')
                    else: df = df_new
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Salvo no CSV!")
                st.divider()

with tab2:
    st.title("📦 Cesta - 1 Bip Final")
    if not os.path.exists(CSV_FILE):
        st.warning("Vai na aba Buscar e salva pelo menos 1 produto")
        st.stop()

    df = pd.read_csv(CSV_FILE)
    st.write(f"{len(df)} produtos cadastrados")

    # MODO FÁCIL DE BIPAR - SEM YOLO TRAVANDO
    escolha = st.selectbox("Escolha o produto para bipar:", df['nome'].tolist())
    prod_sel = df[df['nome']==escolha].iloc[0]

    col_a, col_b = st.columns(2)
    if col_a.button("📷 BIPAR COM CÂMERA (foto)", use_container_width=True):
        st.session_state['bipar'] = True
    if col_b.button("➕ BIPAR DIRETO SEM FOTO", use_container_width=True, type="primary"):
        st.session_state.carrinho.append({"nome": prod_sel['nome'], "preco": float(prod_sel['preco']), "codigo": str(prod_sel['codigo'])})
        st.session_state.total = sum(x['preco'] for x in st.session_state.carrinho)
        st.toast(f"{prod_sel['nome']} adicionado!")

    if st.session_state.get('bipar'):
        foto = st.camera_input("Aponte pro produto e tira foto")
        if foto:
            # NÃO DEPENDE MAIS DO YOLO - QUALQUER FOTO ADICIONA
            st.session_state.carrinho.append({"nome": prod_sel['nome'], "preco": float(prod_sel['preco']), "codigo": str(prod_sel['codigo'])})
            st.session_state.total = sum(x['preco'] for x in st.session_state.carrinho)
            st.session_state['bipar'] = False
            st.success(f"BIP! {prod_sel['nome']}")
            st.rerun()

    st.divider()
    if not st.session_state.carrinho:
        st.info("Cesta vazia")
    else:
        for i, it in enumerate(st.session_state.carrinho):
            c1,c2 = st.columns([4,1])
            c1.write(f"{i+1}. {it['codigo']} | {it['nome']} - R$ {it['preco']:.2f}")
            if c2.button("❌", key=f"d{i}"):
                st.session_state.carrinho.pop(i)
                st.session_state.total = sum(x['preco'] for x in st.session_state.carrinho)
                st.rerun()

        st.subheader(f"TOTAL: R$ {st.session_state.total:.2f}")

        if st.button("✅ GERAR CÓDIGO FINAL QUE REÚNE TODOS", type="primary", use_container_width=True):
            texto = ";".join([f"{x['codigo']}" for x in st.session_state.carrinho])
            texto_qr = f"ATACADAO|{datetime.now().strftime('%Y%m%d%H%M%S')}|{texto}|TOTAL:{st.session_state.total:.2f}"

            qr = qrcode.make(texto_qr)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, width=400, caption="1 BIP SÓ - CESTA COMPLETA")
            st.code(texto_qr)
            st.success("Esse é o código final que reúne todos!")

        if st.button("🗑️ Limpar cesta", use_container_width=True):
            st.session_state.carrinho=[]
            st.session_state.total=0.0
            st.rerun()
