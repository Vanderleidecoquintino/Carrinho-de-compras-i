
st.markdown("""
<style>
/* FUNDO LIMPO - SEM GRADIENTE */
.stApp {
    background-color: #FFFFFF;
}

/* TÍTULO PRINCIPAL - LARANJA ATACADÃO */
h1 {
    background-color: #FF6600 !important;
    color: white !important;
    padding: 16px 20px !important;
    border-radius: 12px !important;
    text-align: center !important;
    font-weight: 800 !important;
    font-size: 26px !important;
    letter-spacing: 0.5px;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 12px rgba(255,102,0,0.3);
}
h2, h3 {
    color: #1A1A1A !important;
    font-weight: 700 !important;
    margin-top: 15px !important;
}

/* TEXTOS PRETOS LEGÍVEIS */
p, span, label, div[data-testid="stMarkdownContainer"] {
    color: #222222 !important;
    font-weight: 500 !important;
}

/* BOTÕES - PADRÃO ATACADÃO */
.stButton > button {
    background-color: #FF6600 !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 12px !important;
    transition: 0.2s;
    box-shadow: 0 2px 8px rgba(255,102,0,0.25);
}
.stButton > button:hover {
    background-color: #E55A00 !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background-color: #000000 !important;
    font-size: 16px !important;
    height: 55px !important;
}

/* CAIXA DA CESTA - ORGANIZADA */
.cesta-box {
    background: #FFF8F2;
    padding: 12px 15px;
    border-radius: 10px;
    border-left: 4px solid #FF6600;
    margin-bottom: 8px;
    color: #000 !important;
    font-weight: 600 !important;
}

/* INPUT CPF E SELECT */
div[data-baseweb="input"], div[data-baseweb="select"] {
    border-radius: 10px !important;
}

/* ESCONDE MENU FEIO */
#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
