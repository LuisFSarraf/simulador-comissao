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

st.title("📊 Painel Comercial - Comissão Individual")

# =========================
# INPUTS
# =========================
col1, col2, col3 = st.columns(3)

def input_user(nome):
    st.subheader(nome)
    t = st.number_input(f"Transportadoras - {nome}", 0)
    e = st.number_input(f"Embarcadores - {nome}", 0)
    return t, e

with col1:
    t1, e1 = input_user("Luis Felipe")
with col2:
    t2, e2 = input_user("Fernando")
with col3:
    t3, e3 = input_user("Outro")

# =========================
# DADOS
# =========================
pessoas = [
    ("Luis Felipe", t1, e1),
    ("Fernando", t2, e2),
    ("Outro", t3, e3)
]

# =========================
# RESULTADO INDIVIDUAL
# =========================
st.subheader("💰 Resultado Individual")

df = []

for nome, t, e in pessoas:

    producao = t + e
    comissao = producao * 50

    df.append([nome, t, e, producao, comissao])

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
# TABELA RESUMO
# =========================
df = pd.DataFrame(df, columns=[
    "Pessoa",
    "Transportadoras",
    "Embarcadores",
    "Produção",
    "Comissão"
])

st.subheader("📊 Resumo")

st.dataframe(df, use_container_width=True)
