import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")
st.title("📊 Sistema Comercial - Versão Final Corrigida (Coringa Real)")

# =========================
# INPUTS
# =========================
col1, col2, col3 = st.columns(3)

def input_user(nome):
    st.subheader(nome)
    t = st.number_input(f"Transportadoras - {nome}", min_value=0, step=1)
    e = st.number_input(f"Embarcadores - {nome}", min_value=0, step=1)
    c = st.number_input(f"Coringas - {nome}", min_value=0, step=1)
    return int(t), int(e), int(c)

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
    return {"0%": 0, "100%": 200, "120%": 300, "150%": 500}[sf]

bonus_sf = valor_sf(sf)

# =========================
# FAIXA — CORINGA OTIMIZADO (CORRIGIDO)
# =========================
def calcular_melhor_faixa(t, e, c):
    """
    Testa todas as distribuições possíveis do coringa entre
    transportadoras e embarcadores, e retorna a melhor faixa.
    """
    FAIXAS = [
        (4, 50, 20, 1000),
        (3, 40, 16,  800),
        (2, 30, 12,  600),
        (1, 20,  8,  400),
    ]

    melhor_bonus = 0
    melhor_nome = "Sem faixa"

    for i in range(c + 1):
        t_final = t + i
        e_final = e + (c - i)

        for faixa_num, min_t, min_e, bonus in FAIXAS:
            if t_final >= min_t and e_final >= min_e:
                if bonus > melhor_bonus:
                    melhor_bonus = bonus
                    melhor_nome = f"Faixa {faixa_num}"
                break  # já achou a melhor faixa para esta distribuição

    return melhor_bonus, melhor_nome

# =========================
# EXECUÇÃO
# =========================
if st.button("🚀 Calcular"):
    pessoas = [
        ("Luis Felipe", t1, e1, c1),
        ("Fernando",    t2, e2, c2),
        ("Outro",       t3, e3, c3),
    ]

    st.subheader("💰 Resultado Individual")
    ranking = []

    for nome, t, e, c in pessoas:
        contratos = t + e + c
        comissao = contratos * 50
        bonus_faixa, faixa_nome = calcular_melhor_faixa(t, e, c)
        total = comissao + bonus_faixa + bonus_sf

        ranking.append({"Pessoa": nome, "Contratos": contratos, "Total (R$)": total})

        st.markdown(f"""
<div style="background:#1e293b;padding:18px;border-radius:16px;margin-bottom:12px;color:white">
  <h3 style="margin:0 0 4px 0">{nome}</h3>
  <h2 style="margin:0 0 10px 0">{contratos} contratos</h2>
  💰 Comissão: <b>R$ {comissao:,.2f}</b><br>
  🏆 Faixa: <b>{faixa_nome}</b> → R$ {bonus_faixa:,.2f}<br>
  📈 Success Fee ({sf}) → R$ {bonus_sf:,.2f}
  <h2 style="color:#3b82f6;margin:12px 0 0 0">TOTAL: R$ {total:,.2f}</h2>
</div>
""", unsafe_allow_html=True)

    # =========================
    # RESULTADO DO TIME
    # =========================
    total_contratos = sum(r["Contratos"] for r in ranking)
    total_geral     = sum(r["Total (R$)"] for r in ranking)

    st.subheader("👥 Resultado do Time")
    st.markdown(f"""
<div style="background:#0f172a;padding:18px;border-radius:16px;color:white">
  📦 <b>Total de Contratos:</b> {total_contratos}<br>
  📈 <b>Success Fee do Time ({sf}):</b> R$ {bonus_sf:,.2f}<br>
  💵 <b>Total Pago ao Time:</b> R$ {total_geral:,.2f}
</div>
""", unsafe_allow_html=True)

    # =========================
    # RANKING
    # =========================
    st.subheader("🏆 Ranking")
    df = pd.DataFrame(ranking).sort_values("Contratos", ascending=False).reset_index(drop=True)
    df.index += 1  # ranking começa em 1
    df.index.name = "Posição"
    st.dataframe(df, use_container_width=True)
