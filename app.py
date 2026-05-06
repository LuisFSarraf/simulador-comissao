import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SaaS Comercial", layout="wide")

# =========================
# UI
# =========================
st.markdown("""
<style>
.main {background-color:#0f172a;color:white;}

.card {
    background:#1e293b;
    padding:18px;
    border-radius:16px;
    margin-bottom:14px;
}

h3 {margin-bottom:5px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 SaaS Comercial - Performance Completa")

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
# FAIXA INDIVIDUAL
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
# SUCCESS FEE (CORRETO + BAR)
# =========================
def success_fee(total):

    if total >= 150:
        return 500, 150
    elif total >= 120:
        return 300, 120
    elif total >= 100:
        return 200, 100
    else:
        percent = (total / 100) * 100
        return 0, percent

# =========================
# EXECUÇÃO
# =========================
if st.button("🚀 Calcular"):

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    st.subheader("💰 Resultado Individual")

    ranking_data = []

    for nome, t, e, c in pessoas:

        # ✔ contratos reais
        contratos = t + e + c

        # ✔ comissão (coringa incluído)
        comissao = contratos * 50

        # ✔ faixa individual
        bonus_faixa, faixa_nome = faixa(contratos)

        # ✔ success fee individual
        bonus_sf, percent_sf = success_fee(contratos)

        # ✔ total final
        total = comissao + bonus_faixa + bonus_sf

        ranking_data.append([nome, contratos])

        # =========================
        # CARD INDIVIDUAL
        # =========================
        st.markdown(f"""
<div class="card">

<h3>{nome}</h3>

<h2>{contratos} contratos</h2>

💰 Comissão: R$ {comissao:.2f}  
🏆 Faixa: {faixa_nome} (+ R$ {bonus_faixa:.2f})  

📈 Success Fee: {percent_sf:.0f}%

<div style="background:#334155;height:8px;border-radius:6px;margin:8px 0;">
<div style="width:{min(percent_sf/150*100,100)}%;height:8px;background:#3b82f6;border-radius:6px"></div>
</div>

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
