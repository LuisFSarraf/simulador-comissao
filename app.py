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

st.title("📊 Painel Comercial - Comissão e Metas")

# =========================
# INPUTS
# =========================
col1, col2, col3 = st.columns(3)

def input_user(nome):
    st.subheader(nome)
    t = st.number_input(f"Transportadoras - {nome}", 0)
    e = st.number_input(f"Embarcadores - {nome}", 0)
    h = st.number_input(f"Híbridos - {nome}", 0)
    return t, e, h

with col1:
    t1, e1, h1 = input_user("Luis Felipe")
with col2:
    t2, e2, h2 = input_user("Fernando")
with col3:
    t3, e3, h3 = input_user("Outro")

# =========================
# SUCCESS FEE
# =========================
sf_valor = st.number_input("Valor transacionado (R$)", 0)
meta_sf = 5000

sf_pct = sf_valor / meta_sf if meta_sf else 0

if sf_pct >= 1.5:
    bonusSF = 500
elif sf_pct >= 1.2:
    bonusSF = 300
elif sf_pct >= 1.0:
    bonusSF = 200
else:
    bonusSF = 0

# =========================
# HÍBRIDO (CORRETO)
# =========================
def aplicar_hibrido(t, e, h):

    # primeiro cobre transportadoras
    falta_t = max(0, 50 - t)
    uso_t = min(h, falta_t)

    h_restante = h - uso_t

    # depois cobre embarcadores
    falta_e = max(0, 20 - e)
    uso_e = min(h_restante, falta_e)

    return t + uso_t, e + uso_e

# =========================
# FAIXAS (CORRIGIDO)
# =========================
def calcular_faixa(t, e):

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
if st.button("Calcular"):

    # =========================
    # TOTAL TIME
    # =========================
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_h = h1 + h2 + h3

    final_t, final_e = aplicar_hibrido(total_t, total_e, total_h)

    bonus_faixa, faixa_nome = calcular_faixa(final_t, final_e)

    # =========================
    # INDIVIDUAL
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1, h1),
        ("Fernando", t2, e2, h2),
        ("Outro", t3, e3, h3)
    ]

    st.subheader("💰 Comissão Individual")

    df = []

    for nome, t, e, h in pessoas:

        producao = t + e + h
        comissao = producao * 50

        df.append([nome, t, e, h, producao, comissao])

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{producao} contratos</div>

<div class="small">
Transportadoras: {t}<br>
Embarcadores: {e}<br>
Híbridos: {h}
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
    # BONUS TIME
    # =========================
    st.subheader("🏆 Bônus do Time")

    st.markdown(f"""
<div class="card">

<div class="title">Faixa atingida</div>
<div class="value ok">{faixa_nome}</div>

<div class="title">Bônus faixa</div>
<div class="value ok">R$ {bonus_faixa}</div>

<div class="title">Success Fee</div>
<div class="value ok">R$ {bonusSF}</div>

<div class="title">Total bônus time</div>
<div class="value ok">R$ {bonus_faixa + bonusSF}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # RESUMO
    # =========================
    df = pd.DataFrame(df, columns=[
        "Pessoa",
        "Transportadoras",
        "Embarcadores",
        "Híbridos",
        "Produção",
        "Comissão"
    ])

    st.subheader("📊 Resumo Geral")
    st.dataframe(df, use_container_width=True)
