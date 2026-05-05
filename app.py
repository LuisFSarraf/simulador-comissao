import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

st.title("📊 Dashboard Comercial - Simulador de Comissão")

# =========================
# BASE DE DADOS
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

sf = st.slider("📈 Success Fee (% da meta do time)", 0, 200, 0)

# =========================
# SALVAR DADOS
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
# FUNÇÃO BONUS
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
# BOTÃO CALCULAR
# =========================
if st.button("🚀 Calcular"):

    # Totais
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    bonus, faixa = calcular_bonus(total_t, total_e, total_c)

    # SUCCESS FEE
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

    # INDIVIDUAL
    def calc_ind(t, e, c):
        base = (t + e + c) * 50
        total = base + bonus + bonusSF
        return base, total

    base1, total1 = calc_ind(t1, e1, c1)
    base2, total2 = calc_ind(t2, e2, c2)
    base3, total3 = calc_ind(t3, e3, c3)

    # =========================
    # RESULTADO TIME
    # =========================
    st.subheader("📊 Resultado do Time")

    colA, colB, colC = st.columns(3)
    colA.metric("Faixa", faixa)
    colB.metric("Transportadoras", total_t)
    colC.metric("Embarcadores", total_e)

    st.write(f"💰 Bônus Faixa: R$ {bonus}")
    st.write(f"📈 Success Fee: {nivelSF} | R$ {bonus}")

    st.divider()

    # =========================
    # INDIVIDUAL
    # =========================
    def mostrar(nome, t, e, c, base, total):
        st.subheader(f"👤 {nome}")
        st.write(f"Transportadoras: {t}")
        st.write(f"Embarcadores: {e}")
        st.write(f"Coringas: {c}")
        st.write(f"Total contratos: {t+e+c}")
        st.write(f"Comissão: R$ {base}")
        st.write(f"Bônus Faixa: R$ {bonus}")
        st.write(f"Success Fee: R$ {bonusSF}")
        st.success(f"💰 Total: R$ {total}")

    col1, col2, col3 = st.columns(3)

    with col1:
        mostrar("Luis Felipe", t1, e1, c1, base1, total1)
    with col2:
        mostrar("Fernando", t2, e2, c2, base2, total2)
    with col3:
        mostrar("Outro", t3, e3, c3, base3, total3)

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
        "Total": [total1, total2, total3]
    }).sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")
    st.dataframe(ranking, use_container_width=True)

    # =========================
    # GRÁFICOS
    # =========================
    st.divider()
    st.subheader("📊 Gráficos")

    st.plotly_chart(px.bar(ranking, x="Pessoa", y="Contratos"))
    st.plotly_chart(px.pie(ranking, names="Pessoa", values="Contratos"))

    # =========================
    # META
    # =========================
    st.divider()
    st.subheader("🎯 Meta")

    meta_t = 50
    meta_e = 20

    st.metric("Transportadoras", total_t, f"{int((total_t/meta_t)*100)}%")
    st.metric("Embarcadores", total_e, f"{int((total_e/meta_e)*100)}%")

    # =========================
    # PREVISÃO
    # =========================
    if not st.session_state.dados.empty:

        hoje = datetime.now()
        dias_mes = calendar.monthrange(hoje.year, hoje.month)[1]

        total_hist = (
            st.session_state.dados["transportadora"].sum() +
            st.session_state.dados["embarcador"].sum() +
            st.session_state.dados["coringa"].sum()
        )

        media = total_hist / hoje.day
        previsao = int(media * dias_mes)

        st.metric("📉 Previsão do mês", previsao)

# =========================
# HISTÓRICO
# =========================
st.divider()
st.subheader("📅 Histórico")

st.dataframe(st.session_state.dados, use_container_width=True)
