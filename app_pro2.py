import streamlit as st
import json
from io import BytesIO
import qrcode

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #FFFFFF!important; }
h1 {
    background-color: #FF6600!important;
    color: white!important;
    padding: 14px!important;
    border-radius: 12px!important;
    text-align: center!important;
    font-weight: 800!important;
    font-size: 22px!important;
}
.cesta-box {
    background: #FFF8F2;
    padding: 12px;
    border-radius: 10px;
    border-left: 5px solid #FF6600;
    color: #000!important;
    font-weight: 600!important;
    width: 100%;
    min-height: 44px;
    display: flex;
    align-items: center;
}
.stButton > button {
    background-color: #FF6600!important;
    color: white!important;
    border-radius: 10px!important;
    font-weight: 700!important;
    height: 44px!important;
}
#MainMenu, footer, header {visibility: hidden;}

/* >>> ISSO QUE VOCÊ ESQUECEU O NOME - @media query <<< */
@media (max-width: 768px) {
    /* no celular em pé, não deixa quebrar linha */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap!important;
        gap: 5px!important;
    }
    div[data-testid="column"] {
        min-width: 0!important;
    }
    /* coluna do nome fica maior */
    div[data-testid="column"]:nth-child(1) { flex: 5!important; }
    div[data-testid="column"]:nth-child(2) { flex: 1!important; }
    div[data-testid="column"]:nth-child(3) { flex: 1!important; }

   .cesta-box {
        font-size: 12px!important;
        padding: 8px!important;
    }
}
</style>
""", unsafe_allow_html=True)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

st.title("🛒 ATACADÃO 1-BIP")

produtos = [
    {"nome":"Água 500ml","preco":1.29,"ean":"1"},
    {"nome":"Coca 2L","preco":9.50,"ean":"2"},
    {"nome":"Óleo Soya","preco":6.90,"ean":"3"},
    {"nome":"Arroz 5kg","preco":27.90,"ean":"4"},
    {"nome":"Feijão 1kg","preco":7.50,"ean":"5"},
]

st.caption("Toque pra adicionar")
c1, c2 = st.columns(2)
for i, p in enumerate(produtos):
    with (c1 if i%2==0 else c2):
        if st.button(f"➕ {p['nome']}\nR$ {p['preco']:.2f}", key=p['ean'], use_container_width=True):
            if p['ean'] in st.session_state.carrinho:
                st.session_state.carrinho[p['ean']]['qtd'] += 1
            else:
                st.session_state.carrinho[p['ean']] = {"dados": p, "qtd": 1}
            st.rerun()

total = sum(v['dados']['preco']*v['qtd'] for v in st.session_state.carrinho.values())
st.divider()
st.subheader(f"Cesta R$ {total:.2f}")

for ean, item in list(st.session_state.carrinho.items()):
    p = item['dados']; q = item['qtd']
    col1, col2, col3 = st.columns([5,1,1])
    with col1:
        st.markdown(f"<div class='cesta-box'>{p['nome']} x{q} - R$ {p['preco']*q:.2f}</div>", unsafe_allow_html=True)
    with col2:
        if st.button("➕", key=f"a_{ean}", use_container_width=True):
            st.session_state.carrinho[ean]['qtd'] += 1
            st.rerun()
    with col3:
        if st.button("➖", key=f"r_{ean}", use_container_width=True):
            if st.session_state.carrinho[ean]['qtd'] > 1:
                st.session_state.carrinho[ean]['qtd'] -= 1
            else:
                del st.session_state.carrinho[ean]
            st.rerun()

if st.session_state.carrinho:
    st.divider()
    if st.button("GERAR QR - 1 BIP SÓ", type="primary", use_container_width=True):
        qr = qrcode.make(json.dumps(st.session_state.carrinho))
        buf = BytesIO(); qr.save(buf, format="PNG"); buf.seek(0)
        st.image(buf, width=300)
