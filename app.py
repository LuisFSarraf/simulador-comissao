import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# CSS (UI PREMIUM)
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

[data-testid="stMetric"] {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.4);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial - Simulador de Comissão")

# =========================
# BASE
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "data", "pessoa", "transportadora", "embarcador", "coringa"
    ])

# =========================
# INPUTS
# =========================
col1, col2, col3 = st.columns(3)

def input_user(nome):
    st.subheader(f"👤 {nome}")
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

st.divider()

sf = st.slider("📈 Success Fee (%)", 0, 200, 0)

# =========================
# SALVAR
# =========================
if st.button("💾 Salvar Dia"):
    hoje = datetime.now().strftime("%Y-%m-%d")

    novos = pd.DataFrame([
        [hoje, "Luis Felipe", t1, e1, c1],
        [hoje, "Fernando", t2, e2, c2],
        [hoje, "Outro", t3, e3, c3],
    ], columns=["data", "pessoa", "transportadora", "embarcador", "coringa"])

    st.session_state.dados = pd.concat([st.session_state.dados, novos])
    st.success("Dados salvos!")

# =========================
# BONUS
# =========================
def calcular_bonus(t, e, c):
    melhorBonus = 0
    melhorFaixa = "Abaixo da meta"

    for i in range(c+1):
        tF = t + i
        eF = e + (c - i)

        if tF >= 50 and eF >= 20:
            return 1000, "Faixa 4"
        elif tF >= 40 and eF >= 16:
            melhorBonus, melhorFaixa = 800, "Faixa 3"
        elif tF >= 30 and eF >= 12:
            melhorBonus, melhorFaixa = 600, "Faixa 2"
        elif tF >= 20 and eF >= 8:
            melhorBonus, melhorFaixa = 400, "Faixa 1"

    return melhorBonus, melhorFaixa

# =========================
# CALCULAR
# =========================
if st.button("🚀 Calcular"):

    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    bonus, faixa = calcular_bonus(total_t, total_e, total_c)

    # Success Fee
    if sf >= 150:
        bonusSF = 500
        nivelSF = "150%"
    elif sf >= 120:
        bonusSF = 300
        nivelSF = "120%"
    elif sf >= 100:
        bonusSF = 200
        nivelSF = "100%"
    else:
        bonusSF = 0
        nivelSF = "Não atingido"

    def calc_ind(t,e,c):
        base = (t+e+c)*50
        total = base + bonus + bonusSF
        return base,total

    base1,total1 = calc_ind(t1,e1,c1)
    base2,total2 = calc_ind(t2,e2,c2)
    base3,total3 = calc_ind(t3,e3,c3)

    # =========================
    # KPIs
    # =========================
    st.subheader("📊 Visão Geral")

    colA,colB,colC,colD = st.columns(4)
    colA.metric("Faixa", faixa)
    colB.metric("Transportadoras", total_t)
    colC.metric("Embarcadores", total_e)
    colD.metric("Bônus", f"R$ {bonus}")

    st.write(f"📈 Success Fee: {nivelSF} | R$ {bonusSF}")

    st.divider()

    # =========================
    # RANKING
    # =========================
    ranking = pd.DataFrame({
        "Pessoa":["Luis Felipe","Fernando","Outro"],
        "Contratos":[
            t1+e1+c1,
            t2+e2+c2,
            t3+e3+c3
        ],
        "Total":[total1,total2,total3]
    }).sort_values("Contratos",ascending=False).reset_index(drop=True)

    medalhas = ["🥇","🥈","🥉"]
    ranking["Posição"] = [medalhas[i] for i in range(len(ranking))]

    st.subheader("🏆 Ranking")
    st.dataframe(ranking, use_container_width=True)

    top = ranking.iloc[0]

    st.markdown(f"""
    <div class="card">
        <h2>🔥 Top Performer</h2>
        <h3>{top['Pessoa']}</h3>
        <p>{top['Contratos']} contratos</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================
    # GRÁFICOS
    # =========================
    df_chart = pd.DataFrame({
        "Pessoa":["Luis Felipe","Fernando","Outro"],
        "Transportadoras":[t1,t2,t3],
        "Embarcadores":[e1,e2,e3],
        "Coringas":[c1,c2,c3]
    })

    df_melt = df_chart.melt(id_vars="Pessoa",
                           var_name="Tipo",
                           value_name="Qtd")

    fig1 = px.bar(df_melt,x="Pessoa",y="Qtd",color="Tipo",barmode="stack")
    fig1.update_layout(template="plotly_dark")

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(ranking,x="Pessoa",y="Contratos",text="Contratos")
    fig2.update_layout(template="plotly_dark")

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # CARDS
    # =========================
    def card(nome,t,e,c,total):
        st.markdown(f"""
        <div class="card">
        <h3>{nome}</h3>
        <p>Contratos: {t+e+c}</p>
        <p>💰 R$ {total}</p>
        </div>
        """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)

    with col1:
        card("Luis Felipe",t1,e1,c1,total1)
    with col2:
        card("Fernando",t2,e2,c2,total2)
    with col3:
        card("Outro",t3,e3,c3,total3)

# =========================
# HISTÓRICO
# =========================
st.divider()
st.subheader("📅 Histórico")

st.dataframe(st.session_state.dados, use_container_width=True)
