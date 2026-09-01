import streamlit as st
from ultralytics import YOLOWorld
import cv2

# 1. SEUS 18 PRODUTOS
produtos = [
    {"nome":"[BULNEZ] Água Mineral 500ml","preco":1.29,"ean":"7898915120015"},
    {"nome":"Coca-Cola 2L","preco":9.50,"ean":"7894900011517"},
    {"nome":"Maionese Suavit 450g","preco":4.49,"ean":"7893000291481"},
    {"nome":"Requeijão Canto Minas 400g","preco":13.90,"ean":"7896908200015"},
    {"nome":"Óleo Soya 900ml","preco":6.90,"ean":"7892300000014"},
    {"nome":"Ketchup Quero 400g","preco":8.90,"ean":"7896004700014"},
    {"nome":"Limpador Limpol 500ml","preco":2.99,"ean":"7896039710015"},
    {"nome":"Energético Baly 473ml","preco":5.49,"ean":"7898915120040"},
    {"nome":"[BULNEZ] Macarrão 500g","preco":2.99,"ean":"7898915120022"},
    {"nome":"[BULNEZ] Massa Fresca 500g","preco":7.90,"ean":"7898915120050"},
    {"nome":"[BULNEZ] Tortilha 400g","preco":8.50,"ean":"7898915120060"},
    {"nome":"Arroz Tio João 5kg","preco":27.90,"ean":"7893500010001"},
    {"nome":"Biscoito Vitarella 350g","preco":4.99,"ean":"7896004000010"},
    {"nome":"Café Bom Jesus 250g","preco":12.98,"ean":"7896045500012"},
    {"nome":"Chocolate Harald 500g","preco":59.90,"ean":"7896063800011"},
    {"nome":"Suco Subello 200ml","preco":1.49,"ean":"7898951000015"},
    {"nome":"[BULNEZ] Esponja 3un","preco":2.49,"ean":"7898915120039"},
    {"nome":"Feijão Kicaldo 1kg","preco":7.50,"ean":"7896101000013"},
]

# 2. YOLO-WORLD - ZERO-SHOT
@st.cache_resource
def load_model():
    model = YOLOWorld("yolov8s-worldv2.pt") # baixa sozinho na 1ª vez
    classes = [p["nome"] for p in produtos]
    model.set_classes(classes)
    return model

model = load_model()

# 3. INTERFACE
st.title("Teste YOLO-World - Só EAN")

img = st.camera_input("Aponte pro produto")

if img:
    results = model.predict(img, conf=0.2)

    for box in results[0].boxes:
        cls_id = int(box.cls)
        produto = produtos[cls_id]

        # Botão já com EAN igual Atacadão
        if st.button(f"➕ {produto['ean']} | {produto['nome']} - R$ {produto['preco']:.2f}", key=produto['ean']):
            st.success(f"Adicionado: {produto['ean']}")
            st.session_state.carrinho.append(produto)

# 4. CARRINHO - MOSTRA EAN
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if st.session_state.carrinho:
    st.divider()
    for it in st.session_state.carrinho:
        st.write(f"- {it['ean']} | {it['nome']} R$ {it['preco']:.2f}")
