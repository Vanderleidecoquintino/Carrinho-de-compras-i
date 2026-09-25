import streamlit as st
from ultralytics import YOLO
from PIL import Image
import random, os, json
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Atacadão 1 Bip", page_icon="🛒")
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #FF6600 0%, #FF9A4D 10%, #FFFFFF 25%, #FFFFFF 80%, #FF6600 100%); }
h1 { background: #FF6600; color: white!important; padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; }
h2, h3 { color: #000000!important; }
p, span, label, div[data-testid="stMarkdownContainer"] p { color: #000000!important; font-weight: 600!important; }
.stButton > button { background: #FF6600; color: white; border-radius: 12px; font-weight: bold; border: none; }
.cesta-box { background:white; padding:10px; border-radius:10px; border:2px solid #FF6600; margin-bottom:5px;}
</style>
""", unsafe_allow_html=True)

if "cpf" not in st.session_state:
    st.session_state.cpf = None
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

if not st.session_state.cpf:
    st.title("🛒 CLIENTE ATACADÃO")
    st.subheader("👤 Digite seu CPF para entrar")
    cpf = st.text_input("CPF (11 números)", max_chars=11)
    if st.button("ENTRAR", type="primary", use_container_width=True):
        if len(cpf)==11 and cpf.isdigit():
            st.session_state.cpf = cpf
            arq = f"cesta_{cpf}.json"
            if os.path.exists(arq):
                with open(arq,"r") as f:
                    st.session_state.carrinho = json.load(f)
            st.rerun()
        else:
            st.error("CPF inválido, 11 números")
    st.stop()

cpf = st.session_state.cpf

def salvar():
    with open(f"cesta_{cpf}.json","w") as f:
        json.dump(st.session_state.carrinho, f)

def add_produto(p):
    ean = p['ean']
    if ean in st.session_state.carrinho:
        st.session_state.carrinho[ean]['qtd'] += 1
    else:
        st.session_state.carrinho[ean] = {"dados": p, "qtd": 1}
    salvar()

def bip():
    st.markdown('<audio autoplay><source src="https://cdn.freesound.org/previews/4/4587_3198-lq.mp3"></audio>', unsafe_allow_html=True)

@st.cache_resource
def load_model():
    if os.path.exists("best.pt"):
        return YOLO("best.pt")
    else:
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

mapa_best = {
    "ketchup": "7896004700014",
    "agua": "7898915120015",
    "coca": "7894900011517",
    "maionese": "7893000291481",
    "oleo": "7892300000014",
    "limpol": "7896039710015",
    "baly": "7898915120040",
    "macarrao": "7898915120022",
    "tortilha": "7898915120060",
    "arroz": "7893500010001",
    "biscoito": "7896004000010",
    "cafe": "7896045500012",
    "esponja": "7898915120039",
}

col_top1, col_top2 = st.columns([3,1])
with col_top1:
    st.title("🛒 CLIENTE ATACADÃO")
with col_top2:
    st.write(f"CPF: **{cpf}**")
    if st.button("Sair"):
        st.session_state.cpf=None
        st.session_state.carrinho={}
        st.rerun()

html_flip = """
<div style="text-align:right; margin-bottom:5px;">
  <button id="btnFlip" style="padding:8px 14px; border-radius:20px; border:none; background:#000; color:#fff; font-weight:bold;">VIRAR CAMERA</button>
</div>
<script>
let facing = "environment";
document.getElementById('btnFlip').onclick = async () => {
  facing = facing === "environment"? "user" : "environment";
  try {
    const stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:facing}});
    stream.getTracks().forEach(t=>t.stop());
    alert("Camera virada para: " + facing);
  } catch(e) { alert("Nao deu: "+e.message); }
}
</script>
"""
components.html(html_flip, height=70)

foto = st.camera_input("📸 Aponte pro produto e bipa")
if foto:
    img = Image.open(foto)
    res = model(img, verbose=False, conf=0.80)[0]
    if res.boxes is not None and len(res.boxes)>0:
        best_box = max(res.boxes, key=lambda b: float(b.conf[0]))
        conf = float(best_box.conf[0])
        cls = int(best_box.cls[0])
        nome = model.names[cls].lower()
        st.write(f"Debug: {nome} - {conf:.2f}")
        bip()
        st.success(f"BIP! {nome} {conf:.0%}")
        sugestoes = []
        for chave, ean in mapa_best.items():
            if chave in nome:
                p = next((x for x in produtos if x["ean"]==ean), None)
                if p: sugestoes.append(p)
        if not sugestoes:
            sugestoes = produtos[:8]
        cols = st.columns(2)
        for i,p in enumerate(sugestoes[:8]):
            with cols[i%2]:
                if st.button(f"➕ {p['nome'][:22]}", key=f"add_{p['ean']}_{i}"):
                    add_produto(p); bip(); st.rerun()
    else:
        st.warning("Não detectei - use a lista abaixo")

st.divider()
st.subheader("📋 Todos os Produtos - Combo Box")
mapa = {f"{p['ean']} - {p['nome']} - R$ {p['preco']:.2f}": p for p in produtos}
sel = st.selectbox("Escolha:", list(mapa.keys()))
if st.button("➕ ADICIONAR", use_container_width=True):
    add_produto(mapa[sel]); bip(); st.rerun()

st.divider()
total = sum(v['dados']['preco']*v['qtd'] for v in st.session_state.carrinho.values())
st.subheader(f"🛒 Cesta - {len(st.session_state.carrinho)} tipos - R$ {total:.2f}")

if not st.session_state.carrinho:
    st.info("Cesta vazia")
else:
    h1,h2,h3,h4,h5 = st.columns([3,1,1,1,1])
    h1.markdown("**Produto**"); h2.markdown("**Preço**"); h3.markdown("**Qtd**"); h4.markdown("**Sub**"); h5.markdown("**+/-**")
    for ean, item in list(st.session_state.carrinho.items()):
        p = item['dados']; qtd = item['qtd']; sub = p['preco']*qtd
        c1,c2,c3,c4,c5 = st.columns([3,1,1,1,1])
        with c1: st.markdown(f"<div class='cesta-box'>{p['nome'][:25]}</div>", unsafe_allow_html=True)
        with c2: st.write(f"R$ {p['preco']:.2f}")
        with c3: st.write(f"**{qtd}**")
        with c4: st.write(f"R$ {sub:.2f}")
        with c5:
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("➖", key=f"menos_{ean}"):
                    if qtd>1: st.session_state.carrinho[ean]['qtd']-=1
                    else: del st.session_state.carrinho[ean]
                    salvar(); st.rerun()
            with cc2:
                if st.button("➕", key=f"mais_{ean}"):
                    st.session_state.carrinho[ean]['qtd']+=1
                    salvar(); st.rerun()
    if st.button("🗑️ Limpar Cesta", use_container_width=True):
        st.session_state.carrinho={}; salvar(); st.rerun()
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
        st.success(f"PAGO! R$ {total:.2f} - CPF {cpf}")
        st.balloons()
        st.session_state.carrinho={}; salvar()
