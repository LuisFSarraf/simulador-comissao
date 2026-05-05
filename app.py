import streamlit as st

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# CSS PADRÃO (CONSISTENTE NO APP)
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

.title {
    font-size:18px;
    font-weight:600;
}

.value {
    font-size:28px;
    font-weight:bold;
}

.small {
    font-size:14px;
    opacity:0.85;
}

.ok {color:#3b82f6;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial - Comissão")

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
# SUCCESS FEE
# =========================
st.subheader("📈 Success Fee (Meta R$ 5.000)")

sf_valor = st.number_input("Valor transacionado no mês (R$)", 0)
meta_sf = 5000

sf_percent = (sf_valor / meta_sf) * 100 if meta_sf > 0 else 0

if sf_percent >= 150:
    bonusSF = 500
    faixa_sf = "150% (Excelência)"
elif sf_percent >= 120:
    bonusSF = 300
    faixa_sf = "120% (Superação)"
elif sf_percent >= 100:
    bonusSF = 200
    faixa_sf = "100% (Meta atingida)"
else:
    bonusSF = 0
    faixa_sf = "Abaixo da meta"

st.markdown(f"""
<div class="card">
<div class="title">Success Fee</div>
<div class="value ok">R$ {sf_valor}</div>
<div class="small">{sf_percent:.1f}% - {faixa_sf}</div>
<div class="small">Bônus do time: R$ {bonusSF}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# CORINGA (AGORA PARTICIPA DA META)
# =========================
def aplicar_coringa(t, e, c):

    faltam_t = max(0, 50 - t)
    usados_t = min(c, faltam_t)

    faltam_e = max(0, 20 - e)
    restantes = c - usados_t
    usados_e = min(restantes, faltam_e)

    final_t = t + usados_t
    final_e = e + usados_e

    return final_t, final_e, usados_t, usados_e

# =========================
# EXECUÇÃO
# =========================
if st.button("Calcular"):

    # TOTAL BRUTO
    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    # CORINGAS AGORA AJUDAM NA META
    final_t, final_e, ut, ue = aplicar_coringa(total_t, total_e, total_c)

    # =========================
    # FAIXA DO TIME
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
            return 0, "Abaixo"

    bonus_faixa, faixa = calcular_faixa(final_t, final_e)

    # =========================
    # COMISSÃO
    # =========================
    def comissao(t, e, c):
        return (t + e + c) * 50

    def total_individual(t, e, c):
        return comissao(t, e, c) + bonus_faixa + bonusSF

    # =========================
    # RESUMO TIME (MESMO PADRÃO VISUAL)
    # =========================
    st.subheader("🎯 Metas do Time")

    st.markdown(f"""
<div class="card">
<div class="title">Transportadoras</div>
<div class="value ok">{final_t} / 50</div>

<div class="title">Embarcadores</div>
<div class="value ok">{final_e} / 20</div>

<div class="title">Faixa</div>
<div class="value ok">{faixa}</div>

<div class="small">Bônus faixa: R$ {bonus_faixa}</div>

<div class="small">
Coringas usados: {ut + ue} (aplicados na meta)
</div>
</div>
""", unsafe_allow_html=True)

    # =========================
    # RESULTADO INDIVIDUAL (MESMO VISUAL DO APP)
    # =========================
    st.subheader("💰 Resultado Individual")

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    for nome, t, e, c in pessoas:

        contratos = t + e + c
        com = comissao(t, e, c)
        total = total_individual(t, e, c)

        st.markdown(f"""
<div class="card">
<div class="title">{nome}</div>

<div class="value">{contratos} contratos</div>

<div class="small">
💼 Comissão: R$ {com}<br>
🏆 Bônus faixa: R$ {bonus_faixa}<br>
📈 Success Fee: R$ {bonusSF}<br>
🔁 Coringas pessoais: {c}
</div>

<div class="value ok">
💰 Total: R$ {total}
</div>
</div>
""", unsafe_allow_html=True)
