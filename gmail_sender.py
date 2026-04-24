"""Send email via Gmail SMTP using an App Password.

The credentials live in two environment variables:
- GMAIL_USER: the full Gmail address (e.g., name@gmail.com)
- GMAIL_APP_PASSWORD: 16-character app password (spaces tolerated)
"""
import logging
import os
import smtplib
from email.message import EmailMessage


def _get_credentials():
    user = (os.environ.get("GMAIL_USER") or "").strip()
    password = (os.environ.get("GMAIL_APP_PASSWORD") or "").replace(" ", "")
    if not user or not password:
        raise RuntimeError("GMAIL_USER and GMAIL_APP_PASSWORD must be set")
    return user, password


def send_pdf_to_user(to_email: str, nome: str, pdf_bytes: bytes) -> None:
    """Send the generated cadastro PDF to the end-user via Gmail SMTP."""
    user, password = _get_credentials()

    msg = EmailMessage()
    msg["Subject"] = "Seu cadastro foi concluído — PDF em anexo"
    msg["From"] = f"Cadastro Digital <{user}>"
    msg["To"] = to_email

    text = (
        f"Olá, {nome}!\n\n"
        "Recebemos seu cadastro com sucesso. Em anexo segue o PDF com todas as informações que você preencheu.\n\n"
        "Guarde este email — ele serve como comprovante.\n\n"
        "— Cadastro Digital"
    )
    msg.set_content(text)

    html = f"""
    <!doctype html>
    <html>
      <body style="margin:0; padding:24px; background:#f6f7fb; font-family:-apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color:#1f2937;">
        <div style="max-width:560px; margin:0 auto; background:#ffffff; border-radius:14px; overflow:hidden; box-shadow:0 6px 24px rgba(15, 23, 42, 0.08);">
          <div style="background:linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding:28px 24px; color:white;">
            <h1 style="margin:0; font-size:22px; font-weight:600;">Cadastro concluído</h1>
            <p style="margin:6px 0 0; opacity:0.9; font-size:14px;">Olá, {nome}!</p>
          </div>
          <div style="padding:24px;">
            <p style="margin:0 0 12px; line-height:1.55;">Recebemos seu cadastro com sucesso. O PDF com todas as informações que você preencheu está anexado a este email.</p>
            <p style="margin:0 0 12px; line-height:1.55;">Guarde este email — ele serve como comprovante.</p>
            <p style="margin:24px 0 0; color:#64748b; font-size:13px;">Se você não solicitou este cadastro, pode ignorar esta mensagem com segurança.</p>
          </div>
          <div style="background:#f6f7fb; padding:14px 24px; color:#94a3b8; font-size:12px; text-align:center;">
            Enviado automaticamente por Cadastro Digital
          </div>
        </div>
      </body>
    </html>
    """
    msg.add_alternative(html, subtype="html")

    safe = "".join(c if c.isalnum() else "_" for c in (nome or "cadastro"))
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=f"cadastro_{safe}.pdf",
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    logging.info("PDF email sent to %s", to_email)
