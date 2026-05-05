import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# CSS LIMPO E PROFISSIONAL
# =========================
st.markdown("""
<style>
.main {background-color:#0f172a;color:white;}

.block-container {
    padding-top:2rem;
    max-width:1200px;
}

.card {
    background:#1e293b;
    padding:25px;
    border-radius:16px;
    margin-bottom:15px;
}

.kpi {
    font-size:28px;
    font-weight:bold;
}

.ok {color:#3b82f6;}     /* azul */
.warn {color:#60a5fa;}   /* azul claro */
.bad {color:#ef4444;}    /* vermelho */

.title {
    font-size:22px;
    margin-bottom:10px;
}

.value {
    font-size:32px;
    font-weight:bold;
}

.small {
    font-size:16px;
    opacity:0.8;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial")

# =========================
# INPUTS
# =========================
col1, col2, col3 = st.columns(3)

def input_user(nome):
    st.subheader(nome)
    t = st.number_input(f"Transportadoras - {nome}", 0)
    e = st.number_input(f"Embarcadores - {nome}", 0)
    c = st.number_input(f"Coringas - {nome}", 0)
    return t, e, c

with col1:
    t1, e1, c1 = input_user("Luis Felipe")

with col2:
    t2, e2, c2 = input_user("Fernando")

with col3:
    t3, e3, c3 = input_user("Outro")

sf = st.slider("Success Fee (%)", 0, 200, 0)

# =========================
# CORINGA INTELIGENTE
# =========================
def calcular_melhor_cenario(t, e, c):
    melhor_bonus = 0
    melhor_faixa = "Abaixo"
    melhor_i = 0

    for i in range(c + 1):
        tF = t + i
        eF = e + (c - i)

        if tF >= 50 and eF >= 20:
            return 1000, "Faixa 4", i, c - i
        elif tF >= 40 and eF >= 16 and melhor_bonus < 800:
            melhor_bonus, melhor_faixa, melhor_i = 800, "Faixa 3", i
        elif tF >= 30 and eF >= 12 and melhor_bonus < 600:
            melhor_bonus, melhor_faixa, melhor_i = 600, "Faixa 2", i
        elif tF >= 20 and eF >= 8 and melhor_bonus < 400:
            melhor_bonus, melhor_faixa, melhor_i = 400, "Faixa 1", i

    return melhor_bonus, melhor_faixa, melhor_i, c - melhor_i

# =========================
# CALCULAR
# =========================
if st.button("Calcular"):

    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    bonus, faixa, usado_t, usado_e = calcular_melhor_cenario(total_t, total_e, total_c)

    final_t = total_t + usado_t
    final_e = total_e + usado_e

    # SUCCESS FEE
    if sf >= 150:
        bonusSF = 500
    elif sf >= 120:
        bonusSF = 300
    elif sf >= 100:
        bonusSF = 200
    else:
        bonusSF = 0

    def calc_ind(t, e, c):
        base = (t + e + c) * 50
        return base + bonus + bonusSF

    total1 = calc_ind(t1, e1, c1)
    total2 = calc_ind(t2, e2, c2)
    total3 = calc_ind(t3, e3, c3)

    # =========================
    # KPI METAS
    # =========================
    st.subheader("🎯 Metas do Time")

    def status(valor, meta):
        if valor >= meta:
            return "ok"
        elif valor >= meta * 0.7:
            return "warn"
        return "bad"

    colA, colB, colC = st.columns(3)

    colA.markdown(f"""
    <div class="card">
        <div class="title">Transportadoras</div>
        <div class="value {status(final_t,50)}">{final_t} / 50</div>
    </div>
    """, unsafe_allow_html=True)

    colB.markdown(f"""
    <div class="card">
        <div class="title">Embarcadores</div>
        <div class="value {status(final_e,20)}">{final_e} / 20</div>
    </div>
    """, unsafe_allow_html=True)

    colC.markdown(f"""
    <div class="card">
        <div class="title">Faixa atingida</div>
        <div class="value ok">{faixa}</div>
        <div class="small">Bônus: R$ {bonus}</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # CORINGAS
    # =========================
    st.markdown(f"""
    <div class="card">
    <div class="title">Uso dos Coringas</div>
    <div class="small">
    +{usado_t} em Transportadoras<br>
    +{usado_e} em Embarcadores
    </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # RANKING
    # =========================
    ranking = pd.DataFrame({
        "Pessoa": ["Luis Felipe","Fernando","Outro"],
        "Contratos": [
            t1 + e1 + c1,
            t2 + e2 + c2,
            t3 + e3 + c3
        ],
        "Total (R$)": [total1, total2, total3]
    }).sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")

    st.dataframe(ranking, use_container_width=True)

    top = ranking.iloc[0]

    st.markdown(f"""
    <div class="card">
        <div class="title">Top Performer</div>
        <div class="value ok">{top['Pessoa']}</div>
        <div class="small">{top['Contratos']} contratos</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # RESULTADO INDIVIDUAL
    # =========================
    st.subheader("💰 Resultado Individual")

    def card(nome, total):
        st.markdown(f"""
        <div class="card">
            <div class="title">{nome}</div>
            <div class="value">R$ {total}</div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        card("Luis Felipe", total1)
    with col2:
        card("Fernando", total2)
    with col3:
        card("Outro", total3)
