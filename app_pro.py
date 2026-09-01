import streamlit as st
import pandas as pd
import os
import requests
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="Atacadão PRO - Busca + YOLO", layout="wide", page_icon="🛒")

CSV_FILE = "produtos_atacadao.csv"

# --- FUNÇÃO BUSCA ATACADÃO ---
@st.cache_data(ttl=3600)
def buscar_atacadao(termo, cep="02170901"):
    try:
        url = f"https://www.atacadao.com.br/api/catalog_system/pub/products/search?ft={termo}&_from=0&_to=4"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "PostalCode": cep.replace("-","")}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code!=200: return None, f"Erro {resp.status_code}"
        produtos=[]
        for p in resp.json():
            try:
                item=p['items'][0]
                offer=item['sellers'][0]['commertialOffer']
                produtos.append({
                    "nome":p['productName'],
                    "marca":p.get('brand',''),
                    "preco":offer['Price'],
                    "imagem":item['images'][0]['imageUrl'] if item['images'] else None,
                })
            except: continue
        return produtos, None
    except Exception as e: return None, str(e)

# --- ESTADO ---
if 'carrinho' not in st.session_state: st.session_state.carrinho=[]
if 'total' not in st.session_state: st.session_state.total=0.0

# --- ABAS ---
tab1, tab2 = st.tabs(["🔍 1. Buscar Preços Atacadão", "📷 2. Carrinho YOLO PRO"])

with tab1:
    st.title("🛒 Buscador Atacadão - Ao Vivo")
    c1,c2=st.columns([3,1])
    with c1: termo=st.text_input("Produto", "Arroz 5kg", key="busca")
    with c2: cep=st.text_input("CEP", "02170-901")

    if st.button("🔍 BUSCAR", type="primary", use_container_width=True):
        with st.spinner(f"Buscando {termo}..."):
            res,erro=buscar_atacadao(termo, cep.replace("-",""))
            if erro: st.error(erro)
            else:
                for prod in res:
                    col1,col2,col3=st.columns([1,3,1])
                    with col1:
                        if prod['imagem']: st.image(prod['imagem'], width=100)
                    with col2:
                        st.write(f"**{prod['nome']}**")
                        st.write(f"R$ {prod['preco']:.2f} - {prod['marca']}")
                    with col3:
                        if st.button("💾 Salvar", key=f"s_{prod['nome']}_{prod['preco']}"):
                            novo=pd.DataFrame([{"nome":prod['nome'],"preco":prod['preco'],"codigo":"7890000000000","classe_yolo":"bottle"}])
                            if os.path.exists(CSV_FILE):
                                old=pd.read_csv(CSV_FILE)
                                df=pd.concat([old,novo]).drop_duplicates('nome')
                            else: df=novo
                            df.to_csv(CSV_FILE,index=False)
                            st.success("Salvo no CSV!")
                    st.divider()

    st.subheader(f"📦 Seu CSV ({CSV_FILE})")
    if os.path.exists(CSV_FILE):
        df=pd.read_csv(CSV_FILE)
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Baixar CSV", df.to_csv(index=False), "produtos_atacadao.csv")
    else:
        # cria CSV inicial com 10
        df=pd.DataFrame([
            {"nome":"Arroz Tio Joao 5kg","preco":27.9,"codigo":"7893500020132","classe_yolo":"box"},
            {"nome":"Feijao Kicaldo 1kg","preco":8.49,"codigo":"7898903551025","classe_yolo":"cup"},
            {"nome":"Oleo Soya 900ml","preco":7.29,"codigo":"7896273000011","classe_yolo":"bottle"},
            {"nome":"Acucar Uniao 5kg","preco":19.9,"codigo":"7891910000197","classe_yolo":"box"},
            {"nome":"Cafe Pilao 500g","preco":18.9,"codigo":"7891021001142","classe_yolo":"cup"},
            {"nome":"Leite Italac 1L","preco":4.99,"codigo":"7896051130058","classe_yolo":"bottle"},
            {"nome":"Macarrao Renata 500g","preco":3.79,"codigo":"7896022201086","classe_yolo":"box"},
            {"nome":"Ketchup Quero 400g","preco":8.9,"codigo":"7896102500825","classe_yolo":"bottle"},
            {"nome":"Maionese Hellmanns 500g","preco":9.9,"codigo":"7891030000000","classe_yolo":"bowl"},
            {"nome":"Papel Higienico Neve 12un","preco":16.9,"codigo":"7896110000000","classe_yolo":"book"},
        ])
        df.to_csv(CSV_FILE,index=False)
        st.dataframe(df)

with tab2:
    st.title("📷 Carrinho PRO - YOLO Atacadão")

    # Carrega produtos do CSV
    if os.path.exists(CSV_FILE):
        df=pd.read_csv(CSV_FILE)
        PRODUTOS={row['classe_yolo']: {"nome":row['nome'],"preco":row['preco'],"codigo":row['codigo']} for _,row in df.iterrows()}
        st.caption(f"{len(PRODUTOS)} produtos do Atacadão carregados do CSV")
    else:
        st.warning("Busque produtos na aba 1 primeiro")
        PRODUTOS={}

    from ultralytics import YOLO
    @st.cache_resource
    def load_model(): return YOLO("yolov8n.pt")
    model=load_model()

    img_file=st.camera_input("Aponte para o produto")

    if img_file and PRODUTOS:
        img=Image.open(img_file)
        results=model(img)
        # Simula detecção -> pega classe detectada e busca no PRODUTOS
        for r in results:
            for box in r.boxes:
                cls=model.names[int(box.cls)]
                if cls in PRODUTOS:
                    prod=PRODUTOS[cls]
                    st.session_state.carrinho.append(prod)
                    st.session_state.total+=prod['preco']
                    st.toast(f"{prod['nome']} adicionado!")

    # Cesta
    st.divider()
    st.subheader(f"🛒 Cesta: {len(st.session_state.carrinho)} itens - Total R$ {st.session_state.total:.2f}")
    for item in st.session_state.carrinho:
        st.write(f"- {item['nome']} - R$ {item['preco']:.2f}")

    if st.button("Limpar Cesta"):
        st.session_state.carrinho=[]
        st.session_state.total=0.0
        st.rerun()
