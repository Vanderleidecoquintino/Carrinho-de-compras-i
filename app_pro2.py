foto = st.camera_input("📸 Aponte pro produto e bipa")
if foto:
    img = Image.open(foto)
    res = model(img, verbose=False, conf=0.80)[0] # 0.80 pra parar de ver relógio

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
            st.warning("Detectei mas não tá no mapa - usando lista geral")
            sugestoes = produtos[:8]

        cols = st.columns(2)
        for i,p in enumerate(sugestoes[:8]):
            with cols[i%2]:
                # KEY FIXA SEM RANDOM - ISSO CONSERTA O ADD
                if st.button(f"➕ {p['nome'][:22]}", key=f"add_cam_{p['ean']}_{i}"):
                    add_produto(p)
                    bip()
                    st.rerun()
    else:
        st.warning("Não detectei - use a lista abaixo")
