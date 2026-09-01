import streamlit as st
import random
from datetime import datetime
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]
    st.session_state.total=0.0
    st.session_state.ultimo_codigo=None

produtos = [
    {"nome":"Ketchup Quero 400g","preco":8.9,"classe":"bottle"},
    {"nome":"Coca-Cola 2L","preco":9.5,"classe":"bottle"},
    {"nome":"Arroz Tio João 5kg","preco":27.9,"classe":"box"},
    {"nome":"Feijão Kicaldo","preco":7.5,"classe":"box"},
    {"nome":"Maçã","preco":4.2,"classe":"apple"},
    {"nome":"Banana","preco":5.1,"classe":"banana"},
]

def tocar_bip():
    st.markdown("""
    <audio autoplay>
      <source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

st.title("🛒 Atacadão - Aponte e Bipa")

foto = st.camera_input("Aponte para o produto")

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
            tocar_bip()
            st.success(f"BIP! Vi: {', '.join(classes)}")
            filtrados = [p for p in produtos if p['classe'] in classes] or produtos
            for i,p in enumerate(filtrados):
                if st.button(f"➕ {p['nome']} - R$ {p['preco']:.2f}", key=f"y{i}"):
                    st.session_state.carrinho.append(p)
                    st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
                    tocar_bip()
                    st.toast("Na cesta!")
                    st.rerun()
    except Exception as e:
        st.warning(f"Carregando IA... use manual abaixo")

st.write("**Escolha manual:**")
for i,p in enumerate(produtos):
    if st.button(f"➕ {p['nome']} - R$ {p['preco']:.2f}", key=f"m{i}"):
        st.session_state.carrinho.append(p)
        st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
        tocar_bip()
        st.rerun()

st.divider()
st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
for it in st.session_state.carrinho:
    st.write(f"- {it['nome']} R$ {it['preco']:.2f}")

if st.session_state.carrinho:
    if st.button("✅ FINALIZAR - GERAR CÓDIGO DE SAÍDA", type="primary", use_container_width=True):
        id_compra=str(random.randint(1000000000000,9999999999999))
        st.session_state.ultimo_codigo=id_compra
        import barcode
        from barcode.writer import ImageWriter
        CODE128=barcode.get_barcode_class('code128')
        bar=CODE128(id_compra, writer=ImageWriter())
        buf=BytesIO(); bar.write(buf)
        tocar_bip()
        st.balloons()
        st.success(f"PAGO! TOTAL R$ {st.session_state.total:.2f}")
        st.image(buf.getvalue())
        st.code(id_compra)
        st.markdown(f"Mostre esse código na saída")

if st.button("🗑️ Limpar cesta"):
    st.session_state.carrinho=[]; st.session_state.total=0.0; st.session_state.ultimo_codigo=None; st.rerun()
