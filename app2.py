import streamlit as st
from ultralytics import YOLO
from PIL import Image
import random
from io import BytesIO
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
h2, h3 { color: #000000!important; }
p, span, label, div[data-testid="stMarkdownContainer"] p { color: #000000!important; font-weight: 600!important; }
.stButton > button { background: #FF6600; color: white; border-radius: 12px; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

# --- BANCO + SESSAO QUE NAO PERDE NO F5 ---
@st.cache_resource
def get_db():
    conn = sqlite3.connect('atacadao.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY AUTOINCREMENT, cpf TEXT, inicio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS carrinho (sessao_id INTEGER, produto TEXT, preco REAL, ean TEXT)')
    return conn
conn = get_db()

if 'sessao_id' not in st.session_state:
    st.session_state.sessao_id = None
if 'carrinho' not in st.session_state:
    st.session_state.carrinho=[]
if 'cpf' not in st.session_state:
    st.session_state.cpf = ""

# --- TOPO CPF ---
st.title("🛒 CLIENTE ATACADÃO")
cpf = st.text_input("CPF Cliente:", value=st.session_state.cpf, placeholder="Digite 11 dígitos")

if st.button("Iniciar Compra") and cpf:
    cur = conn.cursor()
    cur.execute("INSERT INTO sessoes (cpf, inicio) VALUES (?,?)", (cpf, datetime.now().isoformat()))
    st.session_state.sessao_id = cur.lastrowid
    st.session_state.cpf = cpf
    conn.commit()
    st.success(f"Sessão {st.session_state.sessao_id} iniciada para CPF {cpf}")
    st.rerun()

if not st.session_state.sessao_id:
    st.warning("Digite o CPF e inicie a compra pra liberar a câmera")
    st.stop()

st.info(f"Cliente: {st.session_state.cpf} | Sessão: {st.session_state.sessao_id}")

@st.cache_resource
def load_model():
    return YOLO("yolo11m.pt")
model = load_model()

produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015","yolo":["bottle"]},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517","yolo":["bottle"]},
    {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481","yolo":["bottle","cup"]},
    {"nome":"Requeijão Canto Minas 400g","preco":13.90,"ean":"7896908200015","yolo":["bottle","cup","bowl"]},
    {"nome":"Óleo Soya 900ml","preco":6.90,"ean":"7892300000014","yolo":["bottle"]},
    {"nome":"Ketchup Quero 400g","preco":8.90,"ean":"7896004700014","yolo":["bottle"]},
    {"nome":"Limpador Limpol 500ml","preco":2.99,"ean":"7896039710015","yolo":["bottle"]},
    {"nome":"Energético Baly 473ml","preco":5.49,"ean":"7898915120040","yolo":["bottle","can"]},
    {"nome":"[BULNEZ] Macarrão 500g","preco":2.99,"ean":"7898915120022","yolo":["box","book"]},
    {"nome":"[BULNEZ] Massa Fresca 500g","preco":7.90,"ean":"7898915120050","yolo":["box","bowl"]},
    {"nome":"[BULNEZ] Tortilha 400g","preco":8.50,"ean":"7898915120060","yolo":["box"]},
    {"nome":"Arroz Tio João 5kg","preco":27.90,"ean":"7893500010001","yolo":["box","book"]},
    {"nome":"Biscoito Vitarella 350g","preco":4.99,"ean":"7896004000010","yolo":["box","book"]},
    {"nome":"Café Bom Jesus 250g","preco":12.98,"ean":"7896045500012","yolo":["box","cup"]},
    {"nome":"Chocolate Harald 500g","preco":59.90,"ean":"7896063800011","yolo":["box","book"]},
    {"nome":"Suco Subello 200ml","preco":1.49,"ean":"7898951000015","yolo":["box"]},
    {"nome":"[BULNEZ] Esponja 3un","preco":2.49,"ean":"7898915120039","yolo":["box"]},
    {"nome":"Feijão Kicaldo 1kg","preco":7.50,"ean":"7896101000013","yolo":["box","book"]},
]

def bip():
    st.markdown('<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3"></audio>', unsafe_allow_html=True)

foto = st.camera_input("📸 Aponte pro produto e bipa")

if foto:
    img = Image.open(foto)
    res = model(img, verbose=False, conf=0.4)
    visto = set(model.names[int(b.cls)] for r in res for b in r.boxes) if res[0].boxes else set()
    if visto:
        bip()
        st.success(f"BIP! Detectei: {', '.join(visto)}")
        sugestoes = [p for p in produtos if any(v in p['yolo'] for v in visto)]
        if not sugestoes: sugestoes = produtos[:8]
        st.write("Sugestões:")
        cols = st.columns(2)
        for i,p in enumerate(sugestoes[:8]):
            with cols[i%2]:
                if st.button(f"➕ {p['ean'][-4:]} | {p['nome'][:20]}", key=f"s{i}_{p['ean']}"):
                    st.session_state.carrinho.append(p)
                    conn.execute("INSERT INTO carrinho VALUES (?,?,?,?)", (st.session_state.sessao_id, p['nome'], p['preco'], p['ean']))
                    conn.commit()
                    bip(); st.rerun()
    else:
        st.warning("Não detectei - use a lista abaixo")

st.divider()
st.subheader("📋 Todos os Produtos - Combo Box")
mapa = {f"{p['ean']} - {p['nome']} - R$ {p['preco']:.2f}": p for p in produtos}
sel = st.selectbox("Escolha:", list(mapa.keys()))
c1,c2 = st.columns(2)
with c1:
    if st.button("➕ ADICIONAR", use_container_width=True):
        st.session_state.carrinho.append(mapa[sel])
        conn.execute("INSERT INTO carrinho VALUES (?,?,?,?)", (st.session_state.sessao_id, mapa[sel]['nome'], mapa[sel]['preco'], mapa[sel]['ean']))
        conn.commit()
        bip(); st.rerun()
with c2:
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state.carrinho=[]
        conn.execute("DELETE FROM carrinho WHERE sessao_id=?", (st.session_state.sessao_id,))
        conn.commit()
        st.rerun()

total = sum(x['preco'] for x in st.session_state.carrinho)
st.divider()
st.subheader(f"🛒 {len(st.session_state.carrinho)} itens - R$ {total:.2f}")
for it in st.session_state.carrinho:
    st.markdown(f"<p style='color:black!important'>- {it['ean']} | {it['nome']} R$ {it['preco']:.2f}</p>", unsafe_allow_html=True)

if st.session_state.carrinho:
    if st.button("✅ PAGAR - GERAR CÓDIGO SAÍDA", type="primary", use_container_width=True):
        idc=str(random.randint(1000000000000,9999999999999))
        try:
            import barcode
            from barcode.writer import ImageWriter
            CODE128=barcode.get_barcode_class('code128')
            bar=CODE128(idc, writer=ImageWriter())
            buf=BytesIO(); bar.write(buf); buf.seek(0)
            st.image(buf)
        except:
            st.code(idc)
        st.success(f"PAGO! CPF {st.session_state.cpf} - R$ {total:.2f}")
        st.balloons()
