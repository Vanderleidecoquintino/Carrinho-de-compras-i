import streamlit as st
import pandas as pd
import random
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")
st.write("✅ APP CARREGOU - Se você vê isso, o app está ok")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
    st.session_state.total = 0.0
    st.session_state.compras = {}  # banco na memória
    st.session_state.ultimo_codigo = None

# Produtos fixos aqui dentro pra não precisar de CSV
produtos = [
    {"nome": "Ketchup Quero 400g", "preco": 8.90},
    {"nome": "Arroz Tio João 5kg", "preco": 27.90},
    {"nome": "Feijão Kicaldo 1kg", "preco": 7.50},
]

tab1, tab2 = st.tabs(["📱 CLIENTE", "💻 CAIXA"])

with tab1:
    st.header("📱 CLIENTE")
    
    for i, p in enumerate(produtos):
        # key único é importante
        if st.button(f"➕ {p['nome']} - R$ {p['preco']:.2f}", key=f"btn_add_{i}"):
            st.session_state.carrinho.append(p)
            st.session_state.total = sum(x['preco'] for x in st.session_state.carrinho)
            st.toast(f"Adicionado {p['nome']}")
            st.rerun()

    st.divider()
    st.subheader(f"Cesta: {len(st.session_state.carrinho)} itens - R$ {st.session_state.total:.2f}")
    
    for item in st.session_state.carrinho:
        st.write(f"- {item['nome']}")

    if st.session_state.carrinho:
        if st.button("✅ GERAR CÓDIGO PARA O CAIXA", type="primary", use_container_width=True, key="btn_gerar"):
            id_compra = str(random.randint(1000000000000, 9999999999999))
            dados = {
                "id": id_compra,
                "data": datetime.now().strftime("%H:%M:%S"),
                "itens": list(st.session_state.carrinho),
                "total": st.session_state.total
            }
            st.session_state.compras[id_compra] = dados
            st.session_state.ultimo_codigo = id_compra
            
            # Gera código de barras
            try:
                import barcode
                from barcode.writer import ImageWriter
                CODE128 = barcode.get_barcode_class('code128')
                bar = CODE128(id_compra, writer=ImageWriter())
                buf = BytesIO()
                bar.write(buf)
                st.image(buf.getvalue())
            except Exception as e:
                st.write(f"Código gerado (sem imagem): {e}")

            st.success(f"CÓDIGO GERADO: {id_compra}")
            st.code(id_compra)
            st.balloons()

        if st.session_state.ultimo_codigo:
            st.info(f"Último código: {st.session_state.ultimo_codigo}")

    if st.button("🗑️ Limpar cesta", key="btn_limpar"):
        st.session_state.carrinho = []
        st.session_state.total = 0.0
        st.session_state.ultimo_codigo = None
        st.rerun()

with tab2:
    st.header("💻 CAIXA - Terminal")
    st.write(f"Compras salvas: {len(st.session_state.compras)}")

    codigo = st.text_input("Digite ou bipe o código aqui:", key="input_caixa")
    
    if st.button("BUSCAR COMPRA", key="btn_buscar"):
        compra = st.session_state.compras.get(codigo.strip())
        if compra:
            st.success(f"✅ COMPRA {compra['id']} - {compra['data']}")
            for it in compra['itens']:
                st.write(f"✓ {it['nome']} - R$ {it['preco']:.2f}")
            st.markdown(f"## TOTAL R$ {compra['total']:.2f}")
            st.balloons()
        else:
            st.error(f"Código {codigo} não encontrado. Gere primeiro na aba CLIENTE.")
            st.write(f"Códigos disponíveis: {list(st.session_state.compras.keys())}")
