import streamlit as st

st.set_page_config(page_title="Simulador de Comissão", layout="wide")

st.title("📊 Simulador de Comissão - Equipe")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("👤 Luis Felipe")
    t1 = st.number_input("Transportadoras (Luis Felipe)", 0)
    e1 = st.number_input("Embarcadores (Luis Felipe)", 0)
    c1 = st.number_input("Coringas (Luis Felipe)", 0)

with col2:
    st.header("👤 Fernando")
    t2 = st.number_input("Transportadoras (Fernando)", 0)
    e2 = st.number_input("Embarcadores (Fernando)", 0)
    c2 = st.number_input("Coringas (Fernando)", 0)

with col3:
    st.header("👤 Outro")
    t3 = st.number_input("Transportadoras (Outro)", 0)
    e3 = st.number_input("Embarcadores (Outro)", 0)
    c3 = st.number_input("Coringas (Outro)", 0)

st.divider()

sf = st.number_input("📈 Success Fee (% da meta do time)", 0)

if st.button("Calcular"):

    t = t1 + t2 + t3
    e = e1 + e2 + e3
    c = c1 + c2 + c3

    melhorBonus = 0
    melhorFaixa = "Abaixo da meta"
    melhorT = t
    melhorE = e

    for i in range(c + 1):
        tFinal = t + i
        eFinal = e + (c - i)

        bonus = 0
        faixa = ""

        if tFinal >= 50 and eFinal >= 20:
            bonus = 1000
            faixa = "Faixa 4"
        elif tFinal >= 40 and eFinal >= 16:
            bonus = 800
            faixa = "Faixa 3"
        elif tFinal >= 30 and eFinal >= 12:
            bonus = 600
            faixa = "Faixa 2"
        elif tFinal >= 20 and eFinal >= 8:
            bonus = 400
            faixa = "Faixa 1"

        if bonus > melhorBonus:
            melhorBonus = bonus
            melhorFaixa = faixa
            melhorT = tFinal
            melhorE = eFinal

    bonusSF = 0
    nivelSF = "Não atingido"

    if sf >= 150:
        bonusSF = 500
        nivelSF = "150%"
    elif sf >= 120:
        bonusSF = 300
        nivelSF = "120%"
    elif sf >= 100:
        bonusSF = 200
        nivelSF = "100%"

    base1 = (t1 + e1 + c1) * 50
    base2 = (t2 + e2 + c2) * 50
    base3 = (t3 + e3 + c3) * 50

    total1 = base1 + melhorBonus + bonusSF
    total2 = base2 + melhorBonus + bonusSF
    total3 = base3 + melhorBonus + bonusSF

    st.subheader("📊 Resultado do Time")
    st.write(f"Faixa: {melhorFaixa}")
    st.write(f"Transportadoras: {melhorT}")
    st.write(f"Embarcadores: {melhorE}")
    st.write(f"Bônus Faixa (por pessoa): R$ {melhorBonus}")
    st.write(f"Success Fee: {nivelSF} (R$ {bonusSF})")

    st.divider()

    def mostrar(nome, t, e, c, base, total):
        st.subheader(f"👤 {nome}")
        st.write(f"Transportadoras: {t}")
        st.write(f"Embarcadores: {e}")
        st.write(f"Coringas: {c}")
        st.write(f"Total de contratos: {t+e+c}")
        st.write(f"Comissão: R$ {base}")
        st.write(f"Bônus Faixa: R$ {melhorBonus}")
        st.write(f"Success Fee: R$ {bonusSF}")
        st.success(f"Total: R$ {total}")

    col1, col2, col3 = st.columns(3)

    with col1:
        mostrar("Luis Felipe", t1, e1, c1, base1, total1)

    with col2:
        mostrar("Fernando", t2, e2, c2, base2, total2)

    with col3:
        mostrar("Outro", t3, e3, c3, base3, total3)
