import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import io
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", layout="wide")

# ─────────────────────────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .card {
    background: #1e293b; border: 1px solid #334155;
    border-radius: 16px; padding: 20px 24px; margin-bottom: 14px; color: #f1f5f9;
  }
  .card h3 { margin: 0 0 4px 0; color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
  .card h2 { margin: 0 0 12px 0; color: #f8fafc; font-size: 20px; }
  .card .linha { margin: 5px 0; font-size: 15px; }
  .card .total { color: #38bdf8; font-size: 24px; font-weight: 700; margin-top: 14px; border-top: 1px solid #334155; padding-top: 10px; }
  .card-time { background: #0f172a; border: 1px solid #1d4ed8; border-radius: 16px; padding: 20px 24px; color: #f1f5f9; margin-bottom: 14px; }
  .card-time .linha { margin: 6px 0; font-size: 15px; }
  .tag-faixa { display: inline-block; background: #1d4ed8; color: white; border-radius: 8px; padding: 2px 10px; font-size: 13px; font-weight: 600; }
  .tag-sem-faixa { display: inline-block; background: #475569; color: #cbd5e1; border-radius: 8px; padding: 2px 10px; font-size: 13px; }
  .hint { color: #64748b; font-size: 13px; margin-top: 3px; margin-bottom: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────

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

def calcular_comissao(t, e, c):
    return (t + e + c) * COMISSAO_POR_CONTRATO

def calcular_melhor_faixa(t, e, c):
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
# FUNÇÃO — GERAR IMAGEM PNG
# ─────────────────────────────────────────────────────────────────

def gerar_imagem(resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                 total_t, total_e, total_c, dist_time, aloc_c, total_contratos, total_geral):
    n = len(resultados)
    fig_height = 3.5 + n * 2.8
    fig, ax = plt.subplots(figsize=(10, fig_height))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, fig_height)
    ax.axis("off")
    fig.patch.set_facecolor("#0f172a")

    y = fig_height - 0.5
    ax.text(5, y, "Dashboard Comercial", ha="center", va="top",
            fontsize=18, fontweight="bold", color="#f8fafc")
    y -= 0.5
    ax.text(5, y, datetime.now().strftime("Gerado em %d/%m/%Y às %H:%M"),
            ha="center", va="top", fontsize=9, color="#64748b")
    y -= 0.6

    card_h = 1.4
    rect = FancyBboxPatch((0.3, y - card_h), 9.4, card_h,
                          boxstyle="round,pad=0.1", linewidth=1.5,
                          edgecolor="#1d4ed8", facecolor="#0f172a")
    ax.add_patch(rect)
    c_t, c_e = aloc_c
    coringa_txt = f"  ↳ Coringas: {c_t} como transp. · {c_e} como embarc." if total_c > 0 else ""
    ax.text(0.7, y - 0.2, f"Time: {total_t}T + {total_e}E + {total_c}C  →  {dist_time[0]}T + {dist_time[1]}E",
            va="top", fontsize=10, color="#94a3b8")
    ax.text(0.7, y - 0.55, f"Faixa: {nome_faixa}  →  R$ {bonus_faixa:,.2f} por vendedor{coringa_txt}",
            va="top", fontsize=10, color="#f1f5f9", fontweight="bold")
    ax.text(0.7, y - 0.9, f"Success Fee ({sf_opcao}):  R$ {bonus_sf:,.2f} por vendedor",
            va="top", fontsize=10, color="#f1f5f9")
    y -= card_h + 0.3

    for r in resultados:
        card_h = 2.2
        rect = FancyBboxPatch((0.3, y - card_h), 9.4, card_h,
                              boxstyle="round,pad=0.1", linewidth=1,
                              edgecolor="#334155", facecolor="#1e293b")
        ax.add_patch(rect)
        ax.text(0.7, y - 0.2, r["nome"].upper(), va="top", fontsize=9, color="#94a3b8", fontweight="bold")
        ax.text(0.7, y - 0.55, f"{r['contratos']} contratos  ·  {r['t']}T + {r['e']}E + {r['c']}C",
                va="top", fontsize=11, color="#f8fafc", fontweight="bold")
        ax.text(0.7, y - 0.95,  f"Comissão:       R$ {r['comissao']:>10,.2f}", va="top", fontsize=10, color="#e2e8f0", fontfamily="monospace")
        ax.text(0.7, y - 1.28, f"Bônus faixa:    R$ {r['bonus_faixa']:>10,.2f}", va="top", fontsize=10, color="#e2e8f0", fontfamily="monospace")
        ax.text(0.7, y - 1.61, f"Success fee:    R$ {r['bonus_sf']:>10,.2f}",   va="top", fontsize=10, color="#e2e8f0", fontfamily="monospace")
        ax.plot([0.7, 9.7], [y - 1.82, y - 1.82], color="#334155", linewidth=0.8)
        ax.text(0.7, y - 2.0, "TOTAL", va="top", fontsize=12, color="#38bdf8", fontweight="bold")
        ax.text(9.7, y - 2.0, f"R$ {r['total']:,.2f}", ha="right", va="top", fontsize=13, color="#38bdf8", fontweight="bold")
        y -= card_h + 0.25

    ax.text(0.7, y - 0.1, "Total pago ao time:", va="top", fontsize=10, color="#64748b")
    ax.text(9.7, y - 0.1, f"R$ {total_geral:,.2f}", ha="right", va="top", fontsize=11, color="#64748b", fontweight="bold")

    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf

# ─────────────────────────────────────────────────────────────────
# FUNÇÃO — MONTAR CORPO DO E-MAIL (HTML)
# ─────────────────────────────────────────────────────────────────

def montar_corpo_email(resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                       total_contratos, total_geral, mensagem_extra):
    mes_ano = datetime.now().strftime("%B/%Y").capitalize()
    linhas_vendedores = ""
    for r in resultados:
        linhas_vendedores += f"""
        <tr>
          <td style="padding:10px 14px;color:#f1f5f9;font-weight:600">{r['nome']}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:center">{r['contratos']}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:right">R$ {r['comissao']:,.2f}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:center">{r['nome_faixa']}</td>
          <td style="padding:10px 14px;color:#38bdf8;text-align:right;font-weight:700">R$ {r['total']:,.2f}</td>
        </tr>"""

    html = f"""
    <html><body style="margin:0;padding:0;background:#0f172a;font-family:Arial,sans-serif">
    <div style="max-width:640px;margin:32px auto;background:#1e293b;border-radius:16px;overflow:hidden;border:1px solid #334155">

      <!-- Cabeçalho -->
      <div style="background:#1d4ed8;padding:28px 32px">
        <h1 style="margin:0;color:white;font-size:22px">📊 Resultado Comercial — {mes_ano}</h1>
        <p style="margin:6px 0 0 0;color:#bfdbfe;font-size:13px">
          Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        </p>
      </div>

      <!-- Mensagem personalizada -->
      <div style="padding:24px 32px 0 32px">
        <p style="color:#e2e8f0;font-size:15px;line-height:1.6;margin:0">
          {mensagem_extra}
        </p>
      </div>

      <!-- Resumo do time -->
      <div style="padding:20px 32px">
        <div style="background:#0f172a;border-radius:12px;padding:16px 20px;border:1px solid #1d4ed8">
          <p style="margin:0 0 6px 0;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:1px">Resultado do Time</p>
          <p style="margin:4px 0;color:#f1f5f9;font-size:14px">
            🏆 Faixa atingida: <strong style="color:white">{nome_faixa}</strong>
            &nbsp;→&nbsp; <strong>R$ {bonus_faixa:,.2f}</strong> por vendedor
          </p>
          <p style="margin:4px 0;color:#f1f5f9;font-size:14px">
            📈 Success Fee ({sf_opcao}): <strong>R$ {bonus_sf:,.2f}</strong> por vendedor
          </p>
          <p style="margin:4px 0;color:#f1f5f9;font-size:14px">
            📦 Total de contratos: <strong>{total_contratos}</strong>
            &nbsp;·&nbsp; 💵 Total pago ao time: <strong style="color:#38bdf8">R$ {total_geral:,.2f}</strong>
          </p>
        </div>
      </div>

      <!-- Tabela individual -->
      <div style="padding:0 32px 24px 32px">
        <table style="width:100%;border-collapse:collapse;background:#0f172a;border-radius:12px;overflow:hidden">
          <thead>
            <tr style="background:#1e3a5f">
              <th style="padding:10px 14px;color:#94a3b8;text-align:left;font-size:12px">Vendedor</th>
              <th style="padding:10px 14px;color:#94a3b8;text-align:center;font-size:12px">Contratos</th>
              <th style="padding:10px 14px;color:#94a3b8;text-align:right;font-size:12px">Comissão</th>
              <th style="padding:10px 14px;color:#94a3b8;text-align:center;font-size:12px">Faixa</th>
              <th style="padding:10px 14px;color:#94a3b8;text-align:right;font-size:12px">Total</th>
            </tr>
          </thead>
          <tbody>{linhas_vendedores}</tbody>
        </table>
      </div>

      <!-- Rodapé -->
      <div style="padding:16px 32px;border-top:1px solid #334155;text-align:center">
        <p style="margin:0;color:#475569;font-size:12px">
          Este e-mail foi gerado automaticamente pelo Dashboard Comercial.
        </p>
      </div>
    </div>
    </body></html>
    """
    return html

# ─────────────────────────────────────────────────────────────────
# FUNÇÃO — ENVIAR E-MAIL VIA SMTP (Outlook/Corporativo)
# ─────────────────────────────────────────────────────────────────

def enviar_email(remetente, senha, destinatarios, assunto, corpo_html, img_buf, servidor_smtp, porta):
    msg = MIMEMultipart("related")
    msg["From"]    = remetente
    msg["To"]      = ", ".join(destinatarios)
    msg["Subject"] = assunto

    # Parte alternativa (HTML)
    alternativa = MIMEMultipart("alternative")
    msg.attach(alternativa)
    alternativa.attach(MIMEText(corpo_html, "html", "utf-8"))

    # Imagem como anexo
    img_buf.seek(0)
    img_anexo = MIMEImage(img_buf.read(), name="resultado_comercial.png")
    img_anexo.add_header("Content-Disposition", "attachment", filename="resultado_comercial.png")
    msg.attach(img_anexo)

    contexto = ssl.create_default_context()
    with smtplib.SMTP(servidor_smtp, porta) as server:
        server.ehlo()
        server.starttls(context=contexto)
        server.login(remetente, senha)
        server.sendmail(remetente, destinatarios, msg.as_string())

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
    nome3 = col_n3.text_input("Vendedor 3", value="Outro")

nomes = [nome1, nome2, nome3]

sf_opcao = st.selectbox("📈 Success Fee do Time", list(SUCCESS_FEE_MAP.keys()),
    help="Meta do time atingida. Bônus pago integralmente a cada vendedor, sem rateio.")
bonus_sf, sf_descricao = SUCCESS_FEE_MAP[sf_opcao]

# ─────────────────────────────────────────────────────────────────
# INTERFACE — INPUTS
# ─────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📋 Contratos por Vendedor")

col1, col2, col3 = st.columns(3)
dados_input = []

for idx, (col, nome) in enumerate(zip([col1, col2, col3], nomes)):
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

    total_t = sum(d[1] for d in dados_input)
    total_e = sum(d[2] for d in dados_input)
    total_c = sum(d[3] for d in dados_input)

    bonus_faixa, nome_faixa, dist_time, aloc_c = calcular_melhor_faixa(total_t, total_e, total_c)

    st.markdown("---")

    # ── Faixa do time
    st.subheader("👥 Faixa do Time")
    tag_time = '<span class="tag-sem-faixa">Sem faixa</span>' if nome_faixa == "Sem faixa" \
               else f'<span class="tag-faixa">{nome_faixa}</span>'
    c_t, c_e = aloc_c
    hint_c = f'<div class="hint">↳ Coringas do time: {c_t} como transportadora · {c_e} como embarcador</div>' if total_c > 0 else ""

    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 Total do time: <b>{total_t}T + {total_e}E + {total_c}C</b> → com coringas: <b>{dist_time[0]}T + {dist_time[1]}E</b></div>
  {hint_c}
  <div class="linha">🏆 Faixa atingida: {tag_time} → <b>R$ {bonus_faixa:,.2f}</b> por vendedor</div>
  <div class="linha">📈 Success Fee ({sf_opcao} · {sf_descricao}): <b>R$ {bonus_sf:,.2f}</b> por vendedor</div>
</div>
""", unsafe_allow_html=True)

    # ── Resultados individuais
    st.subheader("💰 Resultado Individual")
    resultados = []
    for nome, t, e, c in dados_input:
        comissao = calcular_comissao(t, e, c)
        total    = comissao + bonus_faixa + bonus_sf
        resultados.append({
            "nome": nome, "t": t, "e": e, "c": c,
            "contratos": t + e + c, "comissao": comissao,
            "bonus_faixa": bonus_faixa, "nome_faixa": nome_faixa,
            "bonus_sf": bonus_sf, "total": total,
        })
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
</div>
""", unsafe_allow_html=True)

    total_contratos = sum(r["contratos"] for r in resultados)
    total_geral     = sum(r["total"]     for r in resultados)

    st.subheader("💵 Resumo Financeiro do Time")
    st.markdown(f"""
<div class="card-time">
  <div class="linha">📦 <b>Total de Contratos:</b> {total_contratos}</div>
  <div class="linha">💵 <b>Total Pago ao Time:</b> R$ {total_geral:,.2f}</div>
</div>
""", unsafe_allow_html=True)

    # ── Ranking
    st.subheader("🏆 Ranking")
    df = pd.DataFrame([{
        "Vendedor": r["nome"], "Contratos": r["contratos"],
        "Comissão (R$)": r["comissao"], "Faixa": r["nome_faixa"],
        "Bônus Faixa (R$)": r["bonus_faixa"], "Success Fee (R$)": r["bonus_sf"],
        "Total (R$)": r["total"],
    } for r in resultados]).sort_values("Total (R$)", ascending=False).reset_index(drop=True)
    df.index += 1; df.index.name = "Pos."
    st.dataframe(df.style.format({
        "Comissão (R$)": "R$ {:,.2f}", "Bônus Faixa (R$)": "R$ {:,.2f}",
        "Success Fee (R$)": "R$ {:,.2f}", "Total (R$)": "R$ {:,.2f}",
    }), use_container_width=True)

    with st.expander("📖 Tabela de Faixas", expanded=False):
        st.dataframe(pd.DataFrame([{
            "Faixa": f"Faixa {num}", "Mín. Transportadoras": min_t,
            "Mín. Embarcadores": min_e, "Bônus (R$)": f"R$ {bonus:,.2f}",
        } for num, min_t, min_e, bonus in reversed(FAIXAS)]), use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────
    # EXPORTAR IMAGEM
    # ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📸 Compartilhar Resultado")

    img_buf = gerar_imagem(resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                           total_t, total_e, total_c, dist_time, aloc_c,
                           total_contratos, total_geral)

    st.image(img_buf, caption="Preview do resultado", use_container_width=True)
    img_buf.seek(0)

    nome_arquivo = f"resultado_comercial_{datetime.now().strftime('%d%m%Y_%H%M')}.png"
    st.download_button(
        label="⬇️ Baixar imagem (PNG)",
        data=img_buf,
        file_name=nome_arquivo,
        mime="image/png",
        use_container_width=True,
    )

    # ─────────────────────────────────────────────────────────────
    # ENVIO DE E-MAIL
    # ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("✉️ Enviar por E-mail")

    with st.expander("⚙️ Configurações de E-mail", expanded=True):
        st.caption("Suas credenciais são usadas apenas nesta sessão e nunca são salvas.")

        col_smtp1, col_smtp2 = st.columns(2)
        servidor_smtp = col_smtp1.text_input("Servidor SMTP", value="smtp.office365.com",
                            help="Outlook/Office365: smtp.office365.com | Gmail: smtp.gmail.com")
        porta_smtp    = col_smtp2.number_input("Porta", value=587, min_value=1, max_value=9999)

        col_e1, col_e2 = st.columns(2)
        email_remetente = col_e1.text_input("Seu e-mail (remetente)")
        senha_email     = col_e2.text_input("Senha / App Password", type="password",
                            help="Para Office365 use sua senha normal. Para Gmail use uma 'App Password'.")

        destinatarios_raw = st.text_input(
            "Destinatários",
            placeholder="email1@empresa.com, email2@empresa.com",
            help="Separe múltiplos e-mails por vírgula."
        )

        assunto_email = st.text_input(
            "Assunto",
            value=f"Resultado Comercial — {datetime.now().strftime('%B/%Y').capitalize()}"
        )

        mensagem_extra = st.text_area(
            "Mensagem personalizada",
            value="Olá, segue o resultado comercial do mês. Em anexo você encontrará o resumo detalhado com as comissões individuais, faixa atingida pelo time e bônus de success fee.",
            height=100
        )

    if st.button("📧 Enviar E-mail", use_container_width=True, type="primary"):
        # Validações
        erros = []
        if not email_remetente:
            erros.append("Informe o e-mail remetente.")
        if not senha_email:
            erros.append("Informe a senha.")
        if not destinatarios_raw.strip():
            erros.append("Informe pelo menos um destinatário.")

        if erros:
            for e in erros:
                st.error(e)
        else:
            destinatarios = [d.strip() for d in destinatarios_raw.split(",") if d.strip()]
            corpo_html = montar_corpo_email(
                resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                total_contratos, total_geral, mensagem_extra
            )

            # Gera nova cópia da imagem para o e-mail
            img_email = gerar_imagem(
                resultados, nome_faixa, bonus_faixa, sf_opcao, bonus_sf,
                total_t, total_e, total_c, dist_time, aloc_c,
                total_contratos, total_geral
            )

            try:
                with st.spinner("Enviando e-mail..."):
                    enviar_email(
                        remetente=email_remetente,
                        senha=senha_email,
                        destinatarios=destinatarios,
                        assunto=assunto_email,
                        corpo_html=corpo_html,
                        img_buf=img_email,
                        servidor_smtp=servidor_smtp,
                        porta=int(porta_smtp),
                    )
                st.success(f"✅ E-mail enviado com sucesso para: {', '.join(destinatarios)}")
            except smtplib.SMTPAuthenticationError:
                st.error("❌ Falha na autenticação. Verifique seu e-mail e senha.")
            except smtplib.SMTPConnectError:
                st.error(f"❌ Não foi possível conectar ao servidor {servidor_smtp}:{int(porta_smtp)}.")
            except Exception as ex:
                st.error(f"❌ Erro ao enviar: {ex}")
