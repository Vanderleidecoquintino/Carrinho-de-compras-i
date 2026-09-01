import streamlit as st
import pandas as pd
import os, json, random
from PIL import Image
from datetime import datetime
from io import BytesIO
import base64

st.set_page_config(page_title="Atacadão 1 Bip", layout="wide", page_icon="🛒")

CSV_FILE = "produtos_atacadao.csv"
DB_FILE = "compras.json"

if 'carrinho' not in st.session_state: st.session_state.carrinho=[]
if 'total' not in st.session_state: st.session_state.total=0.0
if 'venda_finalizada' not in st.session_state: st.session_state.venda_finalizada=False

if not os.path.exists(DB_FILE):
    with open(DB_FILE,'w') as f: json.dump({},f)

def salvar_compra(id_compra, dados):
    with open(DB_FILE,'r') as f: db=json.load(f)
    db[id_compra]=dados
    with open(DB_FILE,'w') as f: json.dump(db,f)

def buscar_compra(id_compra):
    with open(DB_FILE,'r') as f: db=json.load(f)
    return db.get(id_compra)

# Função do som de BIP
def tocar_bip():
    bip_base64 = "UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==" # bip curto
    # som real via JS
    st.markdown("""
    <audio autoplay>
    <source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3" type="audio/mpeg">
    </audio>
    <script>
    var audio = new Audio('https://cdn.freesound.org/previews/4/4587_3198-lq.mp3');
    audio.play();
    </script>
    """, unsafe_allow_html=True)

tab_cliente, tab_caixa = st.tabs(["📱 CLIENTE", "💻 CAIXA + BIP"])

with tab_cliente:
    st.title("📱 Aponte e Compre")
    if not os.path.exists(CSV_FILE):
        st.error("Crie o produtos_atacadao.csv")
        st.stop()
    df=pd.read_csv(CSV_FILE)

    from ultralytics import YOLO
    @st.cache_resource
    def load_model(): return YOLO("yolov8n.pt")
    model=load_model()

    foto=st.camera_input("Aponte para o produto", key="cli")
    if foto:
        img=Image.open(foto)
        results=model(img,verbose=False)
        classes=set(model.names[int(b.cls)] for r in results for b in r.boxes)
        if classes:
            st.success(f"Vi: {', '.join(classes)}")
            tocar_bip()
            cand=df[df['classe_yolo'].isin(classes)]
            if cand.empty: cand=df
            for idx,row in cand.iterrows():
                if st.button(f"➕ {row['nome']} - R$ {row['preco']:.2f}",key=f"add{idx}"):
                    st.session_state.carrinho.append({"nome":row['nome'],"preco":float(row['preco'])})
                    st.session_state.total=sum(i['preco'] for i in st.session_state.carrinho)
                    st.toast("BIP! Na cesta!"); st.rerun()

    st.divider()
    st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
    for item in st.session_state.carrinho:
        st.write(f"• {item['nome']} - R$ {item['preco']:.2f}")

    if st.session_state.carrinho:
        if st.button("✅ GERAR CÓDIGO PARA CAIXA", type="primary", use_container_width=True):
            id_compra = str(random.randint(1000000000000, 9999999999999))
            dados = {"id": id_compra, "data": datetime.now().strftime("%d/%m %H:%M"), "itens": st.session_state.carrinho, "total": st.session_state.total}
            salvar_compra(id_compra, dados)
            import barcode
            from barcode.writer import ImageWriter
            CODE128 = barcode.get_barcode_class('code128')
            code_img = CODE128(id_compra, writer=ImageWriter())
            buf = BytesIO(); code_img.write(buf)
            st.balloons(); tocar_bip()
            st.success(f"Compra {id_compra} - Mostre pro caixa")
            st.image(buf.getvalue(), caption=f"ID {id_compra}")
            st.markdown(f"### {id_compra}")

    if st.button("🗑️ Limpar"): 
        st.session_state.carrinho=[]; st.session_state.total=0.0; st.rerun()

with tab_caixa:
    st.title("💻 Terminal - BIPE AQUI")
    st.info("Clique no campo e bipe a tela do cliente")

    id_bipado = st.text_input("🔫 CAMPO DO BIP:", placeholder="Bipe aqui...", key="caixa_input")

    if id_bipado:
        compra = buscar_compra(id_bipado.strip())
        if compra:
            tocar_bip()
            st.success(f"✅ COMPRA {compra['id']} - {compra['data']}")
            for item in compra['itens']:
                st.write(f"✓ {item['nome']} - R$ {item['preco']:.2f}")
            st.markdown(f"# TOTAL: R$ {compra['total']:.2f}")
            if st.button("💰 FINALIZAR VENDA", type="primary", use_container_width=True):
                tocar_bip()
                st.balloons()
                st.success("VENDA FINALIZADA!")
                st.audio("https://cdn.freesound.org/previews/456/456588_9498993-lq.mp3", autoplay=True)
                st.session_state.venda_finalizada=True
        else:
            st.error(f"Compra {id_bipado} não encontrada")
