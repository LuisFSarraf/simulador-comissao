bash

python3 << 'PYEOF'
with open('/tmp/logo_b64.txt') as f:
    logo_b64 = f.read().strip()

code = '''import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, date, timedelta
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.set_page_config(
    page_title="Painel Comercial Mobiis",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════
# SECRETS
# ═══════════════════════════════════════════════════════════════
try:
    PIPEDRIVE_TOKEN = st.secrets["PIPEDRIVE_TOKEN"]
except Exception:
    PIPEDRIVE_TOKEN = ""
    st.warning("⚠️ Configure PIPEDRIVE_TOKEN em Settings → Secrets.")

PIPEDRIVE_BASE = "https://api.pipedrive.com/v1"
PRODUTO_TRANSP = "Marketplace de Fretes (Transp)"
PRODUTO_EMB    = "Marketplace de Fretes (Emb)"

VENDEDORES = {
    "Luis Felipe": "luis.sarraf@mobiis.com.br",
    "Fernando":    "luiz.goulart@mobiis.com.br",
}

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
''' + f'LOGO_B64 = "{logo_b64}"' + '''

COR_PRIMARIA  = "#2d3ab1"
COR_GRADIENTE = "linear-gradient(135deg, #2d3ab1 0%, #4f5fdb 100%)"

# ═══════════════════════════════════════════════════════════════
# CSS — PREMIUM ENTERPRISE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── KPI CARD ── */
.kpi-card {
  background: var(--background-color);
  border: 1px solid rgba(128,128,128,0.15);
  border-radius: 16px;
  padding: 22px 24px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #2d3ab1, #4f5fdb);
  border-radius: 16px 16px 0 0;
}
.kpi-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  opacity: 0.5;
  margin: 0 0 8px 0;
}
.kpi-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -1px;
  margin: 0;
  line-height: 1;
}
.kpi-sub {
  font-size: 12px;
  opacity: 0.45;
  margin: 6px 0 0 0;
}
.kpi-badge {
  display: inline-block;
  background: linear-gradient(135deg, #2d3ab1, #4f5fdb);
  color: white;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  padding: 3px 9px;
  border-radius: 20px;
  margin-top: 8px;
}

/* ── VENDOR CARD ── */
.vendor-card {
  background: var(--background-color);
  border: 1px solid rgba(128,128,128,0.15);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  position: relative;
}
.vendor-name {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  opacity: 0.5;
  margin: 0 0 4px 0;
}
.vendor-total {
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -1.5px;
  color: #2d3ab1;
  margin: 0 0 16px 0;
  line-height: 1;
}
.vendor-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 0;
  border-bottom: 1px solid rgba(128,128,128,0.08);
  font-size: 13px;
}
.vendor-row:last-child { border-bottom: none; }
.vendor-row-label { opacity: 0.6; font-weight: 500; }
.vendor-row-value { font-weight: 700; }
.vendor-grand {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 2px solid rgba(45,58,177,0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.vendor-grand-label { font-size: 13px; font-weight: 600; opacity: 0.6; }
.vendor-grand-value {
  font-size: 22px;
  font-weight: 900;
  color: #2d3ab1;
  letter-spacing: -0.5px;
}

/* ── TEAM CARD ── */
.team-card {
  background: rgba(45,58,177,0.06);
  border: 1.5px solid rgba(45,58,177,0.2);
  border-radius: 20px;
  padding: 24px 28px;
  margin-bottom: 16px;
}
.team-card .row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
  border-bottom: 1px solid rgba(45,58,177,0.08);
}
.team-card .row:last-child { border-bottom: none; }
.team-card .row b { color: #2d3ab1; }

/* ── PROGRESS BAR ── */
.prog-wrap { margin: 4px 0 10px; }
.prog-track {
  background: rgba(128,128,128,0.12);
  border-radius: 99px;
  height: 8px;
  overflow: hidden;
  margin: 4px 0 2px;
}
.prog-fill {
  background: linear-gradient(90deg, #2d3ab1, #4f5fdb);
  height: 100%;
  border-radius: 99px;
  transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}
.prog-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  opacity: 0.5;
  margin-top: 2px;
}

/* ── INSIGHT CARD ── */
.insight-card {
  background: var(--background-color);
  border: 1px solid rgba(128,128,128,0.12);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.insight-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 1px;
}
.insight-title {
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 2px;
}
.insight-desc {
  font-size: 12px;
  opacity: 0.55;
  margin: 0;
  line-height: 1.5;
}

/* ── RANKING CARD ── */
.rank-card {
  background: var(--background-color);
  border: 1px solid rgba(128,128,128,0.12);
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.rank-medal { font-size: 28px; flex-shrink: 0; }
.rank-info { flex: 1; }
.rank-name { font-size: 15px; font-weight: 700; margin: 0 0 2px; }
.rank-detail { font-size: 12px; opacity: 0.5; margin: 0; }
.rank-total { font-size: 20px; font-weight: 900; color: #2d3ab1; letter-spacing: -0.5px; }

/* ── SECTION HEADER ── */
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 28px 0 16px;
}
.section-title {
  font-size: 16px;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin: 0;
}
.section-line {
  flex: 1;
  height: 1px;
  background: rgba(128,128,128,0.12);
}

/* ── BADGE TIPO ── */
.badge-transp  { background:#dbeafe; color:#1d4ed8; border-radius:6px; padding:2px 8px; font-size:11px; font-weight:700; }
.badge-emb     { background:#dcfce7; color:#166534; border-radius:6px; padding:2px 8px; font-size:11px; font-weight:700; }
.badge-coringa { background:#ede9fe; color:#6d28d9; border-radius:6px; padding:2px 8px; font-size:11px; font-weight:700; }

/* ── PAGE HEADER ── */
.page-header {
  padding: 8px 0 24px;
  border-bottom: 1px solid rgba(128,128,128,0.1);
  margin-bottom: 28px;
}
.page-title {
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -1px;
  margin: 0 0 4px;
}
.page-sub { font-size: 13px; opacity: 0.45; margin: 0; }

/* ── DIVIDER ── */
.div { height: 1px; background: rgba(128,128,128,0.1); margin: 24px 0; }

/* ── CLIENTS TABLE ── */
.client-row {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  margin-bottom: 4px;
  gap: 12px;
  background: rgba(128,128,128,0.03);
  border: 1px solid rgba(128,128,128,0.08);
  font-size: 13px;
}
.client-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.client-name { flex: 1; font-weight: 600; }
.client-meta { opacity: 0.45; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PIPEDRIVE — FUNÇÕES
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def buscar_usuarios():
    try:
        r = requests.get(f"{PIPEDRIVE_BASE}/users",
                         params={"api_token": PIPEDRIVE_TOKEN}, timeout=10)
        r.raise_for_status()
        return {u["email"].lower(): u["id"] for u in (r.json().get("data") or [])}
    except Exception:
        return {}

@st.cache_data(ttl=300, show_spinner=False)
def buscar_negocios(user_id, status, data_inicio, data_fim):
    items = []
    start = 0
    while True:
        try:
            r = requests.get(f"{PIPEDRIVE_BASE}/deals", params={
                "api_token": PIPEDRIVE_TOKEN, "status": status,
                "user_id": user_id, "start": start, "limit": 100,
            }, timeout=10)
            r.raise_for_status()
        except Exception:
            break
        for d in (r.json().get("data") or []):
            campo_data = "won_time" if status == "won" else "lost_time"
            dt = (d.get(campo_data) or "")[:10]
            if data_inicio <= dt <= data_fim:
                items.append(d)
        if r.json().get("additional_data", {}).get("pagination", {}).get("more_items_in_collection"):
            start += 100
        else:
            break
    return items

@st.cache_data(ttl=300, show_spinner=False)
def buscar_produtos_lote(deal_ids: tuple):
    res = {}
    for did in deal_ids:
        try:
            r = requests.get(f"{PIPEDRIVE_BASE}/deals/{did}/products",
                             params={"api_token": PIPEDRIVE_TOKEN}, timeout=10)
            r.raise_for_status()
            res[did] = [p["name"] for p in (r.json().get("data") or [])]
        except Exception:
            res[did] = []
    return res

def classificar(produtos):
    t = any(PRODUTO_TRANSP in p for p in produtos)
    e = any(PRODUTO_EMB    in p for p in produtos)
    if t and e: return "c"
    if t:       return "t"
    if e:       return "e"
    return None

def carregar_vendedor(email, data_inicio, data_fim):
    usuarios = buscar_usuarios()
    uid = usuarios.get(email.lower())
    if not uid:
        return {"t": 0, "e": 0, "c": 0, "ganhos": [], "perdidos": 0}

    ganhos   = buscar_negocios(uid, "won",  data_inicio, data_fim)
    perdidos = buscar_negocios(uid, "lost", data_inicio, data_fim)

    deal_ids     = tuple(d["id"] for d in ganhos)
    prods        = buscar_produtos_lote(deal_ids) if deal_ids else {}

    t = e = c = 0
    lista = []
    tipos = {"t": "Transportadora", "e": "Embarcador", "c": "Embarcador/Transportadora"}
    cores = {"t": "#1d4ed8", "e": "#166534", "c": "#6d28d9"}

    for deal in ganhos:
        tipo = classificar(prods.get(deal["id"], []))
        if tipo == "t":   t += 1
        elif tipo == "e": e += 1
        elif tipo == "c": c += 1
        if tipo:
            lista.append({
                "titulo": deal.get("title", "—"),
                "tipo":   tipos.get(tipo, "—"),
                "cor":    cores.get(tipo, "#888"),
                "data":   (deal.get("won_time") or "")[:10],
            })

    lista.sort(key=lambda x: x["data"], reverse=True)
    return {"t": t, "e": e, "c": c, "ganhos": lista, "perdidos": len(perdidos)}

# ═══════════════════════════════════════════════════════════════
# CÁLCULO
# ═══════════════════════════════════════════════════════════════

def calcular_faixa(t, e, c):
    melhor = (0, "Sem faixa", t, e, 0, 0)
    for i in range(c + 1):
        tf = t + i; ef = e + (c - i)
        for num, mt, me, bonus in FAIXAS:
            if tf >= mt and ef >= me:
                if bonus > melhor[0]:
                    melhor = (bonus, f"Faixa {num}", tf, ef, i, c - i)
                break
    return melhor  # (bonus, nome, t_final, e_final, c_como_t, c_como_e)

def proxima_faixa(t, e, c):
    _, _, tf, ef, _, _ = calcular_faixa(t, e, c)
    atual_bonus, _, _, _, _, _ = calcular_faixa(t, e, c)
    for num, mt, me, bonus in reversed(FAIXAS):
        if bonus <= atual_bonus:
            continue
        return {
            "nome": f"Faixa {num}", "bonus": bonus,
            "falta_t": max(0, mt - tf), "falta_e": max(0, me - ef),
            "pct_t": min(100, round(tf / mt * 100)) if mt else 100,
            "pct_e": min(100, round(ef / me * 100)) if me else 100,
            "mt": mt, "me": me, "tf": tf, "ef": ef,
        }
    return None

# ═══════════════════════════════════════════════════════════════
# COMPONENTES VISUAIS
# ═══════════════════════════════════════════════════════════════

def kpi(label, value, sub=None, badge=None):
    badge_html = f\'<div class="kpi-badge">{badge}</div>\' if badge else ""
    sub_html   = f\'<p class="kpi-sub">{sub}</p>\' if sub else ""
    st.markdown(f"""
<div class="kpi-card">
  <p class="kpi-label">{label}</p>
  <p class="kpi-value">{value}</p>
  {sub_html}{badge_html}
</div>""", unsafe_allow_html=True)

def section(icon, title):
    st.markdown(f"""
<div class="section-header">
  <span style="font-size:18px">{icon}</span>
  <p class="section-title">{title}</p>
  <div class="section-line"></div>
</div>""", unsafe_allow_html=True)

def prog_bar(label, atual, total, suffix=""):
    pct = min(100, round(atual / total * 100)) if total else 0
    st.markdown(f"""
<div class="prog-wrap">
  <div style="font-size:12px;font-weight:600;opacity:0.6;margin-bottom:3px">{label}</div>
  <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
  <div class="prog-meta"><span>{atual} / {total}{suffix}</span><span>{pct}%</span></div>
</div>""", unsafe_allow_html=True)

def insight(icon, title, desc):
    st.markdown(f"""
<div class="insight-card">
  <div class="insight-icon">{icon}</div>
  <div>
    <p class="insight-title">{title}</p>
    <p class="insight-desc">{desc}</p>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# RENDERIZAÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def renderizar(dados, bonus_sf, sf_opcao, sf_descricao, periodo_label):
    """
    dados: {nome: {"t","e","c","ganhos","perdidos"}}
    """
    nomes = list(dados.keys())

    # Totais do time
    total_t = sum(v["t"] for v in dados.values())
    total_e = sum(v["e"] for v in dados.values())
    total_c = sum(v["c"] for v in dados.values())

    bonus_faixa, nome_faixa, tf_time, ef_time, ct_t, ct_e = calcular_faixa(total_t, total_e, total_c)
    prox = proxima_faixa(total_t, total_e, total_c)

    # Resultados individuais
    resultados = {}
    for nome, d in dados.items():
        com = (d["t"] + d["e"] + d["c"]) * COMISSAO_POR_CONTRATO
        tot = com + bonus_faixa + bonus_sf
        resultados[nome] = {**d, "comissao": com, "bonus_faixa": bonus_faixa,
                            "nome_faixa": nome_faixa, "bonus_sf": bonus_sf,
                            "total": tot, "contratos": d["t"]+d["e"]+d["c"]}

    total_contratos = sum(r["contratos"] for r in resultados.values())
    total_geral     = sum(r["total"]     for r in resultados.values())
    total_perdidos  = sum(d["perdidos"]  for d in dados.values())
    top             = max(resultados.values(), key=lambda r: r["contratos"])
    top_nome        = [n for n,r in resultados.items() if r == top][0]

    # ── KPIs PRINCIPAIS
    section("📊", "Visão Geral do Período")
    cols = st.columns(4)
    with cols[0]: kpi("Total de Contratos", total_contratos,
                      f"{total_t} T · {total_e} E · {total_c} E/T")
    with cols[1]: kpi("Faixa do Time", nome_faixa,
                      f"R$ {bonus_faixa:,.0f} por vendedor", badge="🏆 Ativa")
    with cols[2]: kpi("Success Fee", sf_opcao,
                      f"R$ {bonus_sf:,.0f} por vendedor")
    with cols[3]: kpi("Total Pago ao Time", f"R$ {total_geral:,.2f}",
                      f"{len(nomes)} vendedores · {periodo_label}")

    # ── PROGRESSO PARA PRÓXIMA FAIXA
    section("🎯", "Progresso — Próxima Faixa")
    if prox:
        col_p1, col_p2 = st.columns([2,1])
        with col_p1:
            st.markdown(f"""
<div class="team-card">
  <div style="font-size:13px;opacity:0.5;font-weight:600;margin-bottom:12px">
    META: {prox["nome"]} &nbsp;·&nbsp; Bônus R$ {prox["bonus"]:,.0f}/vendedor
  </div>""", unsafe_allow_html=True)
            prog_bar("Transportadoras", prox["tf"], prox["mt"])
            prog_bar("Embarcadores",    prox["ef"], prox["me"])
            falta_txt = []
            if prox["falta_t"]: falta_txt.append(f"{prox['falta_t']} Transportadora(s)")
            if prox["falta_e"]: falta_txt.append(f"{prox['falta_e']} Embarcador(es)")
            if falta_txt:
                st.markdown(f\'<p style="font-size:12px;opacity:0.5;margin-top:4px">Faltam: {" e ".join(falta_txt)}</p>\', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col_p2:
            ganho_extra = prox["bonus"] - bonus_faixa
            kpi("Ganho Extra por Vendedor", f"R$ {ganho_extra:,.0f}",
                f"se atingir {prox['nome']}", badge="🚀 Potencial")
            kpi("Negócios Perdidos", total_perdidos, "no período", badge="⚠️ Atenção" if total_perdidos else None)
    else:
        st.success("🏆 **Faixa Máxima atingida!** O time está na Faixa 4.")

    # ── RESULTADO INDIVIDUAL
    section("💼", "Resultado por Vendedor")
    cols_v = st.columns(len(nomes))
    for col, (nome, r) in zip(cols_v, resultados.items()):
        pct = round(r["contratos"] / total_contratos * 100) if total_contratos else 0
        tag = \'<span class="tag-sem-faixa">Sem faixa</span>\' if nome_faixa == "Sem faixa" \\
              else f\'<span style="display:inline-block;background:#2d3ab1;color:white;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700">{nome_faixa}</span>\'
        with col:
            st.markdown(f"""
<div class="vendor-card">
  <p class="vendor-name">{nome}</p>
  <p class="vendor-total">{r["contratos"]} <span style="font-size:16px;opacity:0.4;font-weight:500">contratos</span></p>

  <div class="vendor-row">
    <span class="vendor-row-label">🚛 Transportadoras</span>
    <span class="vendor-row-value">{r["t"]}</span>
  </div>
  <div class="vendor-row">
    <span class="vendor-row-label">📦 Embarcadores</span>
    <span class="vendor-row-value">{r["e"]}</span>
  </div>
  <div class="vendor-row">
    <span class="vendor-row-label">🔀 Emb./Transportadora</span>
    <span class="vendor-row-value">{r["c"]}</span>
  </div>
  <div class="div" style="margin:12px 0 8px"></div>
  <div class="vendor-row">
    <span class="vendor-row-label">💰 Comissão</span>
    <span class="vendor-row-value">R$ {r["comissao"]:,.2f}</span>
  </div>
  <div class="vendor-row">
    <span class="vendor-row-label">🏆 Bônus Faixa</span>
    <span>{tag} &nbsp;<b>R$ {r["bonus_faixa"]:,.2f}</b></span>
  </div>
  <div class="vendor-row">
    <span class="vendor-row-label">📈 Success Fee</span>
    <span class="vendor-row-value">R$ {r["bonus_sf"]:,.2f}</span>
  </div>
  <div class="vendor-grand">
    <span class="vendor-grand-label">TOTAL</span>
    <span class="vendor-grand-value">R$ {r["total"]:,.2f}</span>
  </div>
  <div style="margin-top:12px">
    <div style="font-size:11px;opacity:0.4;margin-bottom:4px">Participação no time</div>
    <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    <div style="font-size:11px;opacity:0.4;margin-top:3px">{pct}% dos contratos</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── GRÁFICO
    section("📈", "Comparativo Visual")
    fig = go.Figure()
    cores_graf = ["#2d3ab1", "#4f5fdb", "#a5b4fc"]
    for vals, label, cor in zip(
        [[r["t"] for r in resultados.values()],
         [r["e"] for r in resultados.values()],
         [r["c"] for r in resultados.values()]],
        ["Transportadoras", "Embarcadores", "Emb./Transportadora"],
        cores_graf,
    ):
        fig.add_trace(go.Bar(name=label, x=nomes, y=vals,
                             marker_color=cor, marker_line_width=0))
    fig.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0), height=260,
        xaxis=dict(showgrid=False, tickfont=dict(size=13, family="Inter")),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)", tickfont=dict(size=11)),
        bargap=0.25, bargroupgap=0.08,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── RANKING
    section("🏆", "Ranking")
    medalhas = ["🥇", "🥈", "🥉"]
    rank_sorted = sorted(resultados.items(), key=lambda x: x[1]["contratos"], reverse=True)
    cols_rank = st.columns(len(rank_sorted))
    for i, (col, (nome, r)) in enumerate(zip(cols_rank, rank_sorted)):
        with col:
            st.markdown(f"""
<div class="rank-card" style="{"border:1.5px solid rgba(45,58,177,0.3);background:rgba(45,58,177,0.04)" if i==0 else ""}">
  <div class="rank-medal">{medalhas[i] if i < 3 else "🏅"}</div>
  <div class="rank-info">
    <p class="rank-name">{nome}</p>
    <p class="rank-detail">{r["contratos"]} contratos · {r["t"]}T · {r["e"]}E · {r["c"]}E/T</p>
  </div>
  <div class="rank-total">R$ {r["total"]:,.0f}</div>
</div>""", unsafe_allow_html=True)

    # ── INSIGHTS
    section("💡", "Insights Automáticos")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        insight("⭐", f"Top Performer: {top_nome}",
                f"{top['contratos']} contratos fechados · {round(top['contratos']/total_contratos*100) if total_contratos else 0}% da produção do time")
        if total_c > 0:
            insight("🔀", f"Coringas alocados estrategicamente",
                    f"{ct_t} convertidos em Transportadora e {ct_e} em Embarcador para maximizar {nome_faixa}")
        if prox:
            insight("🎯", f"Faltam {prox['falta_t']} Transp. e {prox['falta_e']} Emb. para {prox['nome']}",
                    f"Atingindo a próxima faixa, cada vendedor ganha R$ {prox['bonus']-bonus_faixa:,.0f} a mais")
        if total_perdidos > 0:
            taxa_conv = round(total_contratos / (total_contratos + total_perdidos) * 100)
            insight("⚠️", f"Taxa de conversão: {taxa_conv}%",
                    f"{total_contratos} ganhos e {total_perdidos} perdidos no período")
    with col_i2:
        for nome, r in resultados.items():
            pct = round(r["contratos"] / total_contratos * 100) if total_contratos else 0
            insight("👤", f"{nome}: {pct}% da produção",
                    f"{r['contratos']} contratos · R$ {r['total']:,.2f} no período")
        if bonus_faixa == 0:
            insight("🚀", "Time ainda sem faixa",
                    f"Faixa 1 exige 20 Transportadoras + 8 Embarcadores. Time tem {tf_time}T e {ef_time}E.")

    # ── CLIENTES
    section("🏢", "Clientes Fechados por Vendedor")
    abas_cli = st.tabs(nomes)
    for aba, nome in zip(abas_cli, nomes):
        with aba:
            ganhos = dados[nome]["ganhos"]
            if not ganhos:
                st.info("Nenhum contrato registrado no período.")
                continue
            col_t, col_e, col_c = st.columns(3)
            grupos = {
                "Transportadora":         (col_t, "#1d4ed8", "🚛"),
                "Embarcador":             (col_e, "#166534", "📦"),
                "Embarcador/Transportadora": (col_c, "#6d28d9", "🔀"),
            }
            for tipo_nome, (col, cor, icon) in grupos.items():
                with col:
                    lista_tipo = [g for g in ganhos if g["tipo"] == tipo_nome]
                    st.markdown(f"""
<div style="font-size:12px;font-weight:700;color:{cor};opacity:0.8;
            margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">
  {icon} {tipo_nome} ({len(lista_tipo)})
</div>""", unsafe_allow_html=True)
                    if lista_tipo:
                        for g in lista_tipo:
                            st.markdown(f"""
<div class="client-row">
  <div class="client-dot" style="background:{cor}"></div>
  <div class="client-name">{g["titulo"]}</div>
  <div class="client-meta">{g["data"]}</div>
</div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(\'<p style="font-size:12px;opacity:0.35;padding:8px 0">—</p>\', unsafe_allow_html=True)

    # ── LINK DE COMPARTILHAMENTO
    st.markdown("---")
    base_url = "https://simulador-comissao-skvzytjvfrfm3qsaqghxvw.streamlit.app"
    vals = list(dados.values()); ns = list(dados.keys())
    link = (f"{base_url}?sf={sf_opcao}&run=1"
            f"&n0={ns[0]}&t0={vals[0]['t']}&e0={vals[0]['e']}&c0={vals[0]['c']}"
            f"&n1={ns[1]}&t1={vals[1]['t']}&e1={vals[1]['e']}&c1={vals[1]['c']}")
    st.info("🔗 Compartilhe o link abaixo para visualização do resultado.")
    st.code(link, language=None)

    return resultados, total_contratos, total_geral, bonus_faixa, nome_faixa, dados

# ═══════════════════════════════════════════════════════════════
# E-MAIL EXECUTIVO PREMIUM
# ═══════════════════════════════════════════════════════════════

def montar_email(resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                 total_contratos, total_geral, periodo_label, dados_raw=None):
    total_t = sum(r["t"] for r in resultados.values())
    total_e = sum(r["e"] for r in resultados.values())
    total_c = sum(r["c"] for r in resultados.values())
    top_nome = max(resultados, key=lambda n: resultados[n]["contratos"])
    top_r    = resultados[top_nome]

    linhas_tabela = "".join(f"""
      <tr style="background:{"#ffffff" if i%2==0 else "#f8faff"}">
        <td style="padding:13px 18px;font-weight:600;color:#0f172a;border-bottom:1px solid #e8ecf0">{nome}</td>
        <td style="padding:13px 12px;text-align:center;color:#334155;border-bottom:1px solid #e8ecf0">{r["contratos"]}</td>
        <td style="padding:13px 12px;text-align:center;color:#1d4ed8;border-bottom:1px solid #e8ecf0">{r["t"]}</td>
        <td style="padding:13px 12px;text-align:center;color:#166534;border-bottom:1px solid #e8ecf0">{r["e"]}</td>
        <td style="padding:13px 12px;text-align:center;color:#6d28d9;border-bottom:1px solid #e8ecf0">{r["c"]}</td>
        <td style="padding:13px 12px;text-align:right;color:#334155;border-bottom:1px solid #e8ecf0">R$ {r["comissao"]:,.2f}</td>
        <td style="padding:13px 12px;text-align:right;color:#334155;border-bottom:1px solid #e8ecf0">R$ {r["bonus_faixa"]:,.2f}</td>
        <td style="padding:13px 12px;text-align:right;color:#334155;border-bottom:1px solid #e8ecf0">R$ {r["bonus_sf"]:,.2f}</td>
        <td style="padding:13px 18px;text-align:right;font-weight:800;color:#2d3ab1;
                   border-bottom:1px solid #e8ecf0;font-size:14px">R$ {r["total"]:,.2f}</td>
      </tr>""" for i, (nome, r) in enumerate(resultados.items()))

    # Blocos de clientes detalhados
    blocos_clientes = ""
    if dados_raw:
        for nome, d in dados_raw.items():
            ganhos = d.get("ganhos", [])
            if not ganhos:
                continue
            tipos = {
                "Transportadora":            ("#1d4ed8", "#dbeafe", "🚛"),
                "Embarcador":                ("#166534", "#dcfce7", "📦"),
                "Embarcador/Transportadora": ("#6d28d9", "#ede9fe", "🔀"),
            }
            blocos_tipo = ""
            for tipo_nome, (cor_text, cor_bg, icon) in tipos.items():
                lista = [g for g in ganhos if g["tipo"] == tipo_nome]
                if not lista:
                    continue
                linhas_cli = "".join(f"""
                  <tr>
                    <td style="padding:7px 14px;font-size:12px;color:#334155;
                               border-bottom:1px solid #f1f5f9">{g["data"]}</td>
                    <td style="padding:7px 14px;font-size:12px;color:#0f172a;font-weight:500;
                               border-bottom:1px solid #f1f5f9">{g["titulo"]}</td>
                  </tr>""" for g in lista)
                blocos_tipo += f"""
                <div style="margin-bottom:14px">
                  <div style="background:{cor_bg};color:{cor_text};padding:7px 14px;
                               border-radius:8px 8px 0 0;font-size:11px;font-weight:700;
                               text-transform:uppercase;letter-spacing:0.5px">
                    {icon} {tipo_nome} — {len(lista)} contrato(s)
                  </div>
                  <table width="100%" cellpadding="0" cellspacing="0"
                         style="border:1px solid #e2e8f0;border-top:none;
                                border-radius:0 0 8px 8px;overflow:hidden;background:#fff">
                    {linhas_cli}
                  </table>
                </div>"""

            blocos_clientes += f"""
            <tr><td style="padding:20px 40px 0">
              <p style="margin:0 0 12px;font-size:14px;font-weight:700;color:#0f172a;
                         padding-left:12px;border-left:3px solid #2d3ab1">{nome}</p>
              {blocos_tipo}
            </td></tr>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fechamento Comercial — Mobiis</title>
<style>
  @media (prefers-color-scheme: dark) {{
    .wrap        {{ background:#0f172a !important; }}
    .card        {{ background:#1e293b !important; border-color:#334155 !important; }}
    .card-inner  {{ background:#263148 !important; }}
    .txt         {{ color:#e2e8f0 !important; }}
    .txt-muted   {{ color:#94a3b8 !important; }}
    .txt-strong  {{ color:#f8fafc !important; }}
    .tr-even     {{ background:#1e293b !important; }}
    .tr-odd      {{ background:#263148 !important; }}
    .td-cell     {{ color:#cbd5e1 !important; border-color:#334155 !important; }}
    .td-name     {{ color:#f1f5f9 !important; }}
    .footer      {{ background:#0f172a !important; border-color:#1e293b !important; }}
    .kpi-box     {{ background:#1e3a5f !important; border-color:#2d3ab1 !important; }}
    .cli-row     {{ background:#1e293b !important; border-color:#334155 !important; }}
  }}
</style>
</head>
<body class="wrap" style="margin:0;padding:0;background:#f1f5f9;
      font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#f1f5f9;padding:36px 16px">
<tr><td>
<table class="card" width="680" align="center" cellpadding="0" cellspacing="0"
       style="max-width:680px;background:#ffffff;border-radius:16px;overflow:hidden;
              border:1px solid #e2e8f0;box-shadow:0 4px 24px rgba(0,0,0,0.06)">

  <!-- LOGO + HEADER -->
  <tr>
    <td style="background:#ffffff;padding:28px 40px 22px;text-align:center;
               border-bottom:3px solid #2d3ab1">
      <img src="data:image/jpeg;base64,{LOGO_B64}" alt="Mobiis"
           width="130" style="display:block;margin:0 auto;height:auto">
    </td>
  </tr>
  <tr>
    <td style="background:linear-gradient(135deg,#1e2a96 0%,#2d3ab1 50%,#4f5fdb 100%);
               padding:32px 40px">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <p style="margin:0 0 4px;color:#c7d2fe;font-size:11px;font-weight:600;
                       text-transform:uppercase;letter-spacing:1.5px">Mobiis · Comercial</p>
            <p style="margin:0;color:#ffffff;font-size:24px;font-weight:800;
                       letter-spacing:-0.5px">Fechamento Comercial</p>
            <p style="margin:6px 0 0;color:#a5b4fc;font-size:14px">{periodo_label}</p>
          </td>
          <td style="text-align:right;vertical-align:top">
            <p style="margin:0;color:#c7d2fe;font-size:11px">Gerado em</p>
            <p style="margin:4px 0 0;color:#ffffff;font-size:13px;font-weight:600">
              {datetime.now().strftime("%d/%m/%Y")}
            </p>
            <p style="margin:2px 0 0;color:#a5b4fc;font-size:11px">
              {datetime.now().strftime("%H:%M")}
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- DESTAQUE TOP PERFORMER -->
  <tr>
    <td style="padding:24px 40px 0">
      <div class="kpi-box" style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:12px;
                  padding:18px 22px;display:flex;gap:14px;align-items:center">
        <span style="font-size:32px">⭐</span>
        <div>
          <p class="txt-muted" style="margin:0 0 3px;font-size:11px;font-weight:600;
                    color:#64748b;text-transform:uppercase;letter-spacing:0.8px">
            Top Performer do Período
          </p>
          <p class="txt-strong" style="margin:0;font-size:17px;font-weight:800;color:#0f172a">
            {top_nome} — {top_r["contratos"]} contratos fechados
          </p>
          <p class="txt-muted" style="margin:3px 0 0;font-size:12px;color:#64748b">
            R$ {top_r["total"]:,.2f} no período
          </p>
        </div>
      </div>
    </td>
  </tr>

  <!-- KPIs -->
  <tr>
    <td style="padding:24px 40px 0">
      <p style="margin:0 0 14px;font-size:14px;font-weight:700;color:#0f172a;
                padding-left:12px;border-left:3px solid #2d3ab1">Resumo Financeiro</p>
      <table width="100%" cellpadding="0" cellspacing="0"
             style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden">
        <tr>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-right:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;width:25%">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.8px">
              Total Pago ao Time
            </p>
            <p style="margin:0;color:#2d3ab1;font-size:20px;font-weight:800">
              R$ {total_geral:,.2f}
            </p>
          </td>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-right:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;width:25%">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.8px">
              Faixa do Time
            </p>
            <p style="margin:0;color:#2d3ab1;font-size:20px;font-weight:800">{nome_faixa}</p>
            <p class="txt-muted" style="margin:2px 0 0;font-size:11px;color:#64748b">
              R$ {bonus_faixa:,.0f}/vendedor
            </p>
          </td>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-right:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;width:25%">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.8px">
              Success Fee
            </p>
            <p style="margin:0;color:#2d3ab1;font-size:20px;font-weight:800">{sf_opcao}</p>
            <p class="txt-muted" style="margin:2px 0 0;font-size:11px;color:#64748b">
              R$ {bonus_sf:,.0f}/vendedor
            </p>
          </td>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-bottom:1px solid #e2e8f0;width:25%">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.8px">
              Total Contratos
            </p>
            <p style="margin:0;color:#2d3ab1;font-size:20px;font-weight:800">{total_contratos}</p>
          </td>
        </tr>
        <tr>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-right:1px solid #e2e8f0">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#1d4ed8;text-transform:uppercase;letter-spacing:0.8px">
              🚛 Transportadoras
            </p>
            <p class="txt-strong" style="margin:0;font-size:22px;font-weight:800;color:#0f172a">
              {total_t}
            </p>
          </td>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-right:1px solid #e2e8f0">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#166534;text-transform:uppercase;letter-spacing:0.8px">
              📦 Embarcadores
            </p>
            <p class="txt-strong" style="margin:0;font-size:22px;font-weight:800;color:#0f172a">
              {total_e}
            </p>
          </td>
          <td class="kpi-box" style="padding:18px;background:#f8faff;
                     border-right:1px solid #e2e8f0">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#6d28d9;text-transform:uppercase;letter-spacing:0.8px">
              🔀 Emb./Transportadora
            </p>
            <p class="txt-strong" style="margin:0;font-size:22px;font-weight:800;color:#0f172a">
              {total_c}
            </p>
          </td>
          <td class="kpi-box" style="padding:18px;background:#f8faff">
            <p class="txt-muted" style="margin:0 0 4px;font-size:10px;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.8px">
              Período
            </p>
            <p class="txt-strong" style="margin:0;font-size:13px;font-weight:700;
                       color:#0f172a;line-height:1.3">
              {periodo_label}
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- TABELA INDIVIDUAL -->
  <tr>
    <td style="padding:24px 40px 0">
      <p style="margin:0 0 14px;font-size:14px;font-weight:700;color:#0f172a;
                padding-left:12px;border-left:3px solid #2d3ab1">Desempenho por Vendedor</p>
      <table width="100%" cellpadding="0" cellspacing="0"
             style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;font-size:12px">
        <thead>
          <tr style="background:linear-gradient(135deg,#1e2a96,#2d3ab1)">
            <th style="padding:12px 18px;color:#fff;text-align:left;font-weight:700">Vendedor</th>
            <th style="padding:12px 10px;color:#c7d2fe;text-align:center;font-weight:500">Contratos</th>
            <th style="padding:12px 10px;color:#93c5fd;text-align:center;font-weight:500">Transp.</th>
            <th style="padding:12px 10px;color:#86efac;text-align:center;font-weight:500">Emb.</th>
            <th style="padding:12px 10px;color:#c4b5fd;text-align:center;font-weight:500">E/T</th>
            <th style="padding:12px 10px;color:#c7d2fe;text-align:right;font-weight:500">Comissão</th>
            <th style="padding:12px 10px;color:#c7d2fe;text-align:right;font-weight:500">Bônus Faixa</th>
            <th style="padding:12px 10px;color:#c7d2fe;text-align:right;font-weight:500">Success Fee</th>
            <th style="padding:12px 18px;color:#fff;text-align:right;font-weight:800">Total R$</th>
          </tr>
        </thead>
        <tbody>{linhas_tabela}</tbody>
        <tfoot>
          <tr style="background:#f1f5f9">
            <td style="padding:14px 18px;font-weight:800;color:#0f172a;
                       border-top:2px solid #cbd5e1">Time</td>
            <td style="padding:14px 10px;font-weight:700;text-align:center;color:#0f172a;
                       border-top:2px solid #cbd5e1">{total_contratos}</td>
            <td style="padding:14px 10px;font-weight:700;text-align:center;color:#1d4ed8;
                       border-top:2px solid #cbd5e1">{total_t}</td>
            <td style="padding:14px 10px;font-weight:700;text-align:center;color:#166534;
                       border-top:2px solid #cbd5e1">{total_e}</td>
            <td style="padding:14px 10px;font-weight:700;text-align:center;color:#6d28d9;
                       border-top:2px solid #cbd5e1">{total_c}</td>
            <td colspan="3" style="border-top:2px solid #cbd5e1"></td>
            <td style="padding:14px 18px;font-weight:900;text-align:right;color:#2d3ab1;
                       border-top:2px solid #cbd5e1;font-size:16px">R$ {total_geral:,.2f}</td>
          </tr>
        </tfoot>
      </table>
    </td>
  </tr>

  <!-- CLIENTES DETALHADOS -->
  {f\'<tr><td style="padding:24px 40px 0"><p style="margin:0 0 14px;font-size:14px;font-weight:700;color:#0f172a;padding-left:12px;border-left:3px solid #2d3ab1">Contratos Fechados por Vendedor</p></td></tr>\' + blocos_clientes if dados_raw else ""}

  <!-- TOTAL FINAL DESTAQUE -->
  <tr>
    <td style="padding:24px 40px">
      <div style="background:linear-gradient(135deg,#1e2a96,#2d3ab1,#4f5fdb);
                  border-radius:12px;padding:24px 28px">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td>
              <p style="margin:0;color:#c7d2fe;font-size:11px;font-weight:600;
                         text-transform:uppercase;letter-spacing:1px">
                Total Pago ao Time no Período
              </p>
              <p style="margin:6px 0 0;color:#ffffff;font-size:30px;font-weight:900;
                         letter-spacing:-1px">R$ {total_geral:,.2f}</p>
            </td>
            <td style="text-align:right;vertical-align:middle">
              <p style="margin:0;color:#a5b4fc;font-size:12px">{len(resultados)} vendedores</p>
              <p style="margin:4px 0 0;color:#ffffff;font-size:15px;font-weight:700">
                {total_contratos} contratos
              </p>
            </td>
          </tr>
        </table>
      </div>
    </td>
  </tr>

  <!-- RODAPÉ -->
  <tr>
    <td class="footer" style="background:#f8faff;padding:20px 40px;
               border-top:1px solid #e2e8f0;text-align:center">
      <p style="margin:0;color:#2d3ab1;font-size:13px;font-weight:700">Mobiis</p>
      <p class="txt-muted" style="margin:4px 0 0;color:#94a3b8;font-size:11px;line-height:1.6">
        Relatório gerado automaticamente pelo Painel Comercial Mobiis.<br>
        {datetime.now().strftime("%d/%m/%Y às %H:%M")} · Documento confidencial.
      </p>
    </td>
  </tr>

</table>
</td></tr></table>
</body></html>"""

def enviar_email(remetente, senha, destinatarios, assunto, corpo):
    msg = MIMEMultipart("alternative")
    msg["From"] = remetente; msg["To"] = ", ".join(destinatarios); msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(remetente, senha)
        s.sendmail(remetente, destinatarios, msg.as_string())

def bloco_email(key, periodo_label):
    st.markdown("---")
    section("✉️", "Enviar Relatório por E-mail")
    with st.expander("⚙️ Configurar envio", expanded=False):
        c1, c2 = st.columns(2)
        rem  = c1.text_input("Remetente (Gmail)", key=f"rem_{key}", placeholder="seu@gmail.com")
        pwd  = c2.text_input("App Password",      key=f"pwd_{key}", type="password",
                              help="myaccount.google.com/apppasswords")
        dest = st.text_input("Destinatários (vírgula)",               key=f"dst_{key}")
        subj = st.text_input("Assunto",
                              value=f"Fechamento Comercial — {periodo_label}", key=f"sbj_{key}")
    if st.button("📧 Enviar Relatório Executivo", key=f"send_{key}", use_container_width=True, type="primary"):
        if not rem or not pwd or not dest:
            st.error("Preencha remetente, senha e destinatários.")
            return
        d = st.session_state.get(f"res_{key}")
        if not d:
            st.error("Calcule antes de enviar.")
            return
        corpo = montar_email(d["resultados"], d["nome_faixa"], d["bonus_faixa"],
                             d["sf_opcao"], d["bonus_sf"], d["total_contratos"],
                             d["total_geral"], periodo_label, d.get("dados_raw"))
        try:
            with st.spinner("Enviando relatório..."):
                enviar_email(rem, pwd, [x.strip() for x in dest.split(",")], subj, corpo)
            st.success("✅ Relatório enviado com sucesso!")
        except smtplib.SMTPAuthenticationError:
            st.error("❌ Autenticação falhou. Use uma App Password do Gmail.")
        except Exception as ex:
            st.error(f"❌ Erro: {ex}")

# ═══════════════════════════════════════════════════════════════
# INTERFACE
# ═══════════════════════════════════════════════════════════════

# Header da página
st.markdown(f"""
<div class="page-header">
  <p class="page-title">Painel Comercial</p>
  <p class="page-sub">Mobiis · {datetime.now().strftime("%B de %Y").capitalize()} · Plataforma de Gestão Comercial</p>
</div>""", unsafe_allow_html=True)

# Success Fee global
sf_opcao = st.selectbox("📈 Success Fee do Time", list(SUCCESS_FEE_MAP.keys()),
    help="Nível de atingimento da meta do time.")
bonus_sf, sf_descricao = SUCCESS_FEE_MAP[sf_opcao]

aba_mes, aba_semana, aba_manual = st.tabs(["📅 Mês Atual", "📆 Semana Atual", "✏️ Entrada Manual"])

# ── ABA MÊS
with aba_mes:
    hoje       = date.today()
    ini_mes    = hoje.replace(day=1).strftime("%Y-%m-%d")
    fim_mes    = hoje.strftime("%Y-%m-%d")
    label_mes  = hoje.strftime("Mês de %B de %Y").capitalize()
    st.info(f"📅 Negócios ganhos de **01/{hoje.month:02d}/{hoje.year}** até hoje, por vendedor.")

    if st.button("🔄 Carregar dados do Pipedrive", key="load_mes", use_container_width=True, type="primary"):
        dados_mes = {}
        with st.spinner("Conectando ao Pipedrive..."):
            for nome, email in VENDEDORES.items():
                try:
                    dados_mes[nome] = carregar_vendedor(email, ini_mes, fim_mes)
                    d = dados_mes[nome]
                    st.success(f"✅ {nome}: {d[\'t\']} Transportadoras · {d[\'e\']} Embarcadores · {d[\'c\']} Emb./Transp.")
                except Exception as ex:
                    st.error(f"❌ {nome}: {ex}")
        if dados_mes:
            res, tc, tg, bf, nf, dr = renderizar(dados_mes, bonus_sf, sf_opcao, sf_descricao, label_mes)
            st.session_state["res_mes"] = dict(
                resultados=res, total_contratos=tc, total_geral=tg,
                bonus_faixa=bf, nome_faixa=nf, bonus_sf=bonus_sf,
                sf_opcao=sf_opcao, dados_raw=dados_mes,
            )
            st.session_state["_mes_ok"] = True

    if "res_mes" in st.session_state and not st.session_state.pop("_mes_ok", False):
        d = st.session_state["res_mes"]
        renderizar(d["dados_raw"], d["bonus_sf"], d["sf_opcao"],
                   SUCCESS_FEE_MAP[d["sf_opcao"]][1], label_mes)

    if "res_mes" in st.session_state:
        bloco_email("mes", label_mes)

# ── ABA SEMANA
with aba_semana:
    hoje      = date.today()
    ini_sem   = (hoje - timedelta(days=hoje.weekday())).strftime("%Y-%m-%d")
    fim_sem   = hoje.strftime("%Y-%m-%d")
    label_sem = f"Semana de {ini_sem} a {fim_sem}"
    st.info(f"📆 Negócios ganhos de **{ini_sem}** (segunda-feira) até hoje.")

    if st.button("🔄 Carregar dados do Pipedrive", key="load_sem", use_container_width=True, type="primary"):
        dados_sem = {}
        with st.spinner("Conectando ao Pipedrive..."):
            for nome, email in VENDEDORES.items():
                try:
                    dados_sem[nome] = carregar_vendedor(email, ini_sem, fim_sem)
                    d = dados_sem[nome]
                    st.success(f"✅ {nome}: {d[\'t\']} Transportadoras · {d[\'e\']} Embarcadores · {d[\'c\']} Emb./Transp.")
                except Exception as ex:
                    st.error(f"❌ {nome}: {ex}")
        if dados_sem:
            res, tc, tg, bf, nf, dr = renderizar(dados_sem, bonus_sf, sf_opcao, sf_descricao, label_sem)
            st.session_state["res_sem"] = dict(
                resultados=res, total_contratos=tc, total_geral=tg,
                bonus_faixa=bf, nome_faixa=nf, bonus_sf=bonus_sf,
                sf_opcao=sf_opcao, dados_raw=dados_sem,
            )
            st.session_state["_sem_ok"] = True

    if "res_sem" in st.session_state and not st.session_state.pop("_sem_ok", False):
        d = st.session_state["res_sem"]
        renderizar(d["dados_raw"], d["bonus_sf"], d["sf_opcao"],
                   SUCCESS_FEE_MAP[d["sf_opcao"]][1], label_sem)

    if "res_sem" in st.session_state:
        bloco_email("sem", label_sem)

# ── ABA MANUAL
with aba_manual:
    st.caption("Simule cenários ou corrija dados manualmente.")
    params = st.query_params
    pre    = {k: params.get(k, d) for k, d in {
        "n0":"Luis Felipe","n1":"Fernando",
        "t0":0,"e0":0,"c0":0,"t1":0,"e1":0,"c1":0,"sf":"0%"
    }.items()}
    auto_run = params.get("run","0") == "1"

    c1, c2 = st.columns(2)
    dados_m = {}
    for idx, (col, n_def, k) in enumerate(zip([c1,c2], [pre["n0"],pre["n1"]], ["0","1"])):
        with col:
            st.markdown(f"**{n_def}**")
            t = int(st.number_input("Transportadoras",           min_value=0,step=1,value=int(pre[f"t{k}"]),key=f"mt{k}"))
            e = int(st.number_input("Embarcadores",              min_value=0,step=1,value=int(pre[f"e{k}"]),key=f"me{k}"))
            c = int(st.number_input("Embarcador/Transportadora", min_value=0,step=1,value=int(pre[f"c{k}"]),key=f"mc{k}"))
            dados_m[n_def] = {"t":t,"e":e,"c":c,"ganhos":[],"perdidos":0}

    label_m = f"Simulação — {datetime.now().strftime('%d/%m/%Y')}"
    if st.button("🚀 Calcular", key="btn_m", use_container_width=True, type="primary") or auto_run:
        renderizar(dados_m, bonus_sf, sf_opcao, sf_descricao, label_m)

# ── TABELA DE FAIXAS
with st.expander("📖 Tabela de Faixas de Bônus", expanded=False):
    st.dataframe(pd.DataFrame([{
        "Faixa": f"Faixa {n}", "Mín. Transportadoras": mt,
        "Mín. Embarcadores": me, "Bônus por Vendedor": f"R$ {b:,.2f}",
    } for n,mt,me,b in reversed(FAIXAS)]), use_container_width=True, hide_index=True)
'''

with open('/mnt/user-data/outputs/dashboard_comercial.py', 'w') as f:
    f.write(code)
print("OK —", len(code), "chars")
PYEOF
Saída

OK — 202116 chars
