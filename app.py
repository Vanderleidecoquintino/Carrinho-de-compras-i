import streamlit as st
import random
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Atacadão Vip", page_icon="🛒")

# CSS ATACADÃO LARANJÃO
st.markdown("""
<style>
   .stApp {
        background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%);
    }
    h1 {
        background: #FF6600; color: white!important;
        padding: 15px; border-radius: 15px;
        text-align: center; font-weight: 900;
    }
   .stButton > button {
        background: #FF6600; color: white;
        border-radius: 12px; font-weight: bold; border: none;
    }
   .stButton > button[kind="primary"] {
        background: #00A300!important; font-size: 18px; height: 60px;
    }
</style>
""", unsafe_allow_html=True)

if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]
    st.session_state.total=0.0

# MAPEAMENTO YOLO -> PRODUTO REAL
produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"yolo":["bottle"]},
    {"nome":"Coca-Cola 2L","preco":9.50,"yolo":["bottle"]},
    {"nome":"Maionese Suavit 450g","preco":4.49,"yolo":["bottle","cup"]},
    {"nome":"Requeijão Canto Minas 400g","preco":13.90,"yolo":["bottle","cup","bowl"]},
    {"nome":"Óleo Soya 900ml","preco":6.90,"yolo":["bottle"]},
    {"nome":"Ketchup Quero 400g","preco":8.90,"yolo":["bottle"]},
    {"nome":"Limpador Limpol 500ml","preco":2.99,"yolo":["bottle"]},
    {"nome":"Energético Baly 473ml","preco":5.49,"yolo":["bottle","can"]},
    {"nome":"[BULNEZ] Macarrão 500g","preco":2.99,"yolo":["box","book"]},
    {"nome":"[BULNEZ] Massa Fresca 500g","preco":7.90,"yolo":["box","bowl"]},
    {"nome":"[BULNEZ] Tortilha 400g","preco":8.50,"yolo":["box"]},
    {"nome":"Arroz Tio João 5kg","preco":27.90,"yolo":["box","book"]},
    {"nome":"Biscoito Vitarella 350g","preco":4.99,"yolo":["box","book"]},
    {"nome":"Café Bom Jesus 250g","preco":12.98,"yolo":["box","cup"]},
    {"nome":"Chocolate Harald 500g","preco":59.90,"yolo":["box","book"]},
    {"nome":"Suco Subello 200ml","preco":1.49,"yolo":["box"]},
    {"nome":"[BULNEZ] Esponja 3un","preco":2.49,"yolo":["box"]},
    {"nome":"Feijão Kicaldo 1kg","preco":7.50,"yolo":["box","book"]},
]

def bip():
    st.markdown('<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

st.title("🛒 ATACADÃO - 1 BIP")

foto = st.camera_input("📸 Aponte pro produto e bipa")

if foto:
    try:
        from ultralytics import YOLO
        @st.cache_resource
        def load(): return YOLO("yolov8n.pt")
        model = load()
        img = Image.open(foto)
        res = model(img, verbose=False)
        visto = set(model.names[int(b.cls)] for r in res for b in r.boxes)

        if visto:
            bip()
            st.success(f"BIP! Detectei: {', '.join(visto)}")
            # Filtra produtos que combinam com o que foi visto
            sugestoes = [p for p in produtos if any(v in p['yolo'] for v in visto)]
            if not sugestoes: sugestoes = produtos[:5]

            st.write("Sugestões inteligentes:")
            for i,p in enumerate(sugestoes[:5]):
                if st.button(f"➕ {p['nome']} R$ {p['preco']:.2f}", key=f"s{i}"):
                    st.session_state.carrinho.append(p)
                    st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
                    bip(); st.rerun()
    except Exception as e:
        st.info(f"Carregando IA... {e}")

st.divider()
st.subheader("📋 Todos os Produtos - Combo Box")
mapa = {f"{p['nome']} - R$ {p['preco']:.2f}": p for p in produtos}
sel = st.selectbox("Escolha:", list(mapa.keys()))

c1,c2 = st.columns(2)
with c1:
    if st.button("➕ ADICIONAR", use_container_width=True):
        p=mapa[sel]; st.session_state.carrinho.append(p)
        st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
        bip(); st.toast(f"{p['nome']} OK!"); st.rerun()
with c2:
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state.carrinho=[]; st.session_state.total=0.0; st.rerun()

st.divider()
st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
for it in st.session_state.carrinho:
    st.write(f"- {it['nome']} R$ {it['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("✅ PAGAR - GERAR CÓDIGO SAÍDA", type="primary", use_container_width=True):
        idc=str(random.randint(1000000000000,9999999999999))
        import barcode
        from barcode.writer import ImageWriter
        CODE128=barcode.get_barcode_class('code128')
        bar=CODE128(idc, writer=ImageWriter())
        buf=BytesIO(); bar.write(buf)
        bip(); st.balloons()
        st.success(f"PAGO! R$ {st.session_state.total:.2f}")
        st.image(buf.getvalue())
        st.code(idc)
