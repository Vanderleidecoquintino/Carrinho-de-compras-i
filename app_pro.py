import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
from ultralytics import YOLO

st.set_page_config(page_title="CestaCheck PRO", layout="wide", page_icon="🛒")

# --- ESTILO PRO QUE IMPRESSIONA CLIENTE ---
st.markdown("""
<style>
.metric-card { background: #f0f9ff; padding: 20px; border-radius: 15px; border-left: 5px solid #0066ff; }
</style>
""", unsafe_allow_html=True)

st.title("🛒 CestaCheck PRO - Auditoria Inteligente")
st.caption("Sistema com 250 produtos cadastrados | Detecção automática")

@st.cache_data
def carregar_produtos():
    try:
        return pd.read_csv("produtos.csv", encoding='utf-8-sig')
    except:
        return pd.read_csv("produtos.csv")

@st.cache_resource
def carregar_modelo():
    return YOLO("yolov8n.pt") # ou seu best.pt

tabela = carregar_produtos()
modelo = carregar_modelo()

# --- MAPA INTELIGENTE ---
# Pega os nomes em inglês do YOLO e linka com nome real
mapa_preco = dict(zip(tabela['nome_busca'], tabela['preco']))
mapa_nome = dict(zip(tabela['nome_busca'], tabela['nome_real']))

uploaded = st.file_uploader("📸 Tire foto da cesta", type=["jpg","png","jpeg"])

if uploaded:
    col1, col2 = st.columns(2)
    img = Image.open(uploaded)
    col1.image(img, caption="Foto enviada", use_container_width=True)

    # DETECÇÃO
    results = modelo(img)
    detections = []
    for r in results:
        for box in r.boxes:
            cls = modelo.names[int(box.cls[0])]
            # FILTRA SÓ O QUE TEM NA NOSSA PLANILHA
            if cls in mapa_preco:
                detections.append({
                    "Produto": mapa_nome.get(cls, cls),
                    "Categoria": tabela[tabela['nome_busca']==cls].iloc[0]['categoria'],
                    "Total": mapa_preco[cls],
                    "Confianca": f"{float(box.conf[0])*100:.1f}%"
                })

    if detections:
        df = pd.DataFrame(detections)
        # Se detectar 2 cafes pilão, soma
        df_group = df.groupby("Produto").agg({"Total":"sum","Categoria":"first"}).reset_index()
        total = df_group["Total"].sum()

        col2.metric("💰 Valor Total Auditado", f"R$ {total:.2f}")
        col2.metric("📦 Itens Detectados", f"{len(df_group)} produtos")
        col2.dataframe(df_group, use_container_width=True, hide_index=True)

        # --- PDF QUE NÃO QUEBRA MAIS ---
        def gerar_pdf(df_final, total_final):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 12, "CestaCheck PRO - Relatorio Oficial", ln=True, align='C')
            pdf.set_font("Arial", '', 11)
            pdf.ln(5)
            pdf.cell(0, 8, f"Total de produtos: {len(df_final)}", ln=True)
            pdf.cell(0, 8, f"Valor total: R$ {total_final:.2f}", ln=True)
            pdf.ln(8)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, "Itens auditados:", ln=True)
            pdf.set_font("Arial", '', 10)
            for _, row in df_final.iterrows():
                txt = f"{str(row['Produto'])[:50]} - R$ {row['Total']:.2f}"
                txt = txt.encode('latin-1','replace').decode('latin-1')
                pdf.cell(0, 7, txt, ln=True)
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(0, 10, f"TOTAL FINAL: R$ {total_final:.2f}", ln=True, align='R')

            out = pdf.output(dest='S')
            # CORREÇÃO DO ERRO QUE VC TAVA TENDO
            if isinstance(out, str):
                return out.encode('latin-1','replace')
            return bytes(out)

        pdf_bytes = gerar_pdf(df_group, total)
        st.download_button("📄 BAIXAR PDF OFICIAL (sem erro)", data=pdf_bytes, file_name="relatorio_cestacheck_pro.pdf", mime="application/pdf", type="primary")

        st.success("✅ Pronto pra mostrar pro cliente e ele cair duro!")
    else:
        st.warning("Nenhum produto da nossa base de 250 detectado. Verifique o modelo YOLO.")
