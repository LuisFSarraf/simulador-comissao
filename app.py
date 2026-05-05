import streamlit as st

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# =========================
# CSS LIMPO
# =========================
st.markdown("""
<style>
.main {background-color:#0f172a;color:white;}

.card {
    background:#1e293b;
    padding:22px;
    border-radius:16px;
    margin-bottom:14px;
}

.title {font-size:20px;font-weight:600;}
.value {font-size:30px;font-weight:bold;}
.small {font-size:14px;opacity:0.8;}

.ok {color:#3b82f6;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial")

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
st.subheader("📈 Success Fee")

sf_valor = st.number_input("Valor transacionado (R$)", 0)
meta_sf = 5000

sf_percent = (sf_valor / meta_sf) * 100

if sf_percent >= 150:
    bonusSF = 500
    faixa_sf = "150% (Excelência)"
elif sf_percent >= 120:
    bonusSF = 300
    faixa_sf = "120% (Superação)"
elif sf_percent >= 100:
    bonusSF = 200
    faixa_sf = "100% (Meta)"
else:
    bonusSF = 0
    faixa_sf = "Abaixo da meta"

st.markdown(f"""
<div class="card">
<div class="title">Success Fee</div>
<div class="value ok">R$ {sf_valor}</div>
<div class="small">{sf_percent:.1f}% - {faixa_sf}</div>
<div class="small">Bônus: R$ {bonusSF}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# CORINGA
# =========================
def calcular_coringa(t, e, c):
    bonus = 0
    faixa = "Abaixo"
    ut, ue = 0, 0

    for i in range(c + 1):
        tF = t + i
        eF = e + (c - i)

        if tF >= 50 and eF >= 20:
            return 1000, "Faixa 4", i, c - i
        elif tF >= 40 and eF >= 16:
            bonus, faixa, ut, ue = 800, "Faixa 3", i, c - i
        elif tF >= 30 and eF >= 12:
            bonus, faixa, ut, ue = 600, "Faixa 2", i, c - i
        elif tF >= 20 and eF >= 8:
            bonus, faixa, ut, ue = 400, "Faixa 1", i, c - i

    return bonus, faixa, ut, ue

# =========================
# CALCULAR
# =========================
if st.button("Calcular"):

    total_t = t1 + t2 + t3
    total_e = e1 + e2 + e3
    total_c = c1 + c2 + c3

    bonus_faixa, faixa, ut, ue = calcular_coringa(total_t, total_e, total_c)

    final_t = total_t + ut
    final_e = total_e + ue

    # =========================
    # RESULTADO INDIVIDUAL DISCRIMINADO
    # =========================
    st.subheader("💰 Resultado Individual (Discriminado)")

    def comissao_contratos(t,e,c):
        return (t + e + c) * 50

    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando", t2, e2, c2),
        ("Outro", t3, e3, c3)
    ]

    cards = ""

    for nome, t, e, c in pessoas:

        contratos = t + e + c

        comissao = comissao_contratos(t,e,c)
        bonus_faixa_ind = bonus_faixa
        bonus_fee_ind = bonusSF

        total = comissao + bonus_faixa_ind + bonus_fee_ind

        cards += f"""
        <div class="card">
            <div class="title">{nome}</div>

            <div class="value">{contratos} contratos</div>

            <div class="small">
            💼 Comissão contratos: R$ {comissao}<br>
            🏆 Bônus faixa: R$ {bonus_faixa_ind}<br>
            📈 Success Fee: R$ {bonus_fee_ind}
            </div>

            <div class="value ok">
            💰 Total: R$ {total}
            </div>
        </div>
        """

    st.markdown(cards, unsafe_allow_html=True)

    # =========================
    # RESUMO TIME
    # =========================
    st.subheader("🎯 Resumo do Time")

    st.markdown(f"""
    <div class="card">
    <div class="title">Meta Transportadoras</div>
    <div class="value ok">{final_t} / 50</div>

    <div class="title">Meta Embarcadores</div>
    <div class="value ok">{final_e} / 20</div>

    <div class="title">Faixa do Time</div>
    <div class="value ok">{faixa}</div>

    <div class="small">Bônus faixa: R$ {bonus_faixa}</div>
    </div>
    """, unsafe_allow_html=True)
