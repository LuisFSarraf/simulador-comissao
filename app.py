import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SaaS Comercial", layout="wide")

st.title("📊 Sistema Comercial - Regras Corretas")

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

# =========================
# CORINGA (OTIMIZAÇÃO)
# =========================
def otimizar(t, e, c):

    t_opt = t + c
    e_opt = e + 0

    if t_opt < 50 and e_opt < 20:
        if e_opt < 20:
            e_opt += min(c, 20 - e_opt)
        else:
            t_opt += c

    return t_opt, e_opt

# =========================
# FAIXA
# =========================
def faixa(t, e):

    if t >= 50 and e >= 20:
        return 1000, "Faixa 4"
    elif t >= 40 and e >= 16:
        return 800, "Faixa 3"
    elif t >= 30 and e >= 12:
        return 600, "Faixa 2"
    elif t >= 20 and e >= 8:
        return 400, "Faixa 1"
    else:
        return 0, "Sem faixa"

# =========================
# SUCCESS FEE (META DO TIME)
# =========================
def success_fee(total):

    if total >= 150:
        return 150
    elif total >= 120:
        return 120
    elif total >= 100:
        return 100
    else:
        return 0

# =========================
# EXECUÇÃO
# =========================
if st.button("🚀 Calcular"):

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    # =========================
    # TIME TOTAL
    # =========================
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    t_final, e_final = otimizar(total_t, total_e, total_c)

    meta_total = t_final + e_final

    nivel_sf = success_fee(meta_total)

    # multiplicador da faixa
    if nivel_sf == 150:
        mult = 1.5
    elif nivel_sf == 120:
        mult = 1.2
    elif nivel_sf == 100:
        mult = 1.0
    else:
        mult = 0

    # =========================
    # INDIVIDUAL
    # =========================
    st.subheader("💰 Resultado Individual")

    ranking_data = []

    for nome, t, e, c in pessoas:

        contratos = t + e + c

        comissao = contratos * 50

        bonus_faixa, faixa_nome = faixa(t + c, e + c)

        # ✔ success fee ativa bônus de faixa (multiplicador)
        bonus_faixa_final = bonus_faixa * mult

        total = comissao + bonus_faixa_final

        ranking_data.append([nome, contratos])

        st.markdown(f"""
<div style="background:#1e293b;padding:18px;border-radius:16px;margin-bottom:12px">

<h3>{nome}</h3>

<h2>{contratos} contratos</h2>

💰 Comissão: R$ {comissao:.2f}  
🏆 Faixa: {faixa_nome}  

📈 Success Fee: {nivel_sf}% (multiplicador {mult})

<h3 style="color:#3b82f6">BÔNUS FAIXA FINAL: R$ {bonus_faixa_final:.2f}</h3>

<h2>TOTAL: R$ {total:.2f}</h2>

</div>
""", unsafe_allow_html=True)

    # =========================
    # RANKING
    # =========================
    ranking = pd.DataFrame(ranking_data, columns=["Pessoa", "Contratos"])
    ranking = ranking.sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")
    st.dataframe(ranking, use_container_width=True)

    fig = px.bar(ranking, x="Pessoa", y="Contratos", text="Contratos")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
