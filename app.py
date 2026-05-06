import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

st.title("📊 Sistema Comercial - Versão Final Ajustada")

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
sf = st.selectbox("📈 Success Fee do Time", ["0%", "100%", "120%", "150%"])

def valor_sf(sf):
    if sf == "150%":
        return 500
    elif sf == "120%":
        return 300
    elif sf == "100%":
        return 200
    else:
        return 0

bonus_sf = valor_sf(sf)

# =========================
# FAIXA (CORRIGIDA - OTIMIZAÇÃO CORINGA)
# =========================
def faixa(t, e, c):

    melhor_bonus = 0
    melhor_nome = "Sem faixa"

    # testa todas distribuições possíveis do coringa
    for i in range(c + 1):

        t_final = t + i
        e_final = e + (c - i)

        if t_final >= 50 and e_final >= 20:
            return 1000, "Faixa 4"

        if t_final >= 40 and e_final >= 16:
            melhor_bonus, melhor_nome = 800, "Faixa 3"

        elif t_final >= 30 and e_final >= 12:
            melhor_bonus, melhor_nome = 600, "Faixa 2"

        elif t_final >= 20 and e_final >= 8:
            melhor_bonus, melhor_nome = 400, "Faixa 1"

    return melhor_bonus, melhor_nome

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

    ranking = []

    for nome, t, e, c in pessoas:

        contratos = t + e + c

        # 💰 comissão
        comissao = contratos * 50

        # 🏆 faixa corrigida
        bonus_faixa, faixa_nome = faixa(t, e, c)

        # 📈 success fee fixo (time)
        bonus_sf_ind = bonus_sf

        total = comissao + bonus_faixa + bonus_sf_ind

        ranking.append([nome, contratos])

        st.markdown(f"""
<div style="background:#1e293b;padding:18px;border-radius:16px;margin-bottom:12px">

<h3>{nome}</h3>

<h2>{contratos} contratos</h2>

💰 Comissão: R$ {comissao:.2f}  
🏆 Faixa: {faixa_nome} → R$ {bonus_faixa:.2f}  

📈 Success Fee ({sf}) → R$ {bonus_sf_ind:.2f}

<h2 style="color:#3b82f6">TOTAL: R$ {total:.2f}</h2>

</div>
""", unsafe_allow_html=True)

    # =========================
    # TIME
    # =========================
    total_contratos = sum([t1+e1+c1, t2+e2+c2, t3+e3+c3])

    st.subheader("👥 Resultado do Time")

    st.write(f"""
📦 Total Contratos: {total_contratos}  
📈 Success Fee do Time: {sf} → R$ {bonus_sf}
""")

    # =========================
    # RANKING
    # =========================
    df = pd.DataFrame(ranking, columns=["Pessoa", "Contratos"])
    df = df.sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")
    st.dataframe(df, use_container_width=True)
