import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SaaS Comercial", layout="wide")

st.title("📊 SaaS Comercial - Sistema Final Correto")

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
# CORINGA (OTIMIZAÇÃO FAIXA)
# =========================
def otimizar(t, e, c):

    def simular(t0, e0, c0, prioridade):

        t, e, c = t0, e0, c0

        if prioridade == "T":

            uso_t = min(c, max(0, 50 - t))
            c -= uso_t
            t += uso_t

            uso_e = min(c, max(0, 20 - e))
            e += uso_e

        else:

            uso_e = min(c, max(0, 20 - e))
            c -= uso_e
            e += uso_e

            uso_t = min(c, max(0, 50 - t))
            t += uso_t

        return t, e

    def score(t, e):
        return min(t/50,1)*4 + min(e/20,1)*4

    r1 = simular(t, e, c, "T")
    r2 = simular(t, e, c, "E")

    return r1 if score(r1[0], r1[1]) >= score(r2[0], r2[1]) else r2

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
# SUCCESS FEE (GLOBAL)
# =========================
def success_fee(total):

    if total >= 150:
        return 500, 150
    elif total >= 120:
        return 300, 120
    elif total >= 100:
        return 200, 100
    else:
        return 0, (total/100)*100

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
    # TIME (FAIXA + META)
    # =========================
    t_total = t1 + t2 + t3
    e_total = e1 + e2 + e3
    c_total = c1 + c2 + c3

    t_final, e_final = otimizar(t_total, e_total, c_total)

    bonus_faixa, faixa_nome = faixa(t_final, e_final)

    total_time = t_final + e_final + c_total

    bonus_sf, percent_sf = success_fee(total_time)

    # =========================
    # INDIVIDUAL
    # =========================
    st.subheader("💰 Resultado Individual")

    ranking_data = []

    for nome, t, e, c in pessoas:

        contratos = t + e + c

        comissao = contratos * 50

        bonus_faixa_ind, faixa_ind = faixa(t + c, e + c)

        bonus_sf_ind = bonus_sf * (contratos / max(1, total_time))

        total = comissao + bonus_faixa_ind + bonus_sf_ind

        ranking_data.append([nome, contratos])

        st.markdown(f"""
<div style="background:#1e293b;padding:18px;border-radius:16px;margin-bottom:12px">

<h3>{nome}</h3>

<h2>{contratos} contratos</h2>

💰 Comissão: R$ {comissao:.2f}  
🏆 Faixa: {faixa_ind} (+ R$ {bonus_faixa_ind:.2f})  

📈 Success Fee: {percent_sf:.0f}% (+ R$ {bonus_sf_ind:.2f})

<h3 style="color:#3b82f6">TOTAL: R$ {total:.2f}</h3>

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
