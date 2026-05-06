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

st.title("📊 SaaS Comercial - Performance & Comissão")

# =========================
# INPUTS (CORRIGIDO)
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
    t3, e3, c3 = input_user("Outro")  # ✔ FIX AQUI (era e2 antes)

# =========================
# SUCCESS FEE
# =========================
sf = st.slider("📈 Success Fee (%)", 0, 200, 0)

def calc_sf(sf):
    if sf >= 150:
        return 500, "150%"
    elif sf >= 120:
        return 300, "120%"
    elif sf >= 100:
        return 200, "100%"
    else:
        return 0, "0%"

bonusSF, nivelSF = calc_sf(sf)

# =========================
# FAIXA
# =========================
def faixa(t, e):
    if t >= 50 and e >= 20:
        return 1000, "Faixa 4", (50,20)
    elif t >= 40 and e >= 16:
        return 800, "Faixa 3", (40,16)
    elif t >= 30 and e >= 12:
        return 600, "Faixa 2", (30,12)
    elif t >= 20 and e >= 8:
        return 400, "Faixa 1", (20,8)
    else:
        return 0, "Sem faixa", (20,8)

# =========================
# CORINGA (OTIMIZAÇÃO INTELIGENTE)
# =========================
def aplicar_otimizacao(t, e, c):

    def simular(t0, e0, c0, ordem):

        t, e, c = t0, e0, c0

        if ordem == "T":

            uso_t = min(c, max(0, 50 - t))
            c -= uso_t
            t += uso_t

            uso_e = min(c, max(0, 20 - e))
            e += uso_e

        else:

            uso_e = min(c, max(0, 20 - e))
            c -= uso_e
            e += uso_e

            uso_t = min(c, max(0, 50 - t))
            t += uso_t

        return t, e

    def score(t, e):

        if t >= 50 and e >= 20:
            return 4
        elif t >= 40 and e >= 16:
            return 3
        elif t >= 30 and e >= 12:
            return 2
        elif t >= 20 and e >= 8:
            return 1
        else:
            return 0

    r1 = simular(t, e, c, "T")
    r2 = simular(t, e, c, "E")

    if score(r1[0], r1[1]) >= score(r2[0], r2[1]):
        return r1
    else:
        return r2

# =========================
# EXECUÇÃO
# =========================
if st.button("🚀 Calcular"):

    # =========================
    # TIME
    # =========================
    t_total = t1 + t2 + t3
    e_total = e1 + e2 + e3
    c_total = c1 + c2 + c3

    t_final, e_final = aplicar_otimizacao(t_total, e_total, c_total)

    bonus, faixa_nome, target = faixa(t_final, e_final)

    falta_t = max(0, target[0] - t_final)
    falta_e = max(0, target[1] - e_final)

    # =========================
    # INDIVIDUAL
    # =========================
    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    st.subheader("💰 Resultado Individual")

    df = []

    for nome, t, e, c in pessoas:

        contratos = t + e + c
        comissao = contratos * 50  # coringa gera comissão

        df.append([nome, t, e, c, contratos, comissao])

        st.markdown(f"""
<div class="card">

<div class="title">{nome}</div>

<div class="value">{contratos} contratos</div>

<div class="small">
🚚 Transportadoras: {t}<br>
📦 Embarcadores: {e}<br>
🔁 Coringas: {c}
</div>

<div class="value ok">R$ {comissao}</div>

</div>
""", unsafe_allow_html=True)

    # =========================
    # KPIs TIME
    # =========================
    st.subheader("📊 Performance do Time")

    colA, colB, colC, colD = st.columns(4)

    colA.metric("Faixa", faixa_nome)
    colB.metric("Transportadoras", t_final)
    colC.metric("Embarcadores", e_final)
    colD.metric("Bônus", f"R$ {bonus}")

    st.write(f"📈 Success Fee: {nivelSF} → R$ {bonusSF}")

    # =========================
    # PROGRESSO
    # =========================
    st.subheader("🎯 Progresso para próxima faixa")

    st.write(f"Faltam {falta_t} Transportadoras")
    st.write(f"Faltam {falta_e} Embarcadores")

    st.progress(min((t_final + e_final) / (target[0] + target[1]), 1.0))

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

    # =========================
    # DETALHAMENTO
    # =========================
    df = pd.DataFrame(df, columns=[
        "Pessoa","Transportadoras","Embarcadores","Coringas","Contratos","Comissão"
    ])

    st.subheader("📋 Visão Detalhada")
    st.dataframe(df, use_container_width=True)
