import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# CSS PROFISSIONAL LIMPO
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
    padding:22px;
    border-radius:16px;
    margin-bottom:14px;
}

.title {
    font-size:20px;
    font-weight:600;
}

.value {
    font-size:30px;
    font-weight:bold;
}

.small {
    font-size:14px;
    opacity:0.8;
}

.ok {color:#3b82f6;}     /* azul */
.warn {color:#60a5fa;}   /* azul claro */
.bad {color:#ef4444;}    /* vermelho (só quando necessário) */
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial - Comissão")

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

sf = st.slider("📈 Success Fee (%)", 0, 200, 0)

# =========================
# CORINGA INTELIGENTE
# =========================
def calcular_melhor_cenario(t, e, c):
    melhor_bonus = 0
    melhor_faixa = "Abaixo"
    usado_t = 0
    usado_e = 0

    for i in range(c + 1):
        tF = t + i
        eF = e + (c - i)

        if tF >= 50 and eF >= 20:
            return 1000, "Faixa 4", i, c - i
        elif tF >= 40 and eF >= 16 and melhor_bonus < 800:
            melhor_bonus, melhor_faixa, usado_t, usado_e = 800, "Faixa 3", i, c - i
        elif tF >= 30 and eF >= 12 and melhor_bonus < 600:
            melhor_bonus, melhor_faixa, usado_t, usado_e = 600, "Faixa 2", i, c - i
        elif tF >= 20 and eF >= 8 and melhor_bonus < 400:
            melhor_bonus, melhor_faixa, usado_t, usado_e = 400, "Faixa 1", i, c - i

    return melhor_bonus, melhor_faixa, usado_t, usado_e

# =========================
# CALCULO PRINCIPAL
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

    # =========================
    # KPIs METAS
    # =========================
    st.subheader("🎯 Metas do Time")

    def percent(atual, meta):
        return min(100, int((atual/meta)*100)) if meta > 0 else 0

    colA, colB, colC = st.columns(3)

    colA.markdown(f"""
    <div class="card">
        <div class="title">Transportadoras</div>
        <div class="value ok">{final_t} / 50</div>
        <div class="small">{percent(final_t,50)}% atingido</div>
        <div class="small">Falta: {max(0,50-final_t)}</div>
    </div>
    """, unsafe_allow_html=True)

    colB.markdown(f"""
    <div class="card">
        <div class="title">Embarcadores</div>
        <div class="value ok">{final_e} / 20</div>
        <div class="small">{percent(final_e,20)}% atingido</div>
        <div class="small">Falta: {max(0,20-final_e)}</div>
    </div>
    """, unsafe_allow_html=True)

    colC.markdown(f"""
    <div class="card">
        <div class="title">Faixa</div>
        <div class="value ok">{faixa}</div>
        <div class="small">Bônus: R$ {bonus}</div>
        <div class="small">Success Fee: R$ {bonusSF}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
    <div class="title">Uso de Coringas</div>
    <div class="small">
    ➜ +{usado_t} Transportadoras<br>
    ➜ +{usado_e} Embarcadores
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
        ]
    }).sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")

    st.dataframe(ranking, use_container_width=True)

    top = ranking.iloc[0]

    st.success(f"🔥 Top Performer: {top['Pessoa']}")

    # =========================
    # RESULTADO INDIVIDUAL
    # =========================
    st.subheader("💰 Resultado Individual")

    def calc_ind(t, e, c):
        base = (t + e + c) * 50
        return base + bonus + bonusSF

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    cards = ""

    for nome, t, e, c in pessoas:

        total = calc_ind(t, e, c)

        cards += f"""
        <div class="card">
            <div class="title">{nome}</div>

            <div class="value">{t+e+c} contratos</div>

            <div class="small">
            🚚 Transportadoras: {t}<br>
            📦 Embarcadores: {e}<br>
            🔁 Coringas: {c}
            </div>

            <div class="value ok">
            💰 R$ {total}
            </div>
        </div>
        """

    st.markdown(cards, unsafe_allow_html=True)
