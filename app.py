import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# ─────────────────────────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    color: #f1f5f9;
  }
  .card h3 {
    margin: 0 0 4px 0;
    color: #94a3b8;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .card h2 {
    margin: 0 0 12px 0;
    color: #f8fafc;
    font-size: 20px;
  }
  .card .linha { margin: 5px 0; font-size: 15px; }
  .card .total {
    color: #38bdf8;
    font-size: 24px;
    font-weight: 700;
    margin-top: 14px;
    border-top: 1px solid #334155;
    padding-top: 10px;
  }
  .card-time {
    background: #0f172a;
    border: 1px solid #1d4ed8;
    border-radius: 16px;
    padding: 20px 24px;
    color: #f1f5f9;
    margin-bottom: 14px;
  }
  .card-time .linha { margin: 6px 0; font-size: 15px; }
  .tag-faixa {
    display: inline-block;
    background: #1d4ed8;
    color: white;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 13px;
    font-weight: 600;
  }
  .tag-sem-faixa {
    display: inline-block;
    background: #475569;
    color: #cbd5e1;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 13px;
  }
  .hint {
    color: #64748b;
    font-size: 13px;
    margin-top: 3px;
    margin-bottom: 3px;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────

# Faixas em ordem DECRESCENTE (maior primeiro)
FAIXAS = [
    (4, 50, 20, 1000),
    (3, 40, 16,  800),
    (2, 30, 12,  600),
    (1, 20,  8,  400),
]

SUCCESS_FEE_MAP = {
    "0%":   (0,   "Sem atingimento"),
    "100%": (200, "100% da meta"),
    "120%": (300, "120% da meta"),
    "150%": (500, "150% da meta"),
}

COMISSAO_POR_CONTRATO = 50

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES DE CÁLCULO
# ─────────────────────────────────────────────────────────────────

def calcular_comissao(t: int, e: int, c: int) -> float:
    """Pilar 1 — R$ 50 por contrato (T + E + Coringas)."""
    return (t + e + c) * COMISSAO_POR_CONTRATO


def calcular_melhor_faixa(t: int, e: int, c: int):
    """
    Pilar 2 — Bônus por faixa calculado sobre os totais do TIME.
    Testa todas as alocações possíveis dos coringas (T ou E, nunca os dois).
    Retorna: (bonus, nome_faixa, (t_final, e_final), (c_como_t, c_como_e))
    """
    melhor_bonus = 0
    melhor_nome  = "Sem faixa"
    melhor_t_fin = t
    melhor_e_fin = e
    melhor_c_t   = 0
    melhor_c_e   = 0

    for i in range(c + 1):
        t_final = t + i
        e_final = e + (c - i)

        for num, min_t, min_e, bonus in FAIXAS:
            if t_final >= min_t and e_final >= min_e:
                if bonus > melhor_bonus:
                    melhor_bonus = bonus
                    melhor_nome  = f"Faixa {num}"
                    melhor_t_fin = t_final
                    melhor_e_fin = e_final
                    melhor_c_t   = i
                    melhor_c_e   = c - i
                break

    return melhor_bonus, melhor_nome, (melhor_t_fin, melhor_e_fin), (melhor_c_t, melhor_c_e)


# ─────────────────────────────────────────────────────────────────
# INTERFACE — CABEÇALHO
# ─────────────────────────────────────────────────────────────────

st.title("📊 Dashboard Comercial")
st.caption("Comissão por contrato (individual) · Bônus por faixa (time) · Success fee (time)")

# ─────────────────────────────────────────────────────────────────
# INTERFACE — CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────────

with st.expander("⚙️ Configurar nomes dos vendedores", expanded=False):
    col_n1, col_n2, col_n3 = st.columns(3)
    nome1 = col_n1.text_input("Vendedor 1", value="Luis Felipe")
    nome2 = col_n2.text_input("Vendedor 2", value="Fernando")
    nome3 = col_n3.text_input("Vendedor 3", value="Mileny")

nomes = [nome1, nome2, nome3]

sf_opcao = st.selectbox(
    "📈 Success Fee do Time",
    list(SUCCESS_FEE_MAP.keys()),
    help="Meta do time atingida. Bônus pago integralmente a cada vendedor, sem rateio."
)
bonus_sf, sf_descricao = SUCCESS_FEE_MAP[sf_opcao]

# ─────────────────────────────────────────────────────────────────
# INTERFACE — INPUTS
# ─────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📋 Contratos por Vendedor")

col1, col2, col3 = st.columns(3)
colunas = [col1, col2, col3]
dados_input = []

for idx, (col, nome) in enumerate(zip(colunas, nomes)):
    with col:
        st.markdown(f"**{nome}**")
        t = int(st.number_input("Transportadoras", min_value=0, step=1, key=f"t_{idx}"))
        e = int(st.number_input("Embarcadores",    min_value=0, step=1, key=f"e_{idx}"))
        c = int(st.number_input("Coringas",        min_value=0, step=1, key=f"c_{idx}",
                                help="Alocado como T ou E para maximizar a faixa do time."))
        dados_input.append((nome, t, e, c))

# ─────────────────────────────────────────────────────────────────
# CÁLCULO
# ─────────────────────────────────────────────────────────────────

if st.button("🚀 Calcular Comissões", use_container_width=True, type="primary"):

    # ── Totais do time (usados para calcular faixa) ──────────────
    total_t = sum(d[1] for d in dados_input)
    total_e = sum(d[2] for d in dados_input)
    total_c = sum(d[3] for d in dados_input)

    bonus_faixa, nome_faixa, dist_time, aloc_c = calcular_melhor_faixa(total_t, total_e, total_c)

    st.markdown("---")

    # ── Resultado do time (faixa) ────────────────────────────────
    st.subheader("👥 Faixa do Time")

    if nome_faixa == "Sem faixa":
        tag_time = '<span class="tag-sem-faixa">Sem faixa</span>'
    else:
        tag_time = f'<span class="tag-faixa">{nome_faixa}</span>'

    c_t, c_e = aloc_c
    hint_c = ""
    if total_c > 0:
        hint_c = f'<div class="hint">↳ Coringas do time: {c_t} alocados como transportadora · {c_e} como embarcador</div>'

    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 Total do time: <b>{total_t}T + {total_e}E + {total_c}C</b>
    &nbsp;→&nbsp; com coringas: <b>{dist_time[0]}T + {dist_time[1]}E</b></div>
  {hint_c}
  <div class="linha">🏆 Faixa atingida: {tag_time} → <b>R$ {bonus_faixa:,.2f}</b> por vendedor</div>
  <div class="linha">📈 Success Fee ({sf_opcao} · {sf_descricao}): <b>R$ {bonus_sf:,.2f}</b> por vendedor</div>
</div>
""", unsafe_allow_html=True)

    # ── Resultados individuais ───────────────────────────────────
    st.subheader("💰 Resultado Individual")

    resultados = []
    for nome, t, e, c in dados_input:
        comissao = calcular_comissao(t, e, c)
        total    = comissao + bonus_faixa + bonus_sf

        resultados.append({
            "nome":        nome,
            "t": t, "e": e, "c": c,
            "contratos":   t + e + c,
            "comissao":    comissao,
            "bonus_faixa": bonus_faixa,
            "nome_faixa":  nome_faixa,
            "bonus_sf":    bonus_sf,
            "total":       total,
        })

        if nome_faixa == "Sem faixa":
            tag = '<span class="tag-sem-faixa">Sem faixa</span>'
        else:
            tag = f'<span class="tag-faixa">{nome_faixa}</span>'

        st.markdown(f"""
<div class="card">
  <h3>{nome}</h3>
  <h2>{t + e + c} contratos &nbsp;·&nbsp; {t} transp. + {e} emb. + {c} coringas</h2>
  <div class="linha">💰 Comissão por contratos: <b>R$ {comissao:,.2f}</b></div>
  <div class="linha">🏆 Bônus de faixa (time): {tag} → <b>R$ {bonus_faixa:,.2f}</b></div>
  <div class="linha">📈 Success fee ({sf_opcao}): <b>R$ {bonus_sf:,.2f}</b></div>
  <div class="total">TOTAL &nbsp; R$ {total:,.2f}</div>
</div>
""", unsafe_allow_html=True)

    # ── Resumo do time ───────────────────────────────────────────
    total_contratos = sum(r["contratos"] for r in resultados)
    total_geral     = sum(r["total"]     for r in resultados)

    st.subheader("💵 Resumo Financeiro do Time")
    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 <b>Total de Contratos:</b> {total_contratos}</div>
  <div class="linha">💵 <b>Total Pago ao Time:</b> R$ {total_geral:,.2f}</div>
</div>
""", unsafe_allow_html=True)

    # ── Ranking ──────────────────────────────────────────────────
    st.subheader("🏆 Ranking")

    df = pd.DataFrame([{
        "Vendedor":          r["nome"],
        "Contratos":         r["contratos"],
        "Comissão (R$)":     r["comissao"],
        "Faixa (time)":      r["nome_faixa"],
        "Bônus Faixa (R$)":  r["bonus_faixa"],
        "Success Fee (R$)":  r["bonus_sf"],
        "Total (R$)":        r["total"],
    } for r in resultados])

    df = df.sort_values("Total (R$)", ascending=False).reset_index(drop=True)
    df.index += 1
    df.index.name = "Pos."

    st.dataframe(
        df.style.format({
            "Comissão (R$)":    "R$ {:,.2f}",
            "Bônus Faixa (R$)": "R$ {:,.2f}",
            "Success Fee (R$)": "R$ {:,.2f}",
            "Total (R$)":       "R$ {:,.2f}",
        }),
        use_container_width=True,
    )

    # ── Tabela de referência ─────────────────────────────────────
    with st.expander("📖 Tabela de Faixas", expanded=False):
        df_faixas = pd.DataFrame([{
            "Faixa": f"Faixa {num}",
            "Mín. Transportadoras": min_t,
            "Mín. Embarcadores": min_e,
            "Bônus por vendedor (R$)": f"R$ {bonus:,.2f}",
        } for num, min_t, min_e, bonus in reversed(FAIXAS)])
        st.dataframe(df_faixas, use_container_width=True, hide_index=True)
