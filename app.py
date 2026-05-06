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

.title {font-size:18px;font-weight:600;}
.value {font-size:28px;font-weight:bold;}
.small {font-size:14px;opacity:0.85;}
.ok {color:#3b82f6;}
</style>
""", unsafe_allow_html=True)

st.title("📊 SaaS Comercial - Comissão & Performance")

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
# SUCCESS FEE (INDIVIDUAL AGORA)
# =========================
def calc_sf(valor):
    if valor >= 150:
        return 500, "150%"
    elif valor >= 120:
        return 300, "120%"
    elif valor >= 100:
        return 200, "100%"
    else:
        return 0, "0%"

# =========================
# FAIXA INDIVIDUAL
# =========================
def faixa_individual(t, e):
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
# EXECUÇÃO
# =========================
if st.button("🚀 Calcular"):

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    st.subheader("💰 Resultado Individual (CORRETO)")

    df = []

    for nome, t, e, c in pessoas:

        contratos = t + e + c

        # 💰 comissão (CORINGA INCLUIDO)
        comissao = contratos * 50

        # 🏆 bônus de faixa INDIVIDUAL
        bonus_faixa, faixa_nome = faixa_individual(t + c, e + c)

        # 📈 success fee INDIVIDUAL (exemplo simples baseado em performance)
        sf_input = min(200, (contratos / 100) * 100)
        bonus_sf, nivel_sf = calc_sf(sf_input)

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
<div class="card">

<div class="title">{nome}</div>

<div class="value">{contratos} contratos</div>

<div class="small">
💰 Comissão: R$ {comissao:.2f}<br>
🏆 Bônus faixa: R$ {bonus_faixa:.2f} ({faixa_nome})<br>
📈 Success Fee: R$ {bonus_sf:.2f} ({nivel_sf})
</div>

<div class="value ok">TOTAL: R$ {total:.2f}</div>

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
