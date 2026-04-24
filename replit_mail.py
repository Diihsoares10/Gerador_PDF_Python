"""Send email via the Replit Mail service. Emails are delivered to the
verified Replit account email of the workspace owner — there is no
recipient field to set."""
import base64
import logging
import os
import subprocess
from typing import List, Optional

import requests


def _get_auth_token():
    hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
    if not hostname:
        raise RuntimeError("REPLIT_CONNECTORS_HOSTNAME is not set")
    result = subprocess.run(
        ["replit", "identity", "create", "--audience", f"https://{hostname}"],
        capture_output=True, text=True, check=True,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("Replit identity token was empty")
    return f"Bearer {token}", hostname


def send_email(
    subject: str,
    text: Optional[str] = None,
    html: Optional[str] = None,
    attachments: Optional[List[dict]] = None,
):
    """Send an email. `attachments` is a list of {filename, content (bytes), content_type}."""
    auth_token, hostname = _get_auth_token()

    body = {"subject": subject}
    if text is not None:
        body["text"] = text
    if html is not None:
        body["html"] = html
    if attachments:
        body["attachments"] = [
            {
                "filename": a["filename"],
                "content": base64.b64encode(a["content"]).decode("ascii"),
                "contentType": a.get("content_type", "application/octet-stream"),
                "encoding": "base64",
            }
            for a in attachments
        ]

    resp = requests.post(
        f"https://{hostname}/api/v2/mailer/send",
        headers={
            "Content-Type": "application/json",
            "Replit-Authentication": auth_token,
        },
        json=body,
        timeout=15,
    )
    if not resp.ok:
        try:
            err = resp.json().get("message")
        except Exception:
            err = resp.text
        raise RuntimeError(f"Mail send failed ({resp.status_code}): {err}")
    return resp.json()


def send_submission_notification(submission, pdf_bytes: bytes):
    """Notify admin that a new submission has been completed."""
    d = submission.data or {}
    nome = d.get("nome", "Sem nome")

    text_lines = [
        "Olá!",
        "",
        f"Um novo cadastro foi concluído no Cadastro Digital.",
        "",
        f"  Nome:     {d.get('nome', '—')}",
        f"  CPF:      {d.get('cpf', '—')}",
        f"  Email:    {d.get('email', '—')}",
        f"  Telefone: {d.get('telefone', '—')}",
        f"  Cidade:   {d.get('cidade', '—')} / {d.get('estado', '—')}",
        "",
        f"O PDF gerado está anexado a este email.",
        "",
        "— Cadastro Digital",
    ]

    html = f"""
    <div style="font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width:560px; margin:0 auto; padding:24px;">
      <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding:20px; border-radius:12px; color:white; margin-bottom:20px;">
        <h2 style="margin:0; font-weight:600;">Novo cadastro concluído</h2>
        <p style="margin:6px 0 0; opacity:0.9;">{nome}</p>
      </div>
      <table style="width:100%; border-collapse:collapse;">
        <tr><td style="padding:8px 0; color:#64748b;">Nome</td><td style="padding:8px 0; font-weight:500;">{d.get('nome','—')}</td></tr>
        <tr><td style="padding:8px 0; color:#64748b;">CPF</td><td style="padding:8px 0; font-weight:500;">{d.get('cpf','—')}</td></tr>
        <tr><td style="padding:8px 0; color:#64748b;">Email</td><td style="padding:8px 0; font-weight:500;">{d.get('email','—')}</td></tr>
        <tr><td style="padding:8px 0; color:#64748b;">Telefone</td><td style="padding:8px 0; font-weight:500;">{d.get('telefone','—')}</td></tr>
        <tr><td style="padding:8px 0; color:#64748b;">Cidade</td><td style="padding:8px 0; font-weight:500;">{d.get('cidade','—')} / {d.get('estado','—')}</td></tr>
      </table>
      <p style="color:#64748b; font-size:13px; margin-top:24px;">O PDF completo está anexado a este email.</p>
    </div>
    """

    safe = "".join(c if c.isalnum() else "_" for c in (nome or "cadastro"))
    return send_email(
        subject=f"Novo cadastro: {nome}",
        text="\n".join(text_lines),
        html=html,
        attachments=[
            {
                "filename": f"cadastro_{safe}.pdf",
                "content": pdf_bytes,
                "content_type": "application/pdf",
            }
        ],
    )
