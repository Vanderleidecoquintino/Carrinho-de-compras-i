import streamlit as st
import random, json, os
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Atacadão 1 Bip - BARCODE", page_icon="🛒")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 12%, #FFFFFF 28%, #FFFFFF 85%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
.stButton > button { background: #FF6600; color: white; border-radius: 12px; font-weight: bold; border: none; }
.stButton > button[kind="primary"] { background: #00A300!important; font-size: 22px; height: 70px; }
</style>
""", unsafe_allow_html=True)

if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]; st.session_state.total=0.0

produtos_db = [
    {"nome":"[BULNEZ] Água 500ml", "preco":1.29, "ean":"7898915120015", "yolo":"water bottle"},
    {"nome":"[BULNEZ] Macarrão 500g", "preco":2.99, "ean":"7898915120022", "yolo":"pasta package"},
    {"nome":"Coca-Cola 2L", "preco":9.50, "ean":"7894900011517", "yolo":"Coca-Cola bottle"},
    {"nome":"Suavit Maionese 450g", "preco":4.49, "ean":"7893000291481", "yolo":"mayonnaise jar"},
    {"nome":"[BULNEZ] Esponja 3un", "preco":2.49, "ean":"7898915120039", "yolo":"sponge pack"},
]

def bip(): st.markdown('<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

st.title("🛒 ATACADÃO 1 BIP - BARCODE FINAL")

tab1, tab2 = st.tabs(["📸 Câmera", "📁 Buscar arquivo"])
with tab1: f1 = st.camera_input("Câmera na loja")
with tab2: f2 = st.file_uploader("Teste com imagem dos 5", type=["jpg","png","webp"])
foto = f1 if f1 else f2

if foto:
    try:
        from ultralytics import YOLO
        @st.cache_resource
        def load():
            m=YOLO("yolov8s-world.pt")
            m.set_classes(["water bottle","pasta package","Coca-Cola bottle","mayonnaise jar","sponge pack"])
            return m
        model=load()
        img=Image.open(foto)
        st.image(img, width=300)
        res=model.predict(img, verbose=False, conf=0.15)
        achados=set(model.names[int(b.cls)] for r in res for b in r.boxes)
        if achados:
            bip()
            st.success(f"BIP! Vi: {', '.join(achados)}")
            for det in achados:
                for p in produtos_db:
                    if p['yolo'] in det or det in p['yolo']:
                        if st.button(f"➕ {p['nome']} | EAN {p['ean']} | R$ {p['preco']:.2f}", key=f"{p['ean']}_{random.randint(0,9999)}"):
                            st.session_state.carrinho.append(p)
                            st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
                            st.rerun()
    except Exception as e: st.error(e)

st.divider()
mapa={f"{p['nome']} - EAN {p['ean']}":p for p in produtos_db}
sel=st.selectbox("Manual:", list(mapa.keys()))
if st.button("➕ ADICIONAR EAN"):
    p=mapa[sel]; st.session_state.carrinho.append(p)
    st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
    bip(); st.rerun()

st.divider()
st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
for p in st.session_state.carrinho:
    st.write(f"- {p['nome']} | **EAN {p['ean']}** | R$ {p['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("✅ GERAR BARCODE FINAL PRO CAIXA", type="primary", use_container_width=True):
        id_comanda = f"{random.randint(1000000000000,9999999999999)}"
        dados = {"id": id_comanda, "eans": [p['ean'] for p in st.session_state.carrinho], "total": st.session_state.total}
        os.makedirs("comandas", exist_ok=True)
        with open(f"comandas/{id_comanda}.json","w") as f: json.dump(dados,f)

        import barcode
        from barcode.writer import ImageWriter
        CODE128=barcode.get_barcode_class('code128')
        bar=CODE128(id_comanda, writer=ImageWriter())
        buf=BytesIO(); bar.write(buf)

        bip(); st.balloons()
        st.success(f"COMANDA {id_comanda}")
        st.image(buf.getvalue(), caption=f"CAIXA: Bipe este CODE128")
        st.code(id_comanda)
        st.write("EANs que o caixa vai receber ao bipar:")
        for ean in dados['eans']: st.code(ean)
