import streamlit as st

st.set_page_config(
    page_title="Simulador de Comissão",
    layout="wide",
    page_icon="📊"
)

# =========================
# ESTILO (CSS)
# =========================
st.markdown("""
<style>
.main {
    background-color: #0f172a;
    color: white;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
.title {
    font-size: 26px;
    font-weight: bold;
}
.highlight {
    font-size: 22px;
    color: #22c55e;
    font-weight: bold;
}
.warning {
    color: #f59e0b;
    font-weight: bold;
}
.danger {
    color: #ef4444;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">📊 Simulador de Comissão - Equipe</p>', unsafe_allow_html=True)

# =========================
# INPUTS
# =========================
col1, col2, col3 = st.columns(3)

def input_card(nome):
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.subheader(f"👤 {nome}")
    t = st.number_input(f"Transportadoras - {nome}", 0, key=f"t_{nome}")
    e = st.number_input(f"Embarcadores - {nome}", 0, key=f"e_{nome}")
    c = st.number_input(f"Coringas - {nome}", 0, key=f"c_{nome}")
    st.markdown('</div>', unsafe_allow_html=True)
    return t, e, c

with col1:
    t1, e1, c1 = input_card("Luis Felipe")

with col2:
    t2, e2, c2 = input_card("Fernando")

with col3:
    t3, e3, c3 = input_card("Outro")

st.divider()

sf = st.slider("📈 Success Fee (% da meta)", 0, 200, 0)

# =========================
# CÁLCULO
# =========================
if st.button("🚀 Calcular"):

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

    # SUCCESS FEE
    if sf >= 150:
        bonusSF = 500
        nivelSF = "🔥 150%"
    elif sf >= 120:
        bonusSF = 300
        nivelSF = "🚀 120%"
    elif sf >= 100:
        bonusSF = 200
        nivelSF = "✅ 100%"
    else:
        bonusSF = 0
        nivelSF = "❌ Não atingido"

    # BASE
    base1 = (t1 + e1 + c1) * 50
    base2 = (t2 + e2 + c2) * 50
    base3 = (t3 + e3 + c3) * 50

    total1 = base1 + melhorBonus + bonusSF
    total2 = base2 + melhorBonus + bonusSF
    total3 = base3 + melhorBonus + bonusSF

    # =========================
    # HEADER RESULTADO
    # =========================
    st.divider()
    st.subheader("📊 Resultado do Time")

    colA, colB, colC = st.columns(3)

    colA.metric("Faixa", melhorFaixa)
    colB.metric("Transportadoras", melhorT)
    colC.metric("Embarcadores", melhorE)

    st.markdown(f'<p class="highlight">💰 Bônus Faixa: R$ {melhorBonus}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="highlight">📈 Success Fee: {nivelSF} | R$ {bonusSF}</p>', unsafe_allow_html=True)

    st.divider()

    # =========================
    # CARDS INDIVIDUAIS
    # =========================
    def resultado(nome, t, e, c, base, total):
        cor = "highlight"
        if total < 2000:
            cor = "danger"
        elif total < 4000:
            cor = "warning"

        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.subheader(f"👤 {nome}")
        st.write(f"Transportadoras: {t}")
        st.write(f"Embarcadores: {e}")
        st.write(f"Coringas: {c}")
        st.write(f"Total de contratos: {t+e+c}")
        st.write(f"Comissão: R$ {base}")
        st.write(f"Bônus Faixa: R$ {melhorBonus}")
        st.write(f"Success Fee: R$ {bonusSF}")
        st.markdown(f'<p class="{cor}">💰 Total: R$ {total}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        resultado("Luis Felipe", t1, e1, c1, base1, total1)

    with col2:
        resultado("Fernando", t2, e2, c2, base2, total2)

    with col3:
        resultado("Outro", t3, e3, c3, base3, total3)
