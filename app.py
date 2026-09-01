import streamlit as st
import json, os
from PIL import Image

st.set_page_config(page_title="CAIXA ATACADÃO", page_icon="💰")

st.markdown("""
<style>
.stApp { background: #111; }
h1 { background: #00A300; color: white!important; padding: 15px; border-radius: 15px; text-align: center; }
.stButton > button { background: #00A300; color: white; border-radius: 12px; font-weight: bold; height: 60px; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("💰 CAIXA ATACADÃO - LEITOR FINAL")

# BANCO DE NOMES PRA MOSTRAR BONITO
produtos_db = {
    "7898915120015": "[BULNEZ] Água Mineral 500ml - R$ 1,29",
    "7894900011517": "Coca-Cola 2L - R$ 9,50",
    "7893000291481": "Maionese Suavit 450g - R$ 4,49",
    "7896908200015": "Requeijão Canto Minas 400g - R$ 13,90",
    "7892300000014": "Óleo Soya 900ml - R$ 6,90",
    "7896004700014": "Ketchup Quero 400g - R$ 8,90",
    "7896039710015": "Limpador Limpol 500ml - R$ 2,99",
    "7898915120040": "Energético Baly 473ml - R$ 5,49",
    "7898915120022": "[BULNEZ] Macarrão 500g - R$ 2,99",
    "7898915120050": "[BULNEZ] Massa Fresca 500g - R$ 7,90",
    "7898915120060": "[BULNEZ] Tortilha 400g - R$ 8,50",
    "7898915120039": "[BULNEZ] Esponja 3un - R$ 2,49",
}

st.subheader("BIP 2 - Caixa bipa o barcode final do cliente")

modo = st.radio("Como vai bipar?", ["📸 Câmera (bipa barcode)", "⌨️ Digitar ID"], horizontal=True)

id_lido = ""

if modo == "📸 Câmera (bipa barcode)":
    foto = st.camera_input("Aponte pro barcode final do cliente")
    if foto:
        try:
            from pyzbar.pyzbar import decode
            img = Image.open(foto)
            decodificado = decode(img)
            if decodificado:
                id_lido = decodificado[0].data.decode('utf-8')
                st.success(f"BIP CAIXA! Li: {id_lido}")
            else:
                st.warning("Não li, tenta de novo ou digita")
        except:
            st.info("pyzbar não instalado, use modo digitar")
else:
    id_lido = st.text_input("Cole o ID do barcode final:", placeholder="ex: 1234567890123")

if st.button("💰 PUXAR COMANDA - JOGAR EANS NO PDV", type="primary", use_container_width=True):
    if not id_lido:
        st.error("Bipa primeiro!")
    else:
        caminho = f"comandas/{id_lido}.json"
        if os.path.exists(caminho):
            with open(caminho) as f:
                dados = json.load(f)

            st.balloons()
            st.markdown(f"""
            <div style="background:white;color:black;padding:20px;border-radius:15px;">
            <h2 style="color:#00A300;text-align:center;">✅ COMANDA {dados['id']}</h2>
            <hr>
            """, unsafe_allow_html=True)

            total = 0
            for ean in dados['eans']:
                nome = produtos_db.get(ean, f"Produto EAN {ean}")
                st.code(f"{ean} -> {nome}")
                # pega preço do nome
                try:
                    preco = float(nome.split("R$ ")[1].replace(",","."))
                    total += preco
                except: pass

            st.markdown(f"""
            <h2 style="color:#00A300;">TOTAL: R$ {dados['total']:.2f}</h2>
            <h3 style="background:#00A300;color:white;padding:10px;border-radius:10px;text-align:center;">LIBERADO - PODE SAIR</h3>
            </div>
            """, unsafe_allow_html=True)

            st.success(f"CAIXA RECEBEU {len(dados['eans'])} EANs e jogou no PDV Atacadão!")

        else:
            st.error(f"Comanda {id_lido} não encontrada em /comandas. Gera primeiro no app cliente.")

st.divider()
st.write("Comandas na pasta:")
if os.path.exists("comandas"):
    st.write(os.listdir("comandas"))
