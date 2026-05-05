import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# CSS PREMIUM
# =========================
st.markdown("""
<style>
.main {background-color:#0f172a;color:white;}
.block-container {padding-top:2rem;}

.card {
    background:#1e293b;
    padding:20px;
    border-radius:16px;
    box-shadow:0px 6px 20px rgba(0,0,0,0.4);
    margin-bottom:15px;
}

.kpi-ok {color:#22c55e;font-size:22px;font-weight:bold;}
.kpi-warn {color:#f59e0b;font-size:22px;font-weight:bold;}
.kpi-bad {color:#ef4444;font-size:22px;font-weight:bold;}

h1,h2,h3,h4 {color:white;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial - Comissão")

# =========================
# INPUTS
# =========================
col1,col2,col3 = st.columns(3)

def input_user(nome):
    st.subheader(nome)
    t = st.number_input(f"Transportadoras - {nome}",0)
    e = st.number_input(f"Embarcadores - {nome}",0)
    c = st.number_input(f"Coringas - {nome}",0)
    return t,e,c

with col1:
    t1,e1,c1 = input_user("Luis Felipe")

with col2:
    t2,e2,c2 = input_user("Fernando")

with col3:
    t3,e3,c3 = input_user("Outro")

sf = st.slider("📈 Success Fee (%)",0,200,0)

# =========================
# CORINGA INTELIGENTE
# =========================
def calcular_melhor_cenario(t,e,c):
    melhor_bonus=0
    melhor_faixa="Abaixo"
    melhor_i=0

    for i in range(c+1):
        tF=t+i
        eF=e+(c-i)

        if tF>=50 and eF>=20:
            return 1000,"Faixa 4",i,c-i
        elif tF>=40 and eF>=16 and melhor_bonus<800:
            melhor_bonus,melhor_faixa,melhor_i=800,"Faixa 3",i
        elif tF>=30 and eF>=12 and melhor_bonus<600:
            melhor_bonus,melhor_faixa,melhor_i=600,"Faixa 2",i
        elif tF>=20 and eF>=8 and melhor_bonus<400:
            melhor_bonus,melhor_faixa,melhor_i=400,"Faixa 1",i

    return melhor_bonus,melhor_faixa,melhor_i,c-melhor_i

# =========================
# CALCULAR
# =========================
if st.button("🚀 Calcular"):

    total_t = t1+t2+t3
    total_e = e1+e2+e3
    total_c = c1+c2+c3

    bonus,faixa,usado_t,usado_e = calcular_melhor_cenario(total_t,total_e,total_c)

    final_t = total_t + usado_t
    final_e = total_e + usado_e

    # SUCCESS FEE
    if sf>=150:
        bonusSF=500
    elif sf>=120:
        bonusSF=300
    elif sf>=100:
        bonusSF=200
    else:
        bonusSF=0

    def calc_ind(t,e,c):
        base=(t+e+c)*50
        return base, base+bonus+bonusSF

    base1,total1=calc_ind(t1,e1,c1)
    base2,total2=calc_ind(t2,e2,c2)
    base3,total3=calc_ind(t3,e3,c3)

    # =========================
    # KPIs
    # =========================
    st.subheader("📊 Visão Geral")

    def cor_meta(valor,meta):
        if valor>=meta:
            return "kpi-ok"
        elif valor>=meta*0.7:
            return "kpi-warn"
        return "kpi-bad"

    colA,colB,colC,colD = st.columns(4)

    colA.markdown(f"<div class='{cor_meta(final_t,50)}'>🚚 {final_t}/50</div>",unsafe_allow_html=True)
    colB.markdown(f"<div class='{cor_meta(final_e,20)}'>📦 {final_e}/20</div>",unsafe_allow_html=True)
    colC.metric("Faixa",faixa)
    colD.metric("Bônus",f"R$ {bonus}")

    st.markdown(f"📈 Success Fee: **R$ {bonusSF}**")

    st.divider()

    # =========================
    # CORINGAS EXPLICADOS
    # =========================
    st.markdown(f"""
    <div class="card">
    <b>🎯 Uso dos Coringas</b><br><br>
    ➜ +{usado_t} em Transportadoras<br>
    ➜ +{usado_e} em Embarcadores
    </div>
    """,unsafe_allow_html=True)

    # =========================
    # RANKING
    # =========================
    ranking = pd.DataFrame({
        "Pessoa":["Luis Felipe","Fernando","Outro"],
        "Contratos":[t1+e1+c1,t2+e2+c2,t3+e3+c3],
        "Total":[total1,total2,total3]
    }).sort_values("Contratos",ascending=False).reset_index(drop=True)

    medalhas=["🥇","🥈","🥉"]
    ranking["Posição"]=medalhas

    st.subheader("🏆 Ranking")
    st.dataframe(ranking,use_container_width=True)

    top=ranking.iloc[0]
    st.success(f"🔥 Top Performer: {top['Pessoa']} com {top['Contratos']} contratos")

    # =========================
    # GRÁFICOS PROFISSIONAIS
    # =========================
    st.subheader("📊 Análise Visual")

    df = pd.DataFrame({
        "Pessoa":["Luis Felipe","Fernando","Outro"],
        "Transportadoras":[t1,t2,t3],
        "Embarcadores":[e1,e2,e3],
        "Coringas":[c1,c2,c3]
    })

    df_melt = df.melt(id_vars="Pessoa",var_name="Tipo",value_name="Qtd")

    fig1 = px.bar(df_melt,x="Pessoa",y="Qtd",color="Tipo",barmode="stack")
    fig1.update_layout(
        template="plotly_dark",
        font=dict(size=18),
        title_font_size=24,
        legend_font_size=16
    )
    st.plotly_chart(fig1,use_container_width=True)

    fig2 = px.bar(ranking,x="Pessoa",y="Contratos",text="Contratos")
    fig2.update_layout(
        template="plotly_dark",
        font=dict(size=18),
        title_font_size=24
    )
    st.plotly_chart(fig2,use_container_width=True)

    # =========================
    # SIMULAÇÃO
    # =========================
    st.divider()
    st.subheader("🧠 Simulação de Ganhos")

    extra = st.slider("Se fechar mais quantos contratos?",0,20,0)

    sim_total = (total_t+total_e+total_c+extra)*50 + bonus + bonusSF

    st.metric("💰 Comissão simulada",f"R$ {sim_total}")

    # =========================
    # CARDS INDIVIDUAIS
    # =========================
    def card(nome,total):
        st.markdown(f"""
        <div class="card">
        <h3>{nome}</h3>
        <h2>R$ {total}</h2>
        </div>
        """,unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)

    with col1: card("Luis Felipe",total1)
    with col2: card("Fernando",total2)
    with col3: card("Outro",total3)
