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
# FAIXA (CORRIGIDA)
# =========================
def faixa(total):

    if total >= 70:
        return 1000, "Faixa 4"
    elif total >= 52:
        return 800, "Faixa 3"
    elif total >= 42:
        return 600, "Faixa 2"
    elif total >= 28:
        return 400, "Faixa 1"
    else:
        return 0, "Sem faixa"

# =========================
# SUCCESS FEE (INDIVIDUAL CORRETO)
# =========================
def success_fee(score):

    if score >= 150:
        return 500, "150%"
    elif score >= 120:
        return 300, "120%"
    elif score >= 100:
        return 200, "100%"
    else:
        return 0, "0%"

# =========================
# EXECUÇÃO
# =========================
if st.button("🚀 Calcular"):

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    st.subheader("💰 Resultado Individual (CORRETO FINAL)")

    df = []

    for nome, t, e, c in pessoas:

        # ✔ produção real
        contratos = t + e + c

        # ✔ comissão
        comissao = contratos * 50

        # ✔ faixa (coringa conta aqui também)
        bonus_faixa, faixa_nome = faixa(contratos)

        # ✔ success fee individual (BASE REAL)
        score = contratos
        bonus_sf, nivel_sf = success_fee(score)

        total = comissao + bonus_faixa + bonus_sf

        df.append([
            nome,
            contratos,
            comissao,
            bonus_faixa,
            bonus_sf,
            total
        ])

        st.markdown(f"""
<div style="background:#1e293b;padding:18px;border-radius:16px;margin-bottom:12px">

<h3>{nome}</h3>

<h2>{contratos} contratos</h2>

💰 Comissão: R$ {comissao:.2f}  
🏆 Bônus faixa ({faixa_nome}): R$ {bonus_faixa:.2f}  
📈 Success Fee ({nivel_sf}): R$ {bonus_sf:.2f}  

<h3 style="color:#3b82f6">TOTAL: R$ {total:.2f}</h3>

</div>
""", unsafe_allow_html=True)

    # =========================
    # RANKING
    # =========================
    ranking = pd.DataFrame({
        "Pessoa":[p[0] for p in pessoas],
        "Contratos":[p[1]+p[2]+p[3] for p in pessoas]
    }).sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")
    st.dataframe(ranking, use_container_width=True)

    fig = px.bar(ranking, x="Pessoa", y="Contratos", text="Contratos")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
