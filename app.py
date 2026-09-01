import streamlit as st
import random
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]
    st.session_state.total=0.0

# MARCA PRÓPRIA BULNEZ + PRODUTOS REAIS
produtos = [
    # --- BULNEZ - Marca própria Atacadão (mais barato) ---
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"classe":"bottle"},
    {"nome":"[BULNEZ] Macarrão Espaguete 500g","preco":2.99,"classe":"box"},
    {"nome":"[BULNEZ] Massa Fresca Lasanha 500g","preco":7.90,"classe":"box"},
    {"nome":"[BULNEZ] Tortilha de Trigo 400g","preco":8.50,"classe":"box"},
    {"nome":"[BULNEZ] Esponja Multiuso 3un","preco":2.49,"classe":"box"},
    {"nome":"[BULNEZ] Vassoura","preco":12.90,"classe":"box"},
    {"nome":"[BULNEZ] Pá para Lixo","preco":9.90,"classe":"box"},

    # --- Produtos reais Atacadão Julho 2026 ---
    {"nome":"Maionese Suavit 450g","preco":4.49,"classe":"bottle"},
    {"nome":"Café Bom Jesus 250g","preco":12.98,"classe":"box"},
    {"nome":"Biscoito Vitarella 350g","preco":4.99,"classe":"box"},
    {"nome":"Requeijão Canto Minas 400g","preco":13.90,"classe":"bottle"},
    {"nome":"Batata Palha Yoki 100g","preco":4.99,"classe":"box"},
    {"nome":"Limpador Limpol 500ml","preco":2.99,"classe":"bottle"},
    {"nome":"Chocolate Harald 500g","preco":59.90,"classe":"box"},
    {"nome":"Capeletti Mezzani 1kg","preco":18.90,"classe":"box"},
    {"nome":"Energético Baly 473ml","preco":5.49,"classe":"bottle"},
    {"nome":"Suco Subello 200ml","preco":1.49,"classe":"bottle"},
    {"nome":"Arroz Tio João 5kg","preco":27.90,"classe":"box"},
    {"nome":"Feijão Kicaldo 1kg","preco":7.50,"classe":"box"},
    {"nome":"Ketchup Quero 400g","preco":8.90,"classe":"bottle"},
    {"nome":"Coca-Cola 2L","preco":9.50,"classe":"bottle"},
]

def bip():
    st.markdown("""<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

st.title("🛒 Atacadão - 1 Bip | Bulnez")

foto = st.camera_input("📸 Aponte pro produto")
if foto:
    try:
        from ultralytics import YOLO
        @st.cache_resource
        def load_model(): return YOLO("yolov8n.pt")
        model = load_model()
        img = Image.open(foto)
        results = model(img, verbose=False)
        classes = set(model.names[int(b.cls)] for r in results for b in r.boxes)
        if classes:
            bip()
            st.success(f"BIP! Vi: {', '.join(classes)}")
            filtrados = [p for p in produtos if p['classe'] in classes] or produtos[:6]
            for i,p in enumerate(filtrados):
                if st.button(f"➕ {p['nome']} R$ {p['preco']:.2f}", key=f"y{i}"):
                    st.session_state.carrinho.append(p)
                    st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
                    bip(); st.rerun()
    except:
        pass

st.divider()
st.subheader("📋 Combo Box - Todos os produtos")
opcoes = {f"{p['nome']} - R$ {p['preco']:.2f}": p for p in produtos}
escolha = st.selectbox("Escolha:", list(opcoes.keys()))

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ ADICIONAR", use_container_width=True):
        p = opcoes[escolha]
        st.session_state.carrinho.append(p)
        st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
        bip(); st.toast("Adicionado!"); st.rerun()
with col2:
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state.carrinho=[]; st.session_state.total=0.0; st.rerun()

st.divider()
st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
for it in st.session_state.carrinho:
    st.write(f"- {it['nome']} R$ {it['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("✅ FINALIZAR E PAGAR", type="primary", use_container_width=True):
        id_compra=str(random.randint(1000000000000,9999999999999))
        import barcode
        from barcode.writer import ImageWriter
        CODE128=barcode.get_barcode_class('code128')
        bar=CODE128(id_compra, writer=ImageWriter())
        buf=BytesIO(); bar.write(buf)
        bip(); st.balloons()
        st.success(f"PAGO! TOTAL R$ {st.session_state.total:.2f}")
        st.image(buf.getvalue())
        st.code(id_compra)
        st.info("Mostre esse código na saída - 242 lojas Atacadão com Bulnez")
