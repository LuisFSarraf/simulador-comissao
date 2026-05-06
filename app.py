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

st.title("📊 SaaS Comercial - Sistema Correto")

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
# FAIXA (CORRETA)
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
def success_fee(total_t, total_e):

    score = (total_t + total_e)

    if score >= 80:
        return 500, "150%"
    elif score >= 60:
        return 300, "120%"
    elif score >= 40:
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

    st.subheader("💰 Resultado Individual Correto")

    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3

    bonus_sf, nivel_sf = success_fee(total_t, total_e)

    df = []

    for nome, t, e, c in pessoas:

        # ✔ comissão correta
        contratos = t + e + c
        comissao = contratos * 50

        # ✔ faixa individual correta (SEM coringa)
        bonus_faixa, faixa_nome = faixa(t, e)

        # ✔ success fee proporcional (justo)
        proporcao = contratos / max(1, (t1+t2+t3 + e1+e2+e3 + c1+c2+c3))

        bonus_sf_ind = bonus_sf * proporcao

        total = comissao + bonus_faixa + bonus_sf_ind

        df.append([
            nome,
            contratos,
            comissao,
            bonus_faixa,
            bonus_sf_ind,
            total
        ])

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{contratos} contratos</div>

<div class="small">
💰 Comissão: R$ {comissao:.2f}<br>
🏆 Bônus faixa: R$ {bonus_faixa:.2f} ({faixa_nome})<br>
📈 Success Fee: R$ {bonus_sf_ind:.2f}
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
