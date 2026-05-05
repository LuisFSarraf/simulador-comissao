import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Comercial", layout="wide")

# =========================
# ESTILO
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

st.title("📊 Painel Comercial - Metas e Comissão")

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
st.subheader("📈 Success Fee (Meta R$ 5.000)")

sf_valor = st.number_input("Valor transacionado no mês (R$)", 0)
meta_sf = 5000

sf_percent = (sf_valor / meta_sf) * 100 if meta_sf else 0

if sf_percent >= 150:
    bonusSF = 500
elif sf_percent >= 120:
    bonusSF = 300
elif sf_percent >= 100:
    bonusSF = 200
else:
    bonusSF = 0

# =========================
# CORINGA (SÓ META, NÃO VISUAL)
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
def calcular_faixa(t, e):

    pct_t = t / 50
    pct_e = e / 20
    media = (pct_t + pct_e) / 2

    if pct_t >= 1 and pct_e >= 1:
        return 1000, "Faixa 4"
    elif media >= 0.9:
        return 800, "Faixa 3"
    elif media >= 0.75:
        return 600, "Faixa 2"
    elif media >= 0.5:
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

    # CORINGA APLICADO NA META
    final_t, final_e = aplicar_coringa(total_t, total_e, total_c)

    bonus_faixa, faixa_nome = calcular_faixa(final_t, final_e)

    # =========================
    # KPIs TIME
    # =========================
    pct_t = (final_t / 50) * 100
    pct_e = (final_e / 20) * 100
    media = (pct_t + pct_e) / 2

    st.subheader("🎯 Metas do Time")

    st.markdown(f"""
<div class="card">

<div class="title">Transportadoras</div>
<div class="value ok">{pct_t:.1f}%</div>

<div class="title">Embarcadores</div>
<div class="value ok">{pct_e:.1f}%</div>

<div class="title">Progresso Geral</div>
<div class="value ok">{media:.1f}%</div>

<div class="title">Faixa Atual</div>
<div class="value ok">{faixa_nome}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # INDIVIDUAL (SEM CORINGA)
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1),
        ("Fernando", t2, e2),
        ("Outro", t3, e3)
    ]

    df = []

    for nome, t, e in pessoas:

        producao = t + e
        comissao = producao * 50
        total = comissao + bonus_faixa + bonusSF

        df.append([nome, producao, comissao, total])

    df = pd.DataFrame(df, columns=["Pessoa","Produção","Comissão","Total"])

    df_rank = df.sort_values("Produção", ascending=False)

    st.subheader("🏆 Ranking")

    st.dataframe(df_rank, use_container_width=True)

    # =========================
    # ALERTA
    # =========================
    st.subheader("⚡ Faltas para Meta")

    st.markdown(f"""
<div class="card">

<div class="title">Transportadoras faltando</div>
<div class="value">{max(0, 50 - final_t)}</div>

<div class="title">Embarcadores faltando</div>
<div class="value">{max(0, 20 - final_e)}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # RESULTADO INDIVIDUAL
    # =========================
    st.subheader("💰 Resultado Individual")

    for nome, t, e in pessoas:

        producao = t + e
        comissao = producao * 50
        total = comissao + bonus_faixa + bonusSF

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{producao}</div>

<div class="small">
Comissão: R$ {comissao}<br>
Bônus faixa: R$ {bonus_faixa}<br>
Success Fee: R$ {bonusSF}
</div>

<div class="value ok">
Total: R$ {total}
</div>

</div>
""", unsafe_allow_html=True)
