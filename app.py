import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# ─────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────
st.markdown("""
<style>
  body { background-color: #0f172a; }
  .card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    color: #f1f5f9;
  }
  .card h3 { margin: 0 0 4px 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
  .card h2 { margin: 0 0 12px 0; color: #f8fafc; font-size: 22px; }
  .card .linha { margin: 4px 0; font-size: 15px; }
  .card .total { color: #38bdf8; font-size: 24px; font-weight: 700; margin-top: 12px; }
  .card-time {
    background: #0f172a;
    border: 1px solid #1d4ed8;
    border-radius: 16px;
    padding: 20px 24px;
    color: #f1f5f9;
    margin-bottom: 14px;
  }
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
    color: white;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 13px;
  }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Comercial")

# ─────────────────────────────────────────────
# LÓGICA DE NEGÓCIO
# ─────────────────────────────────────────────

FAIXAS = [
    # (número, min_transportadoras, min_embarcadores, bônus)
    (4, 50, 20, 1000),
    (3, 40, 16,  800),
    (2, 30, 12,  600),
    (1, 20,  8,  400),
]

SUCCESS_FEE_MAP = {
    "0%":    (0,   "Nenhum"),
    "100%":  (200, "100% da meta"),
    "120%":  (300, "120% da meta"),
    "150%":  (500, "150% da meta"),
}

def calcular_comissao(t, e, c):
    """R$ 50 por contrato; coringa conta normalmente."""
    return (t + e + c) * 50

def calcular_melhor_faixa(t, e, c):
    """
    Testa todas as distribuições possíveis do coringa entre
    transportadoras e embarcadores para maximizar a faixa.
    Retorna (bônus, nome_da_faixa, t_usado, e_usado).
    """
    melhor_bonus = 0
    melhor_nome  = "Sem faixa"
    melhor_dist  = (t, e)

    for i in range(c + 1):           # i coringas viram transportadora
        t_final = t + i
        e_final = e + (c - i)        # resto vira embarcador

        for num, min_t, min_e, bonus in FAIXAS:   # faixas em ordem decrescente
            if t_final >= min_t and e_final >= min_e:
                if bonus > melhor_bonus:
                    melhor_bonus = bonus
                    melhor_nome  = f"Faixa {num}"
                    melhor_dist  = (t_final, e_final)
                break   # melhor faixa para esta distribuição já encontrada

    return melhor_bonus, melhor_nome, melhor_dist

def calcular_total(t, e, c, bonus_sf):
    comissao               = calcular_comissao(t, e, c)
    bonus_faixa, nome_faixa, dist = calcular_melhor_faixa(t, e, c)
    total                  = comissao + bonus_faixa + bonus_sf
    return {
        "comissao":    comissao,
        "bonus_faixa": bonus_faixa,
        "nome_faixa":  nome_faixa,
        "dist":        dist,
        "bonus_sf":    bonus_sf,
        "total":       total,
        "contratos":   t + e + c,
    }

# ─────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────

nomes_padrão = ["Luis Felipe", "Fernando", "Outro"]

with st.expander("⚙️ Configurar nomes dos vendedores", expanded=False):
    nomes = []
    for n in nomes_padrão:
        nomes.append(st.text_input(f"Nome ({n})", value=n))
else:
    nomes = nomes_padrão

sf_opcao = st.selectbox("📈 Success Fee do Time", list(SUCCESS_FEE_MAP.keys()))
bonus_sf, sf_label = SUCCESS_FEE_MAP[sf_opcao]

st.markdown("---")
st.subheader("📋 Contratos por Vendedor")

cols = st.columns(3)
dados_input = []

for idx, (col, nome) in enumerate(zip(cols, nomes)):
    with col:
        st.markdown(f"**{nome}**")
        t = st.number_input(f"Transportadoras", min_value=0, step=1, key=f"t_{idx}")
        e = st.number_input(f"Embarcadores",    min_value=0, step=1, key=f"e_{idx}")
        c = st.number_input(f"Coringas",        min_value=0, step=1, key=f"c_{idx}")
        dados_input.append((nome, int(t), int(e), int(c)))

# ─────────────────────────────────────────────
# CÁLCULO E RESULTADO
# ─────────────────────────────────────────────

if st.button("🚀 Calcular Comissões", use_container_width=True):

    st.markdown("---")
    st.subheader("💰 Resultado Individual")

    resultados = []
    for nome, t, e, c in dados_input:
        r = calcular_total(t, e, c, bonus_sf)
        r["nome"] = nome
        resultados.append(r)

        # tag de faixa
        if r["nome_faixa"] == "Sem faixa":
            tag_faixa = f'<span class="tag-sem-faixa">{r["nome_faixa"]}</span>'
        else:
            tag_faixa = f'<span class="tag-faixa">{r["nome_faixa"]}</span>'

        # detalhe do coringa (quando há coringas)
        detalhe_coringa = ""
        if c > 0:
            t_final, e_final = r["dist"]
            detalhe_coringa = (
                f'<div class="linha" style="color:#64748b;font-size:13px">'
                f'↳ Coringas distribuídos: {t_final - t} como transp. / {e_final - e} como embarc.'
                f'</div>'
            )

        st.markdown(f"""
<div class="card">
  <h3>{nome}</h3>
  <h2>{r["contratos"]} contratos &nbsp;·&nbsp; {t} transp. + {e} emb. + {c} coringas</h2>
  <div class="linha">💰 Comissão por contratos: <b>R$ {r["comissao"]:,.2f}</b></div>
  <div class="linha">🏆 Bônus de faixa: {tag_faixa} → <b>R$ {r["bonus_faixa"]:,.2f}</b></div>
  {detalhe_coringa}
  <div class="linha">📈 Bônus success fee ({sf_opcao}): <b>R$ {r["bonus_sf"]:,.2f}</b></div>
  <div class="total">TOTAL: R$ {r["total"]:,.2f}</div>
</div>
""", unsafe_allow_html=True)

    # ─── RESULTADO DO TIME ───
    total_contratos = sum(r["contratos"] for r in resultados)
    total_geral     = sum(r["total"]     for r in resultados)

    st.subheader("👥 Resultado do Time")
    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 <b>Total de Contratos:</b> {total_contratos}</div>
  <div class="linha">📈 <b>Success Fee ({sf_label}):</b> R$ {bonus_sf:,.2f} por pessoa</div>
  <div class="linha">💵 <b>Total Pago ao Time:</b> R$ {total_geral:,.2f}</div>
</div>
""", unsafe_allow_html=True)

    # ─── RANKING ───
    st.subheader("🏆 Ranking")
    df = pd.DataFrame([{
        "Vendedor":       r["nome"],
        "Contratos":      r["contratos"],
        "Comissão (R$)":  r["comissao"],
        "Faixa":          r["nome_faixa"],
        "Bônus Faixa (R$)": r["bonus_faixa"],
        "Success Fee (R$)": r["bonus_sf"],
        "Total (R$)":     r["total"],
    } for r in resultados])

    df = df.sort_values("Total (R$)", ascending=False).reset_index(drop=True)
    df.index += 1
    df.index.name = "Pos."

    st.dataframe(
        df.style.format({
            "Comissão (R$)":     "R$ {:,.2f}",
            "Bônus Faixa (R$)":  "R$ {:,.2f}",
            "Success Fee (R$)":  "R$ {:,.2f}",
            "Total (R$)":        "R$ {:,.2f}",
        }),
        use_container_width=True,
    )
