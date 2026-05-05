import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Executivo Comercial", layout="wide")

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
.warn {color:#fbbf24;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Painel Executivo Comercial")

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
    t1,e1,c1 = input_user("Luis Felipe")
with col2:
    t2,e2,c2 = input_user("Fernando")
with col3:
    t3,e3,c3 = input_user("Outro")

# =========================
# FUNÇÕES
# =========================
def aplicar_coringa(t, e, c):

    faltam_t = max(0, 50 - t)
    usados_t = min(c, faltam_t)

    restante = c - usados_t

    faltam_e = max(0, 20 - e)
    usados_e = min(restante, faltam_e)

    return t + usados_t, e + usados_e, usados_t, usados_e


def faixa(t, e):

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
        return 0, "Abaixo"


def comissao(total):
    return total * 50


# =========================
# EXECUÇÃO
# =========================
if st.button("Calcular"):

    # TOTAL TIME
    total_t = t1+t2+t3
    total_e = e1+e2+e3
    total_c = c1+c2+c3

    # CORINGA ENTRA NA META
    final_t, final_e, ut, ue = aplicar_coringa(total_t, total_e, total_c)

    bonus_faixa, faixa_nome = faixa(final_t, final_e)

    # =========================
    # KPIs
    # =========================
    pct_t = (final_t/50)*100
    pct_e = (final_e/20)*100
    media = (pct_t + pct_e)/2

    st.subheader("🎯 KPIs do Time")

    st.markdown(f"""
<div class="card">

<div class="title">Transportadoras</div>
<div class="value ok">{final_t} / 50 ({pct_t:.1f}%)</div>

<div class="title">Embarcadores</div>
<div class="value ok">{final_e} / 20 ({pct_e:.1f}%)</div>

<div class="title">Progresso Geral</div>
<div class="value ok">{media:.1f}%</div>

<div class="title">Faixa</div>
<div class="value ok">{faixa_nome}</div>

<div class="small">Bônus faixa: R$ {bonus_faixa}</div>

<div class="small">Coringas usados: {ut+ue}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # DADOS INDIVIDUAIS
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    df = []

    for nome,t,e,c in pessoas:
        total = t+e+c
        df.append([nome, t, e, c, total])

    df = pd.DataFrame(df, columns=["Pessoa","Transportadoras","Embarcadores","Coringas","Contratos"])

    # ranking
    df_rank = df.sort_values("Contratos", ascending=False)
    df_rank["% Time"] = (df_rank["Contratos"] / df_rank["Contratos"].sum()) * 100

    # =========================
    # RANKING
    # =========================
    st.subheader("🏆 Ranking por Contratos")

    st.dataframe(df_rank, use_container_width=True)

    # =========================
    # ALERTAS
    # =========================
    st.subheader("⚡ Alertas de Meta")

    falta_t = max(0, 50 - final_t)
    falta_e = max(0, 20 - final_e)

    st.markdown(f"""
<div class="card">

<div class="title">Faltam para meta</div>

<div class="small">Transportadoras: {falta_t}</div>
<div class="small">Embarcadores: {falta_e}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # RESUMO INDIVIDUAL
    # =========================
    st.subheader("💰 Resultado Individual")

    for nome,t,e,c in pessoas:

        total = t+e+c
        valor = comissao(total) + bonus_faixa

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{total} contratos</div>

<div class="small">
Comissão: R$ {comissao(total)}<br>
Bônus faixa: R$ {bonus_faixa}
</div>

<div class="value ok">
Total: R$ {valor}
</div>

</div>
""", unsafe_allow_html=True)
