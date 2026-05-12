import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES FIXAS
# ─────────────────────────────────────────────────────────────────

PIPEDRIVE_TOKEN = "7b1a84e71f65826c1289de0b5b92cc90474c0b5a"
PIPEDRIVE_BASE  = "https://api.pipedrive.com/v1"
PRODUTO_TRANSP  = "Marketplace de Fretes (Transp)"
PRODUTO_EMB     = "Marketplace de Fretes (Emb)"

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
  .card-time { background:#0f172a; border:1px solid #1d4ed8; border-radius:16px; padding:20px 24px; color:#f1f5f9; margin-bottom:14px; }
  .card-time .linha { margin:6px 0; font-size:15px; }
  .tag-faixa { display:inline-block; background:#1d4ed8; color:white; border-radius:8px; padding:2px 10px; font-size:13px; font-weight:600; }
  .tag-sem-faixa { display:inline-block; background:#475569; color:#cbd5e1; border-radius:8px; padding:2px 10px; font-size:13px; }
  .hint { color:#64748b; font-size:13px; margin:3px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES — PIPEDRIVE API
# ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def buscar_usuarios_pipedrive():
    r = requests.get(f"{PIPEDRIVE_BASE}/users", params={"api_token": PIPEDRIVE_TOKEN})
    usuarios = {}
    if r.ok:
        for u in r.json().get("data") or []:
            usuarios[u["email"].lower()] = u["id"]
    return usuarios

@st.cache_data(ttl=300)
def buscar_produtos_do_negocio(deal_id):
    r = requests.get(f"{PIPEDRIVE_BASE}/deals/{deal_id}/products",
                     params={"api_token": PIPEDRIVE_TOKEN})
    if r.ok and r.json().get("data"):
        return [p["name"] for p in r.json()["data"]]
    return []

@st.cache_data(ttl=300)
def buscar_negocios_ganhos(user_id, data_inicio, data_fim):
    negocios = []
    start = 0
    while True:
        r = requests.get(f"{PIPEDRIVE_BASE}/deals", params={
            "api_token": PIPEDRIVE_TOKEN, "status": "won",
            "user_id": user_id, "start": start, "limit": 100,
        })
        if not r.ok:
            break
        for deal in (r.json().get("data") or []):
            won_date = (deal.get("won_time") or "")[:10]
            if data_inicio <= won_date <= data_fim:
                negocios.append(deal)
        pagination = r.json().get("additional_data", {}).get("pagination", {})
        if pagination.get("more_items_in_collection"):
            start += 100
        else:
            break
    return negocios

def classificar_negocio(deal_id):
    produtos   = buscar_produtos_do_negocio(deal_id)
    tem_transp = any(PRODUTO_TRANSP in p for p in produtos)
    tem_emb    = any(PRODUTO_EMB    in p for p in produtos)
    if tem_transp and tem_emb: return "c"
    elif tem_transp:           return "t"
    elif tem_emb:              return "e"
    return None

def contabilizar_vendedor(email, data_inicio, data_fim):
    user_id = buscar_usuarios_pipedrive().get(email.lower())
    if not user_id:
        return 0, 0, 0
    t = e = c = 0
    for deal in buscar_negocios_ganhos(user_id, data_inicio, data_fim):
        tipo = classificar_negocio(deal["id"])
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
        t_final = t + i; e_final = e + (c - i)
        for num, min_t, min_e, bonus in FAIXAS:
            if t_final >= min_t and e_final >= min_e:
                if bonus > melhor_bonus:
                    melhor_bonus = bonus; melhor_nome = f"Faixa {num}"
                    melhor_t_fin = t_final; melhor_e_fin = e_final
                    melhor_c_t = i; melhor_c_e = c - i
                break
    return melhor_bonus, melhor_nome, (melhor_t_fin, melhor_e_fin), (melhor_c_t, melhor_c_e)

# ─────────────────────────────────────────────────────────────────
# FUNÇÃO — RENDERIZAR RESULTADOS
# ─────────────────────────────────────────────────────────────────

def renderizar_resultados(dados_input, bonus_sf, sf_opcao, sf_descricao):
    total_t = sum(d[1] for d in dados_input)
    total_e = sum(d[2] for d in dados_input)
    total_c = sum(d[3] for d in dados_input)
    bonus_faixa, nome_faixa, dist_time, aloc_c = calcular_melhor_faixa(total_t, total_e, total_c)

    st.subheader("👥 Faixa do Time")
    tag_time = '<span class="tag-sem-faixa">Sem faixa</span>' if nome_faixa == "Sem faixa" \
               else f'<span class="tag-faixa">{nome_faixa}</span>'
    c_t, c_e = aloc_c
    hint_c = f'<div class="hint">↳ Coringas: {c_t} como transportadora · {c_e} como embarcador</div>' if total_c > 0 else ""
    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 Total do time: <b>{total_t}T + {total_e}E + {total_c}C</b> → com coringas: <b>{dist_time[0]}T + {dist_time[1]}E</b></div>
  {hint_c}
  <div class="linha">🏆 Faixa atingida: {tag_time} → <b>R$ {bonus_faixa:,.2f}</b> por vendedor</div>
  <div class="linha">📈 Success Fee ({sf_opcao} · {sf_descricao}): <b>R$ {bonus_sf:,.2f}</b> por vendedor</div>
</div>""", unsafe_allow_html=True)

    st.subheader("💰 Resultado Individual")
    resultados = []
    for nome, t, e, c in dados_input:
        comissao = calcular_comissao(t, e, c)
        total    = comissao + bonus_faixa + bonus_sf
        resultados.append({"nome": nome, "t": t, "e": e, "c": c,
                           "contratos": t+e+c, "comissao": comissao,
                           "bonus_faixa": bonus_faixa, "nome_faixa": nome_faixa,
                           "bonus_sf": bonus_sf, "total": total})
        tag = '<span class="tag-sem-faixa">Sem faixa</span>' if nome_faixa == "Sem faixa" \
              else f'<span class="tag-faixa">{nome_faixa}</span>'
        st.markdown(f"""
<div class="card">
  <h3>{nome}</h3>
  <h2>{t+e+c} contratos · {t} transp. + {e} emb. + {c} coringas</h2>
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

    st.subheader("🏆 Ranking")
    df = pd.DataFrame([{"Vendedor": r["nome"], "Contratos": r["contratos"],
                         "Comissão (R$)": r["comissao"], "Faixa": r["nome_faixa"],
                         "Bônus Faixa (R$)": r["bonus_faixa"], "Success Fee (R$)": r["bonus_sf"],
                         "Total (R$)": r["total"]} for r in resultados]
                      ).sort_values("Total (R$)", ascending=False).reset_index(drop=True)
    df.index += 1; df.index.name = "Pos."
    st.dataframe(df.style.format({"Comissão (R$)": "R$ {:,.2f}", "Bônus Faixa (R$)": "R$ {:,.2f}",
                                   "Success Fee (R$)": "R$ {:,.2f}", "Total (R$)": "R$ {:,.2f}"}),
                 use_container_width=True)

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
# ─────────────────────────────────────────────────────────────────

def montar_email_html(resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                      total_contratos, total_geral, periodo_label):
    linhas = "".join(f"""
        <tr>
          <td style="padding:10px 14px;color:#f1f5f9;font-weight:600">{r['nome']}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:center">{r['contratos']}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:right">R$ {r['comissao']:,.2f}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:center">{r['nome_faixa']}</td>
          <td style="padding:10px 14px;color:#38bdf8;text-align:right;font-weight:700">R$ {r['total']:,.2f}</td>
        </tr>""" for r in resultados)
    return f"""<html><body style="margin:0;padding:0;background:#0f172a;font-family:Arial,sans-serif">
<div style="max-width:640px;margin:32px auto;background:#1e293b;border-radius:16px;overflow:hidden;border:1px solid #334155">
  <div style="background:#1d4ed8;padding:28px 32px">
    <h1 style="margin:0;color:white;font-size:22px">Dashboard Comercial</h1>
    <p style="margin:6px 0 0 0;color:#bfdbfe;font-size:13px">{periodo_label} · {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
  </div>
  <div style="padding:24px 32px 0 32px">
    <p style="color:#e2e8f0;font-size:15px;line-height:1.6;margin:0">Olá! Segue o resultado comercial do período com comissões individuais, faixa do time e bônus de success fee.</p>
  </div>
  <div style="padding:20px 32px">
    <div style="background:#0f172a;border-radius:12px;padding:16px 20px;border:1px solid #1d4ed8">
      <p style="margin:4px 0;color:#f1f5f9;font-size:14px">Faixa: <strong>{nome_faixa}</strong> → R$ {bonus_faixa:,.2f} por vendedor</p>
      <p style="margin:4px 0;color:#f1f5f9;font-size:14px">Success Fee ({sf_opcao}): R$ {bonus_sf:,.2f} por vendedor</p>
      <p style="margin:4px 0;color:#f1f5f9;font-size:14px">Total contratos: <strong>{total_contratos}</strong> · Total ao time: <strong style="color:#38bdf8">R$ {total_geral:,.2f}</strong></p>
    </div>
  </div>
  <div style="padding:0 32px 24px 32px">
    <table style="width:100%;border-collapse:collapse;background:#0f172a;border-radius:12px;overflow:hidden">
      <thead><tr style="background:#1e3a5f">
        <th style="padding:10px 14px;color:#94a3b8;text-align:left;font-size:12px">Vendedor</th>
        <th style="padding:10px 14px;color:#94a3b8;text-align:center;font-size:12px">Contratos</th>
        <th style="padding:10px 14px;color:#94a3b8;text-align:right;font-size:12px">Comissão</th>
        <th style="padding:10px 14px;color:#94a3b8;text-align:center;font-size:12px">Faixa</th>
        <th style="padding:10px 14px;color:#94a3b8;text-align:right;font-size:12px">Total</th>
      </tr></thead>
      <tbody>{linhas}</tbody>
    </table>
  </div>
  <div style="padding:16px 32px;border-top:1px solid #334155;text-align:center">
    <p style="margin:0;color:#475569;font-size:12px">Gerado automaticamente pelo Dashboard Comercial.</p>
  </div>
</div></body></html>"""

def enviar_email(remetente, senha, destinatarios, assunto, corpo_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = remetente; msg["To"] = ", ".join(destinatarios); msg["Subject"] = assunto
    msg.attach(MIMEText(corpo_html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(remetente, senha)
        s.sendmail(remetente, destinatarios, msg.as_string())

def bloco_email(key_prefix, periodo_label):
    """
    Bloco de e-mail totalmente independente — lê os dados do session_state.
    Não recebe resultados como argumento, evitando que o app recarregue ao interagir.
    """
    st.markdown("---")
    st.subheader("✉️ Enviar Resultado por E-mail")

    with st.expander("⚙️ Configurações de e-mail", expanded=False):
        col1, col2 = st.columns(2)
        email_rem = col1.text_input("Remetente", placeholder="seu@empresa.com", key=f"rem_{key_prefix}")
        senha_rem = col2.text_input("Senha", type="password", key=f"sen_{key_prefix}")
        destinat  = st.text_input("Destinatários (separar por vírgula)", key=f"dst_{key_prefix}")
        assunto   = st.text_input("Assunto",
                                  value=f"Resultado Comercial — {periodo_label}",
                                  key=f"ass_{key_prefix}")

    if st.button("📧 Enviar E-mail", key=f"btn_email_{key_prefix}", use_container_width=True):
        if not email_rem or not senha_rem or not destinat:
            st.error("Preencha remetente, senha e destinatários.")
            return
        # lê do session_state — não depende de variáveis locais que somem
        d = st.session_state[f"resultado_{key_prefix}"]
        corpo = montar_email_html(
            d["resultados"], d["nome_faixa"], d["bonus_faixa"],
            d["sf_opcao"], d["bonus_sf"], d["total_contratos"],
            d["total_geral"], periodo_label,
        )
        try:
            with st.spinner("Enviando..."):
                enviar_email(email_rem, senha_rem,
                             [x.strip() for x in destinat.split(",")],
                             assunto, corpo)
            st.success("✅ E-mail enviado com sucesso!")
        except smtplib.SMTPAuthenticationError:
            st.error("❌ Falha na autenticação. Verifique e-mail e senha.")
        except Exception as ex:
            st.error(f"❌ Erro: {ex}")

# ─────────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────────

st.title("📊 Dashboard Comercial")
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
        with st.spinner("Buscando dados no Pipedrive..."):
            for nome, email in VENDEDORES.items():
                t, e, c = contabilizar_vendedor(email, inicio_mes, fim_mes)
                dados.append((nome, t, e, c))
                st.success(f"{nome}: {t}T + {e}E + {c}C")
        res, tc, tg, bf, nf = renderizar_resultados(dados, bonus_sf, sf_opcao, sf_descricao)
        # salva no session_state para persistir ao interagir com o formulário de e-mail
        st.session_state["resultado_mes"] = dict(
            resultados=res, total_contratos=tc, total_geral=tg,
            bonus_faixa=bf, nome_faixa=nf, bonus_sf=bonus_sf, sf_opcao=sf_opcao,
        )

    # re-renderiza resultados e exibe e-mail mesmo após interações do formulário
    if "resultado_mes" in st.session_state:
        d = st.session_state["resultado_mes"]
        # só re-renderiza resultados se o botão NÃO acabou de ser clicado (evita duplicar)
        if not st.session_state.get("_btn_mes_clicado"):
            renderizar_resultados(
                [(r["nome"], r["t"], r["e"], r["c"]) for r in d["resultados"]],
                d["bonus_sf"], d["sf_opcao"],
                SUCCESS_FEE_MAP[d["sf_opcao"]][1],
            )
        bloco_email("mes", label_mes)

    st.session_state["_btn_mes_clicado"] = False

# ─── ABA SEMANA ─────────────────────────────────────────────────
with aba_semana:
    hoje          = date.today()
    inicio_semana = (hoje - timedelta(days=hoje.weekday())).strftime("%Y-%m-%d")
    fim_semana    = hoje.strftime("%Y-%m-%d")
    label_semana  = f"Semana {inicio_semana} a {fim_semana}"

    st.info(f"Negócios ganhos de **{inicio_semana}** (segunda) até hoje.")

    if st.button("🔄 Carregar do Pipedrive", key="btn_sem", use_container_width=True, type="primary"):
        dados = []
        with st.spinner("Buscando dados no Pipedrive..."):
            for nome, email in VENDEDORES.items():
                t, e, c = contabilizar_vendedor(email, inicio_semana, fim_semana)
                dados.append((nome, t, e, c))
                st.success(f"{nome}: {t}T + {e}E + {c}C")
        res, tc, tg, bf, nf = renderizar_resultados(dados, bonus_sf, sf_opcao, sf_descricao)
        st.session_state["resultado_sem"] = dict(
            resultados=res, total_contratos=tc, total_geral=tg,
            bonus_faixa=bf, nome_faixa=nf, bonus_sf=bonus_sf, sf_opcao=sf_opcao,
        )

    if "resultado_sem" in st.session_state:
        d = st.session_state["resultado_sem"]
        if not st.session_state.get("_btn_sem_clicado"):
            renderizar_resultados(
                [(r["nome"], r["t"], r["e"], r["c"]) for r in d["resultados"]],
                d["bonus_sf"], d["sf_opcao"],
                SUCCESS_FEE_MAP[d["sf_opcao"]][1],
            )
        bloco_email("sem", label_semana)

    st.session_state["_btn_sem_clicado"] = False

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
            t = int(st.number_input("Transportadoras", min_value=0, step=1, value=dt, key=f"mt_{idx}"))
            e = int(st.number_input("Embarcadores",    min_value=0, step=1, value=de, key=f"me_{idx}"))
            c = int(st.number_input("Coringas",        min_value=0, step=1, value=dc, key=f"mc_{idx}"))
            dados_manual.append((nome_def, t, e, c))

    if st.button("🚀 Calcular", key="btn_manual", use_container_width=True, type="primary") or auto_run:
        st.markdown("---")
        renderizar_resultados(dados_manual, bonus_sf, sf_opcao, sf_descricao)

# ─── TABELA DE FAIXAS ───────────────────────────────────────────
with st.expander("📖 Tabela de Faixas", expanded=False):
    st.dataframe(pd.DataFrame([{
        "Faixa": f"Faixa {num}", "Mín. Transportadoras": min_t,
        "Mín. Embarcadores": min_e, "Bônus (R$)": f"R$ {bonus:,.2f}",
    } for num, min_t, min_e, bonus in reversed(FAIXAS)]), use_container_width=True, hide_index=True)
