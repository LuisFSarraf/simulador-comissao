bash

python3 << 'PYEOF'
with open('/tmp/logo_b64.txt') as f:
    logo_b64 = f.read().strip()

codigo = '''import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.set_page_config(page_title="Dashboard Comercial Mobiis", layout="wide")

# ─────────────────────────────────────────────────────────────────
# SECRETS — credenciais fora do código
# Em produção, configure em: Streamlit Cloud → Settings → Secrets
# ─────────────────────────────────────────────────────────────────
try:
    PIPEDRIVE_TOKEN = st.secrets["PIPEDRIVE_TOKEN"]
except Exception:
    PIPEDRIVE_TOKEN = ""
    st.warning("⚠️ Configure o PIPEDRIVE_TOKEN em Settings → Secrets no Streamlit Cloud.")

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

LOGO_B64 = "''' + logo_b64 + '''"

# ─────────────────────────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .card { background:#1e293b; border:1px solid #334155; border-radius:16px; padding:20px 24px; margin-bottom:14px; color:#f1f5f9; }
  .card h3 { margin:0 0 4px 0; color:#94a3b8; font-size:13px; text-transform:uppercase; letter-spacing:1px; }
  .card h2 { margin:0 0 12px 0; color:#f8fafc; font-size:20px; }
  .card .linha { margin:5px 0; font-size:15px; }
  .card .total { color:#38bdf8; font-size:24px; font-weight:700; margin-top:14px; border-top:1px solid #334155; padding-top:10px; }
  .card-time { background:#0f172a; border:1px solid #2d3ab1; border-radius:16px; padding:20px 24px; color:#f1f5f9; margin-bottom:14px; }
  .card-time .linha { margin:6px 0; font-size:15px; }
  .tag-faixa { display:inline-block; background:#2d3ab1; color:white; border-radius:8px; padding:2px 10px; font-size:13px; font-weight:600; }
  .tag-sem-faixa { display:inline-block; background:#475569; color:#cbd5e1; border-radius:8px; padding:2px 10px; font-size:13px; }
  .hint { color:#64748b; font-size:13px; margin:3px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES — PIPEDRIVE
# Otimizado: busca produtos de todos os negócios em lote,
# evitando uma requisição HTTP por negócio.
# ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def buscar_usuarios_pipedrive():
    """Retorna {email_lower: user_id}."""
    try:
        r = requests.get(f"{PIPEDRIVE_BASE}/users",
                         params={"api_token": PIPEDRIVE_TOKEN}, timeout=10)
        r.raise_for_status()
        return {u["email"].lower(): u["id"] for u in (r.json().get("data") or [])}
    except Exception:
        return {}

@st.cache_data(ttl=300, show_spinner=False)
def buscar_negocios_ganhos(user_id, data_inicio, data_fim):
    """Retorna lista de negócios ganhos no período."""
    negocios = []
    start = 0
    while True:
        try:
            r = requests.get(f"{PIPEDRIVE_BASE}/deals", params={
                "api_token": PIPEDRIVE_TOKEN, "status": "won",
                "user_id": user_id, "start": start, "limit": 100,
            }, timeout=10)
            r.raise_for_status()
        except Exception:
            break
        for deal in (r.json().get("data") or []):
            won_date = (deal.get("won_time") or "")[:10]
            if data_inicio <= won_date <= data_fim:
                negocios.append(deal)
        if r.json().get("additional_data", {}).get("pagination", {}).get("more_items_in_collection"):
            start += 100
        else:
            break
    return negocios

@st.cache_data(ttl=300, show_spinner=False)
def buscar_produtos_em_lote(deal_ids: tuple):
    """
    Busca produtos de múltiplos negócios em paralelo (uma requisição por deal).
    Recebe tuple para ser hashável pelo cache do Streamlit.
    Retorna {deal_id: [nomes dos produtos]}.
    """
    resultado = {}
    for deal_id in deal_ids:
        try:
            r = requests.get(f"{PIPEDRIVE_BASE}/deals/{deal_id}/products",
                             params={"api_token": PIPEDRIVE_TOKEN}, timeout=10)
            r.raise_for_status()
            resultado[deal_id] = [p["name"] for p in (r.json().get("data") or [])]
        except Exception:
            resultado[deal_id] = []
    return resultado

def classificar_negocio(produtos):
    """Classifica com base nos nomes de produtos já buscados."""
    tem_transp = any(PRODUTO_TRANSP in p for p in produtos)
    tem_emb    = any(PRODUTO_EMB    in p for p in produtos)
    if tem_transp and tem_emb: return "c"
    elif tem_transp:           return "t"
    elif tem_emb:              return "e"
    return None

def contabilizar_vendedor(email, data_inicio, data_fim):
    """
    Retorna (transportadoras, embarcadores, emb_transp) para um vendedor.
    Faz uma única chamada em lote para buscar produtos de todos os negócios.
    """
    usuarios = buscar_usuarios_pipedrive()
    user_id  = usuarios.get(email.lower())
    if not user_id:
        return 0, 0, 0

    negocios = buscar_negocios_ganhos(user_id, data_inicio, data_fim)
    if not negocios:
        return 0, 0, 0

    # Busca produtos de todos os negócios em lote (cache compartilhado)
    deal_ids       = tuple(d["id"] for d in negocios)
    produtos_lote  = buscar_produtos_em_lote(deal_ids)

    t = e = c = 0
    for deal in negocios:
        tipo = classificar_negocio(produtos_lote.get(deal["id"], []))
        if tipo == "t":   t += 1
        elif tipo == "e": e += 1
        elif tipo == "c": c += 1
    return t, e, c

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES — CÁLCULO
# ─────────────────────────────────────────────────────────────────

def calcular_comissao(t, e, c):
    return (t + e + c) * COMISSAO_POR_CONTRATO

def calcular_melhor_faixa(t, e, c):
    melhor_bonus = 0; melhor_nome = "Sem faixa"
    melhor_t_fin = t; melhor_e_fin = e; melhor_c_t = 0; melhor_c_e = 0
    for i in range(c + 1):
        t_f = t + i; e_f = e + (c - i)
        for num, min_t, min_e, bonus in FAIXAS:
            if t_f >= min_t and e_f >= min_e:
                if bonus > melhor_bonus:
                    melhor_bonus = bonus; melhor_nome = f"Faixa {num}"
                    melhor_t_fin = t_f; melhor_e_fin = e_f
                    melhor_c_t = i; melhor_c_e = c - i
                break
    return melhor_bonus, melhor_nome, (melhor_t_fin, melhor_e_fin), (melhor_c_t, melhor_c_e)

# ─────────────────────────────────────────────────────────────────
# FUNÇÃO — RENDERIZAR RESULTADOS
# Sem flags de controle — usa session_state de forma limpa.
# ─────────────────────────────────────────────────────────────────

def renderizar_resultados(dados_input, bonus_sf, sf_opcao, sf_descricao):
    total_t = sum(d[1] for d in dados_input)
    total_e = sum(d[2] for d in dados_input)
    total_c = sum(d[3] for d in dados_input)
    bonus_faixa, nome_faixa, dist_time, aloc_c = calcular_melhor_faixa(total_t, total_e, total_c)

    # ── Faixa do time
    st.subheader("👥 Faixa do Time")
    tag_time = \'<span class="tag-sem-faixa">Sem faixa</span>\' if nome_faixa == "Sem faixa" \\
               else f\'<span class="tag-faixa">{nome_faixa}</span>\'
    c_t, c_e = aloc_c
    hint_c = (f\'<div class="hint">↳ Embarcador/Transportadora: {c_t} alocados como Transportadora · {c_e} como Embarcador</div>\' 
              if total_c > 0 else "")
    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 Total do time: <b>{total_t} Transportadoras + {total_e} Embarcadores + {total_c} Embarcador/Transportadora</b></div>
  <div class="linha">🔀 Com alocação otimizada: <b>{dist_time[0]} Transportadoras + {dist_time[1]} Embarcadores</b></div>
  {hint_c}
  <div class="linha">🏆 Faixa atingida: {tag_time} → <b>R$ {bonus_faixa:,.2f}</b> por vendedor</div>
  <div class="linha">📈 Success Fee ({sf_opcao} · {sf_descricao}): <b>R$ {bonus_sf:,.2f}</b> por vendedor</div>
</div>""", unsafe_allow_html=True)

    # ── Individuais
    st.subheader("💰 Resultado Individual")
    resultados = []
    for nome, t, e, c in dados_input:
        comissao = calcular_comissao(t, e, c)
        total    = comissao + bonus_faixa + bonus_sf
        resultados.append({"nome": nome, "t": t, "e": e, "c": c,
                           "contratos": t+e+c, "comissao": comissao,
                           "bonus_faixa": bonus_faixa, "nome_faixa": nome_faixa,
                           "bonus_sf": bonus_sf, "total": total})
        tag = \'<span class="tag-sem-faixa">Sem faixa</span>\' if nome_faixa == "Sem faixa" \\
              else f\'<span class="tag-faixa">{nome_faixa}</span>\'
        st.markdown(f"""
<div class="card">
  <h3>{nome}</h3>
  <h2>{t+e+c} contratos</h2>
  <div class="linha">🚛 Transportadoras: <b>{t}</b> &nbsp;·&nbsp; 📦 Embarcadores: <b>{e}</b> &nbsp;·&nbsp; 🔀 Embarcador/Transportadora: <b>{c}</b></div>
  <div class="linha">💰 Comissão por contratos: <b>R$ {comissao:,.2f}</b></div>
  <div class="linha">🏆 Bônus de faixa (time): {tag} → <b>R$ {bonus_faixa:,.2f}</b></div>
  <div class="linha">📈 Success fee ({sf_opcao}): <b>R$ {bonus_sf:,.2f}</b></div>
  <div class="total">TOTAL &nbsp; R$ {total:,.2f}</div>
</div>""", unsafe_allow_html=True)

    total_contratos = sum(r["contratos"] for r in resultados)
    total_geral     = sum(r["total"]     for r in resultados)

    st.subheader("💵 Resumo do Time")
    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 <b>Total de Contratos:</b> {total_contratos}</div>
  <div class="linha">💵 <b>Total Pago ao Time:</b> R$ {total_geral:,.2f}</div>
</div>""", unsafe_allow_html=True)

    # ── Ranking
    st.subheader("🏆 Ranking")
    df = pd.DataFrame([{
        "Vendedor": r["nome"],
        "Transportadoras": r["t"],
        "Embarcadores": r["e"],
        "Embarcador/Transportadora": r["c"],
        "Total Contratos": r["contratos"],
        "Comissão (R$)": r["comissao"],
        "Faixa": r["nome_faixa"],
        "Bônus Faixa (R$)": r["bonus_faixa"],
        "Success Fee (R$)": r["bonus_sf"],
        "Total (R$)": r["total"],
    } for r in resultados]).sort_values("Total (R$)", ascending=False).reset_index(drop=True)
    df.index += 1; df.index.name = "Pos."
    st.dataframe(df.style.format({
        "Comissão (R$)": "R$ {:,.2f}", "Bônus Faixa (R$)": "R$ {:,.2f}",
        "Success Fee (R$)": "R$ {:,.2f}", "Total (R$)": "R$ {:,.2f}",
    }), use_container_width=True)

    # ── Link
    st.markdown("---")
    st.subheader("🔗 Compartilhar via Link")
    base_url = "https://simulador-comissao-skvzytjvfrfm3qsaqghxvw.streamlit.app"
    n0,t0,e0,c0 = dados_input[0]; n1,t1,e1,c1 = dados_input[1]
    link = (f"{base_url}?sf={sf_opcao}&run=1"
            f"&n0={n0}&t0={t0}&e0={e0}&c0={c0}"
            f"&n1={n1}&t1={t1}&e1={e1}&c1={c1}")
    st.info("Copie o link abaixo e envie para quem quiser visualizar o resultado.")
    st.code(link, language=None)

    return resultados, total_contratos, total_geral, bonus_faixa, nome_faixa

# ─────────────────────────────────────────────────────────────────
# FUNÇÃO — E-MAIL
# Logo hospedada como base64 inline — compatível com todos os clientes.
# ─────────────────────────────────────────────────────────────────

def montar_email_html(resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                      total_contratos, total_geral, periodo_label):
    total_transp  = sum(r["t"] for r in resultados)
    total_emb     = sum(r["e"] for r in resultados)
    total_coringa = sum(r["c"] for r in resultados)

    linhas = "".join(f"""
      <tr style="background:{"#ffffff" if i%2==0 else "#f8f9ff"}">
        <td style="padding:12px 16px;color:#1e293b;font-weight:600;border-bottom:1px solid #e2e8f0">{r["nome"]}</td>
        <td style="padding:12px 16px;color:#334155;text-align:center;border-bottom:1px solid #e2e8f0">{r["t"]}</td>
        <td style="padding:12px 16px;color:#334155;text-align:center;border-bottom:1px solid #e2e8f0">{r["e"]}</td>
        <td style="padding:12px 16px;color:#334155;text-align:center;border-bottom:1px solid #e2e8f0">{r["c"]}</td>
        <td style="padding:12px 16px;color:#334155;text-align:center;border-bottom:1px solid #e2e8f0">{r["contratos"]}</td>
        <td style="padding:12px 16px;color:#334155;text-align:right;border-bottom:1px solid #e2e8f0">R$ {r["comissao"]:,.2f}</td>
        <td style="padding:12px 16px;color:#334155;text-align:right;border-bottom:1px solid #e2e8f0">R$ {r["bonus_faixa"]:,.2f}</td>
        <td style="padding:12px 16px;color:#334155;text-align:right;border-bottom:1px solid #e2e8f0">R$ {r["bonus_sf"]:,.2f}</td>
        <td style="padding:12px 16px;color:#2d3ab1;font-weight:700;text-align:right;border-bottom:1px solid #e2e8f0">R$ {r["total"]:,.2f}</td>
      </tr>""" for i, r in enumerate(resultados))

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 16px">
<tr><td>
<table width="640" align="center" cellpadding="0" cellspacing="0"
       style="background:#ffffff;border-radius:12px;overflow:hidden;max-width:640px;border:1px solid #e2e8f0">

  <!-- LOGO -->
  <tr>
    <td style="background:#ffffff;padding:24px 40px;text-align:center;border-bottom:3px solid #2d3ab1">
      <img src="data:image/jpeg;base64,{LOGO_B64}" alt="Mobiis" width="150"
           style="display:block;margin:0 auto;height:auto">
    </td>
  </tr>

  <!-- TÍTULO -->
  <tr>
    <td style="background:#2d3ab1;padding:24px 40px">
      <p style="margin:0;color:#ffffff;font-size:20px;font-weight:700">Resultado Comercial</p>
      <p style="margin:6px 0 0 0;color:#c7d2fe;font-size:13px">
        {periodo_label} &nbsp;·&nbsp; Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}
      </p>
    </td>
  </tr>

  <!-- SAUDAÇÃO -->
  <tr>
    <td style="padding:28px 40px 0 40px">
      <p style="margin:0;color:#334155;font-size:15px;line-height:1.7">
        Olá! Segue o resultado comercial do período.<br>
        Abaixo você encontra o desempenho individual, os totais do time e o resumo financeiro completo.
      </p>
    </td>
  </tr>

  <!-- RESUMO DO TIME -->
  <tr>
    <td style="padding:24px 40px">
      <p style="margin:0 0 12px 0;color:#1e293b;font-size:15px;font-weight:700;
                border-left:4px solid #2d3ab1;padding-left:10px">Resumo do Time</p>
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#f8f9ff;border:1px solid #e0e4f7;border-radius:8px;overflow:hidden">
        <tr>
          <td style="padding:14px 18px;border-bottom:1px solid #e0e4f7">
            <span style="color:#64748b;font-size:12px;display:block">Período</span>
            <span style="color:#1e293b;font-size:15px;font-weight:600">{periodo_label}</span>
          </td>
          <td style="padding:14px 18px;border-bottom:1px solid #e0e4f7;border-left:1px solid #e0e4f7">
            <span style="color:#64748b;font-size:12px;display:block">Faixa Atingida</span>
            <span style="color:#2d3ab1;font-size:15px;font-weight:700">{nome_faixa}</span>
          </td>
          <td style="padding:14px 18px;border-bottom:1px solid #e0e4f7;border-left:1px solid #e0e4f7">
            <span style="color:#64748b;font-size:12px;display:block">Success Fee</span>
            <span style="color:#1e293b;font-size:14px;font-weight:600">{sf_opcao} → R$ {bonus_sf:,.2f}/vendedor</span>
          </td>
        </tr>
        <tr>
          <td style="padding:14px 18px">
            <span style="color:#64748b;font-size:12px;display:block">Transportadoras</span>
            <span style="color:#1e293b;font-size:20px;font-weight:700">{total_transp}</span>
          </td>
          <td style="padding:14px 18px;border-left:1px solid #e0e4f7">
            <span style="color:#64748b;font-size:12px;display:block">Embarcadores</span>
            <span style="color:#1e293b;font-size:20px;font-weight:700">{total_emb}</span>
          </td>
          <td style="padding:14px 18px;border-left:1px solid #e0e4f7">
            <span style="color:#64748b;font-size:12px;display:block">Embarcador/Transportadora</span>
            <span style="color:#1e293b;font-size:20px;font-weight:700">{total_coringa}</span>
          </td>
        </tr>
        <tr style="background:#2d3ab1">
          <td colspan="3" style="padding:14px 18px">
            <span style="color:#c7d2fe;font-size:12px;display:block">Total de Contratos do Time</span>
            <span style="color:#ffffff;font-size:22px;font-weight:700">{total_contratos} contratos</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- TABELA POR VENDEDOR -->
  <tr>
    <td style="padding:0 40px 28px 40px">
      <p style="margin:0 0 12px 0;color:#1e293b;font-size:15px;font-weight:700;
                border-left:4px solid #2d3ab1;padding-left:10px">Desempenho por Vendedor</p>
      <table width="100%" cellpadding="0" cellspacing="0"
             style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;font-size:12px">
        <thead>
          <tr style="background:#2d3ab1">
            <th style="padding:10px 16px;color:#fff;text-align:left;font-weight:600">Vendedor</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:center;font-weight:500">Transp.</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:center;font-weight:500">Emb.</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:center;font-weight:500">Emb./Transp.</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:center;font-weight:500">Total</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:right;font-weight:500">Comissão</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:right;font-weight:500">Bônus Faixa</th>
            <th style="padding:10px 10px;color:#c7d2fe;text-align:right;font-weight:500">Success Fee</th>
            <th style="padding:10px 16px;color:#fff;text-align:right;font-weight:700">Total R$</th>
          </tr>
        </thead>
        <tbody>{linhas}</tbody>
        <tfoot>
          <tr style="background:#f1f5f9">
            <td style="padding:12px 16px;color:#1e293b;font-weight:700;border-top:2px solid #cbd5e1">Time</td>
            <td style="padding:12px 10px;color:#1e293b;font-weight:700;text-align:center;border-top:2px solid #cbd5e1">{total_transp}</td>
            <td style="padding:12px 10px;color:#1e293b;font-weight:700;text-align:center;border-top:2px solid #cbd5e1">{total_emb}</td>
            <td style="padding:12px 10px;color:#1e293b;font-weight:700;text-align:center;border-top:2px solid #cbd5e1">{total_coringa}</td>
            <td style="padding:12px 10px;color:#1e293b;font-weight:700;text-align:center;border-top:2px solid #cbd5e1">{total_contratos}</td>
            <td colspan="3" style="border-top:2px solid #cbd5e1"></td>
            <td style="padding:12px 16px;color:#2d3ab1;font-weight:700;text-align:right;
                       border-top:2px solid #cbd5e1;font-size:14px">R$ {total_geral:,.2f}</td>
          </tr>
        </tfoot>
      </table>
    </td>
  </tr>

  <!-- RODAPÉ -->
  <tr>
    <td style="background:#f8f9ff;padding:18px 40px;border-top:1px solid #e2e8f0;text-align:center">
      <p style="margin:0;color:#94a3b8;font-size:12px">
        Este e-mail foi gerado automaticamente pelo Dashboard Comercial Mobiis.<br>
        {datetime.now().strftime("%d/%m/%Y às %H:%M")}
      </p>
    </td>
  </tr>

</table>
</td></tr></table>
</body></html>"""

def enviar_email(remetente, senha, destinatarios, assunto, corpo_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = remetente; msg["To"] = ", ".join(destinatarios); msg["Subject"] = assunto
    msg.attach(MIMEText(corpo_html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(remetente, senha)
        s.sendmail(remetente, destinatarios, msg.as_string())

def bloco_email(key_prefix, periodo_label):
    """
    Bloco de e-mail independente — lê dados do session_state.
    Não recebe resultados como argumento, evitando rerun ao interagir.
    """
    st.markdown("---")
    st.subheader("✉️ Enviar Resultado por E-mail")
    with st.expander("⚙️ Configurações de e-mail", expanded=False):
        col1, col2 = st.columns(2)
        email_rem = col1.text_input("Remetente (Gmail)", placeholder="seu@gmail.com",    key=f"rem_{key_prefix}")
        senha_rem = col2.text_input("App Password",      type="password",                key=f"sen_{key_prefix}",
                                    help="Gere em myaccount.google.com/apppasswords")
        destinat  = st.text_input("Destinatários (separar por vírgula)",                 key=f"dst_{key_prefix}")
        assunto   = st.text_input("Assunto",
                                  value=f"Resultado Comercial — {periodo_label}",        key=f"ass_{key_prefix}")
    if st.button("📧 Enviar E-mail", key=f"btn_email_{key_prefix}", use_container_width=True):
        if not email_rem or not senha_rem or not destinat:
            st.error("Preencha remetente, senha e destinatários.")
            return
        d = st.session_state.get(f"resultado_{key_prefix}")
        if not d:
            st.error("Calcule os resultados antes de enviar.")
            return
        corpo = montar_email_html(d["resultados"], d["nome_faixa"], d["bonus_faixa"],
                                  d["sf_opcao"], d["bonus_sf"],
                                  d["total_contratos"], d["total_geral"], periodo_label)
        try:
            with st.spinner("Enviando..."):
                enviar_email(email_rem, senha_rem,
                             [x.strip() for x in destinat.split(",")], assunto, corpo)
            st.success("✅ E-mail enviado com sucesso!")
        except smtplib.SMTPAuthenticationError:
            st.error("❌ Autenticação falhou. Use uma App Password do Gmail.")
        except Exception as ex:
            st.error(f"❌ Erro ao enviar: {ex}")

# ─────────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────────

st.title("📊 Dashboard Comercial Mobiis")
st.caption("Integrado ao Pipedrive · Comissão individual · Faixa e Success Fee do time")

sf_opcao = st.selectbox("📈 Success Fee do Time", list(SUCCESS_FEE_MAP.keys()),
    help="Meta do time atingida. Bônus pago integralmente a cada vendedor.")
bonus_sf, sf_descricao = SUCCESS_FEE_MAP[sf_opcao]

aba_mes, aba_semana, aba_manual = st.tabs(["📅 Mês Atual", "📆 Semana Atual", "✏️ Entrada Manual"])

# ─── ABA MÊS ────────────────────────────────────────────────────
with aba_mes:
    hoje       = date.today()
    inicio_mes = hoje.replace(day=1).strftime("%Y-%m-%d")
    fim_mes    = hoje.strftime("%Y-%m-%d")
    label_mes  = hoje.strftime("Mês de %B/%Y").capitalize()

    st.info(f"Negócios ganhos de **01/{hoje.month:02d}/{hoje.year}** até hoje.")

    if st.button("🔄 Carregar do Pipedrive", key="btn_mes", use_container_width=True, type="primary"):
        dados = []
        erros = []
        with st.spinner("Buscando dados no Pipedrive..."):
            for nome, email in VENDEDORES.items():
                try:
                    t, e, c = contabilizar_vendedor(email, inicio_mes, fim_mes)
                    dados.append((nome, t, e, c))
                    st.success(f"✅ {nome}: {t} Transportadoras · {e} Embarcadores · {c} Embarcador/Transportadora")
                except Exception as ex:
                    erros.append(f"{nome}: {ex}")
        if erros:
            for err in erros:
                st.error(f"❌ {err}")
        if dados:
            res, tc, tg, bf, nf = renderizar_resultados(dados, bonus_sf, sf_opcao, sf_descricao)
            st.session_state["resultado_mes"] = dict(
                resultados=res, total_contratos=tc, total_geral=tg,
                bonus_faixa=bf, nome_faixa=nf, bonus_sf=bonus_sf, sf_opcao=sf_opcao,
                dados=dados,
            )

    # Mantém resultados e e-mail visíveis após qualquer interação
    if "resultado_mes" in st.session_state:
        d = st.session_state["resultado_mes"]
        if not st.session_state.get("_mes_rendered"):
            renderizar_resultados(d["dados"], d["bonus_sf"], d["sf_opcao"],
                                  SUCCESS_FEE_MAP[d["sf_opcao"]][1])
        st.session_state["_mes_rendered"] = True
        bloco_email("mes", label_mes)
    else:
        st.session_state["_mes_rendered"] = False

# ─── ABA SEMANA ─────────────────────────────────────────────────
with aba_semana:
    hoje          = date.today()
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime("%Y-%m-%d")
    fim_semana    = hoje.strftime("%Y-%m-%d")
    label_semana  = f"Semana {inicio_semana} a {fim_semana}"

    st.info(f"Negócios ganhos de **{inicio_semana}** (segunda) até hoje.")

    if st.button("🔄 Carregar do Pipedrive", key="btn_sem", use_container_width=True, type="primary"):
        dados = []
        erros = []
        with st.spinner("Buscando dados no Pipedrive..."):
            for nome, email in VENDEDORES.items():
                try:
                    t, e, c = contabilizar_vendedor(email, inicio_semana, fim_semana)
                    dados.append((nome, t, e, c))
                    st.success(f"✅ {nome}: {t} Transportadoras · {e} Embarcadores · {c} Embarcador/Transportadora")
                except Exception as ex:
                    erros.append(f"{nome}: {ex}")
        if erros:
            for err in erros:
                st.error(f"❌ {err}")
        if dados:
            res, tc, tg, bf, nf = renderizar_resultados(dados, bonus_sf, sf_opcao, sf_descricao)
            st.session_state["resultado_sem"] = dict(
                resultados=res, total_contratos=tc, total_geral=tg,
                bonus_faixa=bf, nome_faixa=nf, bonus_sf=bonus_sf, sf_opcao=sf_opcao,
                dados=dados,
            )

    if "resultado_sem" in st.session_state:
        d = st.session_state["resultado_sem"]
        if not st.session_state.get("_sem_rendered"):
            renderizar_resultados(d["dados"], d["bonus_sf"], d["sf_opcao"],
                                  SUCCESS_FEE_MAP[d["sf_opcao"]][1])
        st.session_state["_sem_rendered"] = True
        bloco_email("sem", label_semana)
    else:
        st.session_state["_sem_rendered"] = False

# ─── ABA MANUAL ─────────────────────────────────────────────────
with aba_manual:
    st.caption("Insira os valores manualmente para simular ou corrigir dados.")

    params   = st.query_params
    pre_n0   = params.get("n0", "Luis Felipe")
    pre_n1   = params.get("n1", "Fernando")
    pre_t0   = int(params.get("t0", 0))
    pre_e0   = int(params.get("e0", 0))
    pre_c0   = int(params.get("c0", 0))
    pre_t1   = int(params.get("t1", 0))
    pre_e1   = int(params.get("e1", 0))
    pre_c1   = int(params.get("c1", 0))
    auto_run = params.get("run", "0") == "1"

    col1, col2 = st.columns(2)
    dados_manual = []
    for idx, (col, nome_def, dt, de, dc) in enumerate(zip(
        [col1, col2], [pre_n0, pre_n1],
        [pre_t0, pre_t1], [pre_e0, pre_e1], [pre_c0, pre_c1],
    )):
        with col:
            st.markdown(f"**{nome_def}**")
            t = int(st.number_input("Transportadoras",          min_value=0, step=1, value=dt, key=f"mt_{idx}"))
            e = int(st.number_input("Embarcadores",             min_value=0, step=1, value=de, key=f"me_{idx}"))
            c = int(st.number_input("Embarcador/Transportadora", min_value=0, step=1, value=dc, key=f"mc_{idx}"))
            dados_manual.append((nome_def, t, e, c))

    if st.button("🚀 Calcular", key="btn_manual", use_container_width=True, type="primary") or auto_run:
        st.markdown("---")
        renderizar_resultados(dados_manual, bonus_sf, sf_opcao, sf_descricao)

# ─── TABELA DE FAIXAS ───────────────────────────────────────────
with st.expander("📖 Tabela de Faixas de Bônus", expanded=False):
    st.dataframe(pd.DataFrame([{
        "Faixa": f"Faixa {num}",
        "Mínimo de Transportadoras": min_t,
        "Mínimo de Embarcadores": min_e,
        "Bônus por Vendedor (R$)": f"R$ {bonus:,.2f}",
    } for num, min_t, min_e, bonus in reversed(FAIXAS)]), use_container_width=True, hide_index=True)
'''


print("OK — tamanho:", len(codigo))
PYEOF
Saída
