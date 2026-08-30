
import streamlit as st
from ultralytics import YOLO
import cv2, numpy as np
from PIL import Image
import pandas as pd
from fpdf import FPDF
import datetime

st.set_page_config(page_title="CestaCheck PRO", page_icon="📦", layout="wide")
st.title("📦 CestaCheck PRO")

MAPA = {
    "rice bag": "arroz", "beans bag": "feijao", "sugar bag": "acucar",
    "coffee bag": "cafe", "milk carton": "leite", "cooking oil bottle": "oleo",
    "pasta bag": "macarrao", "sardine can": "sardinha", "flour bag": "farinha",
    "biscuit pack": "biscoito", "butter pack": "manteiga", "chocolate powder box": "achocolatado"
}
TABELA_PRECO = {
    "arroz": 29.90, "feijao": 9.50, "acucar": 5.29, "cafe": 18.90,
    "leite": 4.99, "oleo": 8.49, "macarrao": 4.20, "sardinha": 5.99,
    "farinha": 6.50, "biscoito": 4.80, "manteiga": 7.20, "achocolatado": 9.90
}

def gerar_pdf(df, total, faltas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "CestaCheck PRO - Relatorio", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | Total: R$ {total:.2f}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Produto", 1); pdf.cell(40, 10, "Status", 1); pdf.cell(40, 10, "Preco", 1); pdf.ln()
    pdf.set_font("Arial", '', 11)
    for _, row in df.iterrows():
        pdf.cell(60, 9, row['Produto'], 1); pdf.cell(40, 9, row['Status'], 1); pdf.cell(40, 9, row['Preco'], 1); pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, f"Itens em falta: {', '.join(faltas) if faltas else 'Nenhum'}", ln=True)
    return pdf.output(dest='S').encode('latin1')

@st.cache_resource
def carrega_modelo():
    m = YOLOWorld('yolov8s-worldv2.pt')
    m.set_classes(list(MAPA.keys()))
    return m

model = carrega_modelo()
arquivo = st.file_uploader("📸 Arraste a foto da cesta aqui", type=["jpg","png","jpeg"])

if arquivo:
    img = Image.open(arquivo).convert("RGB")
    results = model.predict(np.array(img), conf=0.10, verbose=False)
    img_plot = np.array(img).copy()
    itens_pt, total = [], 0
    if results[0].boxes is not None:
        for box in results[0].boxes:
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            nome_pt = MAPA.get(results[0].names[int(box.cls[0])], "item")
            preco = TABELA_PRECO.get(nome_pt, 0)
            itens_pt.append(nome_pt); total += preco
            cv2.rectangle(img_plot, (x1,y1), (x2,y2), (0,200,0), 3)
            cv2.putText(img_plot, f"{nome_pt} R$ {preco:.2f}", (x1, y1-10), 0, 0.7, (0,200,0), 2)
    col1, col2 = st.columns([1.2, 1])
    col1.image(img_plot, use_column_width=True)
    col1.metric("Valor Total na Cesta", f"R$ {total:.2f}")
    faltas = [p for p in TABELA_PRECO if p not in itens_pt]
    dados = [{"Produto": p, "Status": "OK" if p in itens_pt else "FALTA", "Preco": f"R$ {TABELA_PRECO[p]:.2f}"} for p in TABELA_PRECO]
    df = pd.DataFrame(dados)
    col2.dataframe(df, use_container_width=True, hide_index=True)
    pdf_bytes = gerar_pdf(df, total, faltas)
    col2.download_button("📄 Baixar Relatorio PDF", data=pdf_bytes, file_name="Relatorio.pdf", mime="application/pdf", type="primary")
