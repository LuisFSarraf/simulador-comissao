import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

st.title("📊 Sistema Comercial - Versão Final Limpa")

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
# FAIXA (INDIVIDUAL)
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

        # 🏆 faixa
        bonus_faixa, faixa_nome = faixa(t, e)

        # 📈 success fee (individual fixo)
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
    # RANKING (SEM GRÁFICO)
    # =========================
    df = pd.DataFrame(ranking, columns=["Pessoa", "Contratos"])
    df = df.sort_values("Contratos", ascending=False)

    st.subheader("🏆 Ranking")
    st.dataframe(df, use_container_width=True)
