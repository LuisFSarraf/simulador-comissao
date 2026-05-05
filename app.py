import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Comercial", layout="wide")

# =========================
# VISUAL
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

st.title("📊 Painel Comercial Completo")

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
# CORINGA (AJUDA META)
# =========================
def aplicar_coringa(t, e, c):

    faltam_t = max(0, 50 - t)
    usados_t = min(c, faltam_t)

    restante = c - usados_t

    faltam_e = max(0, 20 - e)
    usados_e = min(restante, faltam_e)

    return t + usados_t, e + usados_e

# =========================
# FAIXA (TIME)
# =========================
def calcular_faixa(t, e):

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

    # =========================
    # TIME TOTAL
    # =========================
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    final_t, final_e = aplicar_coringa(total_t, total_e, total_c)

    bonus_faixa, faixa_nome = calcular_faixa(final_t, final_e)

    # =========================
    # INDIVIDUAL
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1),
        ("Fernando", t2, e2),
        ("Outro", t3, e3)
    ]

    st.subheader("💰 Resultado Individual")

    df = []

    for nome, t, e in pessoas:

        producao = t + e
        comissao = producao * 50

        df.append([nome, producao, comissao])

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{producao} contratos</div>

<div class="small">
Transportadoras: {t}<br>
Embarcadores: {e}
</div>

<div class="small">
Comissão: R$ {comissao}
</div>

<div class="value ok">
Total: R$ {comissao}
</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # RESUMO TIME (SEM SER “META VISUAL”)
    # =========================
    st.subheader("📊 Bônus do Time")

    st.markdown(f"""
<div class="card">

<div class="title">Faixa do Time</div>
<div class="value ok">{faixa_nome}</div>

<div class="title">Bônus Faixa</div>
<div class="value ok">R$ {bonus_faixa}</div>

<div class="title">Success Fee</div>
<div class="value ok">R$ {bonusSF}</div>

<div class="title">Total Bônus Coletivo</div>
<div class="value ok">R$ {bonus_faixa + bonusSF}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # TABELA
    # =========================
    df = pd.DataFrame(df, columns=["Pessoa","Produção","Comissão"])

    st.subheader("📋 Resumo")
    st.dataframe(df, use_container_width=True)
