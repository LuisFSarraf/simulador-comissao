import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Comercial", layout="wide")

# =========================
# VISUAL (mantido SaaS)
# =========================
st.markdown("""
<style>
.main {background-color:#0f172a;color:white;}

.card {
    background:#1e293b;
    padding:18px;
    border-radius:14px;
    margin-bottom:14px;
}

.title {font-size:18px;font-weight:600;}
.value {font-size:28px;font-weight:bold;}
.small {font-size:14px;opacity:0.85;}
.ok {color:#3b82f6;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Painel Comercial - Metas & Comissão")

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
# SUCCESS FEE (TIME)
# =========================
sf_valor = st.number_input("Success Fee (R$)", 0)

if sf_valor >= 7500:
    bonusSF = 500
elif sf_valor >= 6000:
    bonusSF = 300
elif sf_valor >= 5000:
    bonusSF = 200
else:
    bonusSF = 0

# =========================
# CORINGA (SÓ META)
# =========================
def aplicar_coringa(t, e, c):

    faltam_t = max(0, 50 - t)
    usados_t = min(c, faltam_t)

    restante = c - usados_t

    faltam_e = max(0, 20 - e)
    usados_e = min(restante, faltam_e)

    return t + usados_t, e + usados_e

# =========================
# FAIXA
# =========================
def faixa(t, e):

    pct = (t/50 + e/20) / 2

    if pct >= 1:
        return 1000, "Faixa 4"
    elif pct >= 0.9:
        return 800, "Faixa 3"
    elif pct >= 0.75:
        return 600, "Faixa 2"
    elif pct >= 0.5:
        return 400, "Faixa 1"
    else:
        return 0, "Sem faixa"

# =========================
# EXECUÇÃO
# =========================
if st.button("Calcular"):

    # TOTAL TIME
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    final_t, final_e = aplicar_coringa(total_t, total_e, total_c)

    bonus_faixa, faixa_nome = faixa(final_t, final_e)

    pct_t = final_t / 50
    pct_e = final_e / 20
    media = (pct_t + pct_e) / 2

    # =========================
    # META TIME (VISUAL ORIGINAL)
    # =========================
    st.subheader("🎯 Metas do Time")

    st.markdown(f"""
<div class="card">

<div class="title">Transportadoras</div>
<div class="value ok">{pct_t*100:.1f}%</div>

<div class="title">Embarcadores</div>
<div class="value ok">{pct_e*100:.1f}%</div>

<div class="title">Progresso Geral</div>
<div class="value ok">{media*100:.1f}%</div>

<div class="title">Faixa Atual</div>
<div class="value ok">{faixa_nome}</div>

<div class="small">Bônus faixa: R$ {bonus_faixa}</div>
<div class="small">Success Fee: R$ {bonusSF}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # INDIVIDUAL (CORRETO)
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1),
        ("Fernando", t2, e2),
        ("Outro", t3, e3)
    ]

    st.subheader("💰 Resultado Individual")

    for nome, t, e in pessoas:

        producao = t + e
        comissao = producao * 50  # SOMENTE PRODUÇÃO REAL

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{producao} contratos</div>

<div class="small">
Comissão: R$ {comissao}
</div>

<div class="value ok">
Total: R$ {comissao}
</div>

</div>
""", unsafe_allow_html=True)
