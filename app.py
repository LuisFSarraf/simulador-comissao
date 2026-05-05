import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Comercial", layout="wide")

st.title("📊 Painel Comercial - CORRIGIDO")

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
# CORINGA
# =========================
def aplicar_coringa(t, e, c):

    faltam_t = max(0, 50 - t)
    usados_t = min(c, faltam_t)

    restante = c - usados_t

    faltam_e = max(0, 20 - e)
    usados_e = min(restante, faltam_e)

    return t + usados_t, e + usados_e

# =========================
# FAIXA DO TIME
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

    # TIME TOTAL
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    final_t, final_e = aplicar_coringa(total_t, total_e, total_c)

    bonus_faixa, faixa_nome = faixa(final_t, final_e)

    # =========================
    # KPI TIME
    # =========================
    pct_t = final_t / 50
    pct_e = final_e / 20
    media = (pct_t + pct_e) / 2

    st.subheader("🎯 Metas do Time")

    st.markdown(f"""
📦 Transportadoras: **{pct_t*100:.1f}%**  
🚚 Embarcadores: **{pct_e*100:.1f}%**  
📊 Total: **{media*100:.1f}%**  
🏆 Faixa: **{faixa_nome}**  
💰 Bônus faixa (time): **R$ {bonus_faixa}**  
📈 Success Fee (time): **R$ {bonusSF}**
""")

    # =========================
    # INDIVIDUAL (CORRETO)
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1),
        ("Fernando", t2, e2),
        ("Outro", t3, e3)
    ]

    st.subheader("💰 Resultado Individual (CORRETO)")

    for nome, t, e in pessoas:

        producao = t + e
        comissao = producao * 50

        # 👇 IMPORTANTE: só comissão individual
        total = comissao

        st.markdown(f"""
---

### {nome}

📦 Produção: **{producao} contratos**  
💰 Comissão: **R$ {comissao}**  
🏆 Total individual: **R$ {total}**
""")

    # =========================
    # RESUMO FINAL DO TIME
    # =========================
    st.subheader("🏁 Total do Time")

    st.markdown(f"""
💰 Bônus faixa (time): **R$ {bonus_faixa}**  
📈 Success fee (time): **R$ {bonusSF}**
""")
