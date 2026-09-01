import streamlit as st
import random
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Atacadão 1 Bip - Teste 5 Produtos", page_icon="🛒")

# CSS LARANJÃO ATACADÃO
st.markdown("""
<style>
  .stApp {
        background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 12%, #FFFFFF 28%, #FFFFFF 85%, #FF6600 100%);
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

# 5 PRODUTOS DE TESTE + MAPEAMENTO
produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"keys":["Bulnez water","water bottle"]},
    {"nome":"[BULNEZ] Macarrão Espaguete 500g","preco":2.99,"keys":["Bulnez pasta","spaghetti"]},
    {"nome":"Coca-Cola 2L","preco":9.50,"keys":["Coca-Cola","coke bottle"]},
    {"nome":"Maionese Suavit 450g","preco":4.49,"keys":["Suavit mayonnaise","mayonnaise jar"]},
    {"nome":"[BULNEZ] Esponja Multiuso 3un","preco":2.49,"keys":["Bulnez sponge","sponge"]},
]

def bip():
    st.markdown('<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

st.title("🛒 ATACADÃO - TESTE 5 PRODUTOS")
st.caption("YOLO-World - reconhece pelo nome sem treinar")

foto = st.camera_input("📸 Aponte pro produto")

if foto:
    try:
        from ultralytics import YOLO
        @st.cache_resource
        def load_world():
            m = YOLO("yolov8s-world.pt")
            m.set_classes(["water bottle", "pasta package", "Coca-Cola bottle", "mayonnaise jar", "sponge pack"])
            return m
        model = load_world()
        img = Image.open(foto)
        results = model.predict(img, verbose=False, conf=0.1)

        achados = []
        for r in results:
            for b in r.boxes:
                nome_detectado = model.names[int(b.cls)]
                achados.append(nome_detectado)

        if achados:
            bip()
            st.success(f"BIP! Detectei: {', '.join(set(achados))}")

            # Acha produto que combina
            for nome_det in achados:
                for p in produtos:
                    if any(k.lower() in nome_det.lower() or nome_det.lower() in k.lower() for k in p['keys']):
                        if st.button(f"➕ {p['nome']} - R$ {p['preco']:.2f} (detectado: {nome_det})", key=f"det_{nome_det}_{random.randint(0,999)}"):
                            st.session_state.carrinho.append(p)
                            st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
                            bip(); st.rerun()
        else:
            st.warning("Não reconheci. Use o combo box abaixo.")
    except Exception as e:
        st.error(f"Baixando modelo World na 1ª vez... {e}")
        st.info("Vai demorar 1 min na primeira vez, depois fica rápido.")

st.divider()
st.subheader("📋 Combo Box - Todos os 5")
mapa = {f"{p['nome']} - R$ {p['preco']:.2f}": p for p in produtos}
sel = st.selectbox("Se não detectar, escolha aqui:", list(mapa.keys()))

c1,c2 = st.columns(2)
with c1:
    if st.button("➕ ADICIONAR", use_container_width=True):
        p=mapa[sel]; st.session_state.carrinho.append(p)
        st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
        bip(); st.toast(f"{p['nome']} adicionado!"); st.rerun()
with c2:
    if st.button("🗑️ Limpar carrinho", use_container_width=True):
        st.session_state.carrinho=[]; st.session_state.total=0.0; st.rerun()

st.divider()
st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - TOTAL R$ {st.session_state.total:.2f}")
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
        st.image(buf.getvalue(), caption="Mostre na saída")
        st.code(idc)
