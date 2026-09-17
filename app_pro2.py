import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Carrinho Inteligente", page_icon="🛒", layout="centered")
st.title("🛒 Carrinho de Compras Inteligente")

# --- 1. SESSÃO CPF ---
if "cpf_logado" not in st.session_state:
    st.session_state.cpf_logado = None
if "cesta" not in st.session_state:
    st.session_state.cesta = []

if not st.session_state.cpf_logado:
    st.subheader("👤 Entrar com CPF")
    cpf = st.text_input("Digite seu CPF (só números):", max_chars=11)
    if st.button("Entrar", type="primary"):
        if len(cpf) == 11 and cpf.isdigit():
            st.session_state.cpf_logado = cpf
            # Carregar cesta se já existir
            arquivo = f"cesta_{cpf}.json"
            if os.path.exists(arquivo):
                with open(arquivo, "r") as f:
                    st.session_state.cesta = json.load(f)
            st.success("Logado com sucesso!")
            st.rerun()
        else:
            st.error("CPF inválido! Digite 11 números.")
    st.stop()

cpf = st.session_state.cpf_logado
st.success(f"Logado como: {cpf} ")
if st.button("Sair / Trocar CPF"):
    st.session_state.cpf_logado = None
    st.session_state.cesta = []
    st.rerun()

st.divider()

# --- 2. PRODUTOS ---
try:
    produtos = pd.read_csv("carrinho.csv")
except:
    st.error("Arquivo carrinho.csv não encontrado no GitHub!")
    st.stop()

st.subheader("📦 Produtos")
for i, row in produtos.iterrows():
    col1, col2 = st.columns([4,1])
    with col1:
        st.write(f"**{row['produto']}** - R$ {float(row['preco']):.2f}")
    with col2:
        if st.button("Adicionar", key=f"add_{i}"):
            st.session_state.cesta.append({"produto": row['produto'], "preco": float(row['preco'])})
            # Salva
            with open(f"cesta_{cpf}.json", "w") as f:
                json.dump(st.session_state.cesta, f)
            st.toast(f"{row['produto']} adicionado!")
            st.rerun()

st.divider()

# --- 3. CESTA ---
st.subheader(f"🧺 Sua Cesta ({len(st.session_state.cesta)} itens)")
if not st.session_state.cesta:
    st.info("Cesta vazia")
else:
    total = 0
    for idx, item in enumerate(list(st.session_state.cesta)):
        c1, c2, c3 = st.columns([3,1,1])
        with c1: st.write(item['produto'])
        with c2: st.write(f"R$ {item['preco']:.2f}")
        with c3:
            if st.button("Remover", key=f"rem_{idx}"):
                st.session_state.cesta.pop(idx)
                with open(f"cesta_{cpf}.json", "w") as f:
                    json.dump(st.session_state.cesta, f)
                st.rerun()
        total += float(item['preco'])
    
    st.metric("Total a pagar", f"R$ {total:.2f}")
    if st.button("Limpar tudo"):
        st.session_state.cesta = []
        if os.path.exists(f"cesta_{cpf}.json"):
            os.remove(f"cesta_{cpf}.json")
        st.rerun()
