# =========================
# BI COMPLETO
# =========================

st.divider()
st.subheader("📊 Inteligência Comercial")

# -------------------------
# GRÁFICO BARRA
# -------------------------
fig_bar = px.bar(
    ranking,
    x="Pessoa",
    y="Contratos",
    text="Contratos",
    title="📊 Contratos por Pessoa"
)
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------
# GRÁFICO PIZZA
# -------------------------
fig_pie = px.pie(
    ranking,
    names="Pessoa",
    values="Contratos",
    title="📌 Distribuição de Contratos"
)
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------
# EVOLUÇÃO
# -------------------------
if not st.session_state.dados.empty:

    df_hist = st.session_state.dados.copy()

    df_hist["total"] = (
        df_hist["transportadora"] +
        df_hist["embarcador"] +
        df_hist["coringa"]
    )

    evolucao = df_hist.groupby(["data", "pessoa"])["total"].sum().reset_index()

    fig_line = px.line(
        evolucao,
        x="data",
        y="total",
        color="pessoa",
        markers=True,
        title="📈 Evolução de Contratos"
    )

    st.plotly_chart(fig_line, use_container_width=True)

# -------------------------
# META vs REALIZADO
# -------------------------
st.divider()
st.subheader("🎯 Meta vs Realizado")

meta_transportadora = 50
meta_embarcador = 20

total_transportadora = t1 + t2 + t3
total_embarcador = e1 + e2 + e3

col1, col2 = st.columns(2)

col1.metric(
    "Transportadoras",
    total_transportadora,
    f"{round((total_transportadora/meta_transportadora)*100)}%"
)

col2.metric(
    "Embarcadores",
    total_embarcador,
    f"{round((total_embarcador/meta_embarcador)*100)}%"
)

# -------------------------
# FALTANTE PRA PRÓXIMA FAIXA
# -------------------------
st.divider()
st.subheader("🔥 Próxima Faixa")

faixas = [
    ("Faixa 4", 50, 20),
    ("Faixa 3", 40, 16),
    ("Faixa 2", 30, 12),
    ("Faixa 1", 20, 8)
]

proxima = None

for nome, t_req, e_req in faixas:
    if total_transportadora < t_req or total_embarcador < e_req:
        proxima = (nome, t_req, e_req)
        break

if proxima:
    nome, t_req, e_req = proxima

    falta_t = max(0, t_req - total_transportadora)
    falta_e = max(0, e_req - total_embarcador)

    st.warning(f"Faltam {falta_t} Transportadoras e {falta_e} Embarcadores para {nome}")
else:
    st.success("🔥 Meta máxima atingida!")

# -------------------------
# PREVISÃO DO MÊS
# -------------------------
st.divider()
st.subheader("📉 Previsão do Mês")

if not st.session_state.dados.empty:

    hoje = datetime.now()
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    dia_atual = hoje.day

    total_contratos = (
        st.session_state.dados["transportadora"].sum() +
        st.session_state.dados["embarcador"].sum() +
        st.session_state.dados["coringa"].sum()
    )

    media_dia = total_contratos / dia_atual
    previsao = int(media_dia * dias_no_mes)

    st.metric("Previsão de contratos no mês", previsao)

# -------------------------
# PROJEÇÃO DE COMISSÃO
# -------------------------
st.divider()
st.subheader("💰 Projeção de Comissão")

contratos_atuais = total_transportadora + total_embarcador + (c1+c2+c3)

valor_base = contratos_atuais * 50
projecao_total = valor_base + bonus + bonusSF

st.metric("Comissão estimada atual", f"R$ {projecao_total}")
