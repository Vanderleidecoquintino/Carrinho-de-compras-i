import streamlit as st
import pandas as pd, random
from datetime import datetime
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]
    st.session_state.total=0.0
    st.session_state.compras={}
    st.session_state.ultimo_codigo=None

# Produtos com classe YOLO mapeada
produtos = [
    {"nome":"Ketchup Quero 400g","preco":8.9,"classe":"bottle"},
    {"nome":"Coca-Cola 2L","preco":9.5,"classe":"bottle"},
    {"nome":"Arroz Tio João 5kg","preco":27.9,"classe":"box"},
    {"nome":"Feijão Kicaldo","preco":7.5,"classe":"box"},
    {"nome":"Maçã","preco":4.2,"classe":"apple"},
    {"nome":"Banana","preco":5.1,"classe":"banana"},
]

tab1, tab2 = st.tabs(["📱 CLIENTE COM CÂMERA", "💻 CAIXA"])

with tab1:
    st.header("📱 Aponte para o produto")
    
    # --- CÂMERA COM IA ---
    foto = st.camera_input("Aponte a câmera", key="cam")
    
    if foto:
        try:
            from ultralytics import YOLO
            @st.cache_resource
            def load_model():
                return YOLO("yolov8n.pt")
            model = load_model()
            
            img = Image.open(foto)
            results = model(img, verbose=False)
            classes = set(model.names[int(b.cls)] for r in results for b in r.boxes)
            
            if classes:
                st.success(f"👁️ Vi: {', '.join(classes)} - BIP!")
                st.audio("https://cdn.freesound.org/previews/4/4587_3198-lq.mp3")
                # Filtra produtos pela classe vista
                filtrados = [p for p in produtos if p['classe'] in classes]
                if not filtrados:
                    filtrados = produtos
                
                st.write("**É um desses? Clique para adicionar:**")
                for i,p in enumerate(filtrados):
                    if st.button(f"➕ {p['nome']} - R$ {p['preco']:.2f}", key=f"yolo_{i}_{p['nome']}"):
                        st.session_state.carrinho.append(p)
                        st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
                        st.toast(f"{p['nome']} na cesta!")
                        st.rerun()
            else:
                st.warning("Não reconheci. Tente de novo ou escolha abaixo.")
        except Exception as e:
            st.error(f"Erro na IA: {e} - Use os botões manuais abaixo")

    st.divider()
    st.write("**Ou escolha manual:**")
    for i,p in enumerate(produtos):
        if st.button(f"➕ {p['nome']} - R$ {p['preco']:.2f}", key=f"man_{i}"):
            st.session_state.carrinho.append(p)
            st.session_state.total=sum(x['preco'] for x in st.session_state.carrinho)
            st.rerun()

    st.divider()
    st.subheader(f"🛒 Cesta {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
    for it in st.session_state.carrinho:
        st.write(f"- {it['nome']} R$ {it['preco']:.2f}")

    if st.session_state.carrinho:
        if st.button("✅ GERAR CÓDIGO DE BARRAS PRO CAIXA", type="primary", use_container_width=True, key="gerar"):
            id_compra=str(random.randint(1000000000000,9999999999999))
            dados={"id":id_compra,"data":datetime.now().strftime("%H:%M:%S"),"itens":list(st.session_state.carrinho),"total":st.session_state.total}
            st.session_state.compras[id_compra]=dados
            st.session_state.ultimo_codigo=id_compra

            import barcode
            from barcode.writer import ImageWriter
            CODE128=barcode.get_barcode_class('code128')
            bar=CODE128(id_compra, writer=ImageWriter())
            buf=BytesIO(); bar.write(buf)
            st.balloons()
            st.image(buf.getvalue())
            st.code(id_compra)
            st.success(f"Mostre esse código pro caixa bipar!")

    if st.button("🗑️ Limpar", key="limpar_cli"):
        st.session_state.carrinho=[]; st.session_state.total=0.0; st.session_state.ultimo_codigo=None; st.rerun()

with tab2:
    st.header("💻 CAIXA - BIP")
    codigo=st.text_input("Bipe o código do cliente:", key="caixa_input")
    if st.button("BUSCAR", key="buscar"):
        c=st.session_state.compras.get(codigo.strip())
        if c:
            st.success(f"COMPRA {c['id']} - {c['data']}")
            for it in c['itens']:
                st.write(f"✓ {it['nome']} R$ {it['preco']:.2f}")
            st.markdown(f"# TOTAL R$ {c['total']:.2f}")
            st.balloons()
            st.audio("https://cdn.freesound.org/previews/456/456588_9498993-lq.mp3")
        else:
            st.error("Código não encontrado. Gere na aba cliente primeiro.")
