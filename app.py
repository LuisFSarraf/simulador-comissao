import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# LOGIN SIMPLES
# =========================
usuarios = {
    "luis": "123",
    "fernando": "123",
    "outro": "123"
}

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in usuarios and usuarios[user] == senha:
            st.session_state.logado = True
            st.session_state.user = user
        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

# =========================
# BASE DE DADOS LOCAL
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "data", "pessoa", "transportadora", "embarcador", "coringa"
    ])

st.title("📊 Dashboard Comercial")

# =========================
# INPUT
# =========================
col1, col2, col3 = st.columns(3)

def input_user(nome):
    st.subheader(nome)
    t = st.number_input(f"Transportadoras {nome}", 0)
    e = st.number_input(f"Embarcadores {nome}", 0)
    c = st.number_input(f"Coringas {nome}", 0)
    return t, e, c

with col1:
    t1, e1, c1 = input_user("Luis Felipe")
with col2:
    t2, e2, c2 = input_user("Fernando")
with col3:
    t3, e3, c3 = input_user("Outro")

sf = st.slider("Success Fee (%)", 0, 200, 0)

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
# CÁLCULO
# =========================
def calcular_bonus(t, e, c):
    melhor = 0
    faixa = "Abaixo"
    for i in range(c+1):
        tF = t+i
        eF = e+(c-i)

        if tF >= 50 and eF >= 20:
            return 1000, "Faixa 4"
        elif tF >= 40 and eF >= 16:
            melhor, faixa = 800, "Faixa 3"
        elif tF >= 30 and eF >= 12:
            melhor, faixa = 600, "Faixa 2"
        elif tF >= 20 and eF >= 8:
            melhor, faixa = 400, "Faixa 1"
    return melhor, faixa

if st.button("🚀 Calcular"):

    t = t1+t2+t3
    e = e1+e2+e3
    c = c1+c2+c3

    bonus, faixa = calcular_bonus(t,e,c)

    if sf >= 150:
        bonusSF = 500
    elif sf >= 120:
        bonusSF = 300
    elif sf >= 100:
        bonusSF = 200
    else:
        bonusSF = 0

    def calc_ind(t,e,c):
        base = (t+e+c)*50
        total = base + bonus + bonusSF
        return base, total

    base1, total1 = calc_ind(t1,e1,c1)
    base2, total2 = calc_ind(t2,e2,c2)
    base3, total3 = calc_ind(t3,e3,c3)

    st.subheader("🏆 Ranking")
    ranking = pd.DataFrame({
        "Pessoa": ["Luis Felipe","Fernando","Outro"],
        "Total": [total1,total2,total3]
    }).sort_values("Total", ascending=False)

    st.dataframe(ranking, use_container_width=True)

    st.subheader("📊 Resultados")
    col1,col2,col3 = st.columns(3)

    col1.metric("Luis Felipe", total1)
    col2.metric("Fernando", total2)
    col3.metric("Outro", total3)

# =========================
# HISTÓRICO
# =========================
st.divider()
st.subheader("📅 Histórico")

st.dataframe(st.session_state.dados, use_container_width=True)
