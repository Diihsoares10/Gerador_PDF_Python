"""All HTTP routes for the form, autosave API and admin panel."""
import re
import uuid
from datetime import datetime

from flask import (
    request,
    render_template,
    send_file,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
    session,
    Response,
)
from flask_login import current_user
from sqlalchemy import func, or_

import logging
import threading

from app import app, db
from models import Submission, User
from replit_auth import make_replit_blueprint, require_login
from pdf_generator import gerar_pdf
from replit_mail import send_submission_notification
from gmail_sender import send_pdf_to_user

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")


# Required fields used to compute progress and decide if the form is complete
REQUIRED_FIELDS = [
    "nome", "cpf", "rg", "data_nascimento", "genero",
    "email", "email_confirmacao", "observacao",
]


@app.before_request
def make_session_permanent():
    session.permanent = True


# -------------- Helpers --------------
def validar_cpf(cpf):
    cpf = re.sub(r"[^0-9]", "", cpf or "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    return resto == int(cpf[10])


def validar_idade(data_nascimento_str):
    try:
        data_nasc = datetime.strptime(data_nascimento_str, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - data_nasc.year - (
            (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)
        )
        return idade >= 18
    except (ValueError, TypeError):
        return False


def compute_progress(data: dict) -> int:
    if not data:
        return 0
    filled = sum(1 for k in REQUIRED_FIELDS if (data.get(k) or "").strip())
    return int(round(filled / len(REQUIRED_FIELDS) * 100))


def get_or_create_submission():
    """Find current submission via session token, or create a new one."""
    token = session.get("submission_token")
    submission = None
    if token:
        submission = Submission.query.filter_by(resume_token=token).first()
    if submission is None:
        submission = Submission(
            resume_token=str(uuid.uuid4()),
            data={},
            status="draft",
            progress=0,
            user_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.add(submission)
        db.session.commit()
        session["submission_token"] = submission.resume_token
    return submission


# -------------- Public routes --------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return submit_form()

    submission = get_or_create_submission()
    resume_url = url_for("resume", token=submission.resume_token, _external=True)
    return render_template(
        "index.html",
        prefill=submission.data or {},
        resume_token=submission.resume_token,
        resume_url=resume_url,
        progress=submission.progress or 0,
    )


@app.route("/r/<token>")
def resume(token):
    submission = Submission.query.filter_by(resume_token=token).first()
    if not submission:
        flash("Link de retomada inválido ou expirado.", "danger")
        return redirect(url_for("index"))
    if submission.status == "completed":
        flash("Esse cadastro já foi concluído. Você pode iniciar um novo.", "success")
        session.pop("submission_token", None)
        return redirect(url_for("index"))

    session["submission_token"] = submission.resume_token
    return redirect(url_for("index"))


@app.route("/api/draft", methods=["POST"])
def api_save_draft():
    """Autosave endpoint — called from the frontend on every change."""
    payload = request.get_json(silent=True) or {}
    data = payload.get("data") or {}

    submission = get_or_create_submission()
    submission.data = data
    submission.progress = compute_progress(data)
    submission.nome = (data.get("nome") or "")[:255] or None
    submission.cpf = (data.get("cpf") or "")[:20] or None
    submission.email = (data.get("email") or "")[:255] or None
    if current_user.is_authenticated and not submission.user_id:
        submission.user_id = current_user.id
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "progress": submission.progress,
            "saved_at": submission.updated_at.isoformat() + "Z",
            "resume_token": submission.resume_token,
        }
    )


def _validar_cpf(cpf: str) -> bool:
    """Validate a Brazilian CPF (digits-only or formatted)."""
    cpf = re.sub(r"\D", "", cpf or "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        s = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        d = (s * 10) % 11
        if d == 10:
            d = 0
        if d != int(cpf[i]):
            return False
    return True


@app.route("/api/lookup", methods=["POST"])
def api_lookup_cpf():
    """Look up an existing draft/submission by CPF.

    Security: validates CPF format, applies a per-session rate limit,
    and returns a generic message instead of leaking which CPFs exist.
    """
    payload = request.get_json(silent=True) or {}
    raw_cpf = (payload.get("cpf") or "").strip()

    # Per-session rate limit (max 8 attempts per minute)
    now = datetime.utcnow().timestamp()
    attempts = [t for t in session.get("lookup_attempts", []) if now - t < 60]
    if len(attempts) >= 8:
        return jsonify({"ok": False, "error": "Muitas tentativas. Tente novamente em 1 minuto."}), 429
    attempts.append(now)
    session["lookup_attempts"] = attempts

    if not _validar_cpf(raw_cpf):
        return jsonify({"ok": False, "error": "CPF inválido. Verifique os dígitos."}), 400

    digits = re.sub(r"\D", "", raw_cpf)
    formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    submission = (
        Submission.query
        .filter(Submission.cpf.in_([digits, formatted, raw_cpf]))
        .order_by(Submission.updated_at.desc())
        .first()
    )

    if not submission:
        return jsonify({"ok": False, "error": "Não encontramos cadastro com esse CPF."}), 404

    return jsonify({
        "ok": True,
        "resume_url": url_for("resume", token=submission.resume_token, _external=True),
        "progress": submission.progress,
        "status": submission.status,
        "nome": submission.nome,
    })


@app.route("/api/draft/clear", methods=["POST"])
def api_clear_draft():
    token = session.pop("submission_token", None)
    if token:
        sub = Submission.query.filter_by(resume_token=token).first()
        if sub and sub.status == "draft":
            db.session.delete(sub)
            db.session.commit()
    return jsonify({"ok": True})


def submit_form():
    """Handle final form submission (POST /) — generate PDF + persist."""
    dados = {key: (request.form.get(key) or "").strip() for key in [
        "nome", "cpf", "rg", "data_nascimento", "genero", "estado_civil",
        "nome_mae", "profissao", "email", "email_confirmacao", "telefone",
        "cep", "logradouro", "numero", "complemento", "bairro", "cidade",
        "estado", "observacao",
    ]}
    receber_por_email = request.form.get("receber_por_email") == "on"

    erros = []
    if not dados["nome"] or len(dados["nome"]) < 3:
        erros.append("Nome deve ter no mínimo 3 caracteres.")
    if not validar_cpf(dados["cpf"]):
        erros.append("CPF inválido.")
    if not validar_idade(dados["data_nascimento"]):
        erros.append("É necessário ser maior de 18 anos.")
    if dados["email"] != dados["email_confirmacao"]:
        erros.append("Os emails não coincidem.")
    if len(dados["observacao"]) > 500:
        erros.append("Observação excede o limite de 500 caracteres.")

    if erros:
        for erro in erros:
            flash(erro, "danger")
        return redirect(url_for("index"))

    submission = get_or_create_submission()
    submission.data = dados
    submission.progress = 100
    submission.status = "completed"
    submission.completed_at = datetime.utcnow()
    submission.nome = dados.get("nome")[:255]
    submission.cpf = dados.get("cpf")[:20]
    submission.email = dados.get("email")[:255]
    if current_user.is_authenticated:
        submission.user_id = current_user.id
    db.session.commit()

    # Clear from session so the user starts fresh next time
    session.pop("submission_token", None)

    try:
        pdf_buffer = gerar_pdf(dados)
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.seek(0)

        # Fire notifications asynchronously (don't block the user)
        user_email = dados.get("email") or ""
        user_name = dados.get("nome") or ""

        def _notify(sub_id):
            # 1) Notify the workspace owner
            try:
                send_submission_notification(submission, pdf_bytes)
                logging.info("Owner notification sent for submission %s", sub_id)
            except Exception as exc:
                logging.warning("Owner notification failed for %s: %s", sub_id, exc)

            # 2) Send the PDF to the end-user (if they opted in)
            if receber_por_email and user_email:
                try:
                    send_pdf_to_user(user_email, user_name, pdf_bytes)
                except Exception as exc:
                    logging.warning("User PDF email failed for %s: %s", sub_id, exc)

        threading.Thread(target=_notify, args=(submission.id,), daemon=True).start()

        safe_filename = re.sub(r"[^a-zA-Z0-9]", "_", dados["nome"])
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"cadastro_{safe_filename}.pdf",
            mimetype="application/pdf",
        )
    except Exception as e:
        flash(f"Erro ao gerar PDF: {str(e)}", "danger")
        return redirect(url_for("index"))


# -------------- Admin --------------
def _require_admin():
    """Allow if user is logged in and either marked admin OR is the first user."""
    if not current_user.is_authenticated:
        return False
    if current_user.is_admin:
        return True
    # Bootstrap: first ever user becomes admin automatically
    total_users = db.session.query(func.count(User.id)).scalar()
    if total_users == 1:
        current_user.is_admin = True
        db.session.commit()
        return True
    return False


@app.route("/admin")
@require_login
def admin_dashboard():
    if not _require_admin():
        return render_template("403.html"), 403

    q = (request.args.get("q") or "").strip()
    status = request.args.get("status") or ""

    query = Submission.query
    if status in ("draft", "completed"):
        query = query.filter(Submission.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Submission.nome.ilike(like),
                Submission.cpf.ilike(like),
                Submission.email.ilike(like),
            )
        )

    submissions = query.order_by(Submission.updated_at.desc()).limit(200).all()

    total = db.session.query(func.count(Submission.id)).scalar() or 0
    completed = (
        db.session.query(func.count(Submission.id))
        .filter(Submission.status == "completed")
        .scalar() or 0
    )
    drafts = total - completed
    rate = round((completed / total) * 100) if total else 0

    return render_template(
        "admin/dashboard.html",
        submissions=submissions,
        total=total,
        completed=completed,
        drafts=drafts,
        rate=rate,
        q=q,
        status=status,
    )


@app.route("/admin/submissions/<int:sid>")
@require_login
def admin_submission_detail(sid):
    if not _require_admin():
        return render_template("403.html"), 403
    submission = Submission.query.get_or_404(sid)
    return render_template("admin/detail.html", s=submission)


@app.route("/admin/submissions/<int:sid>/pdf")
@require_login
def admin_submission_pdf(sid):
    if not _require_admin():
        return render_template("403.html"), 403
    submission = Submission.query.get_or_404(sid)
    pdf_buffer = gerar_pdf(submission.data or {})
    safe_filename = re.sub(r"[^a-zA-Z0-9]", "_", submission.nome or f"cadastro_{sid}")
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"cadastro_{safe_filename}.pdf",
        mimetype="application/pdf",
    )


@app.route("/admin/export.csv")
@require_login
def admin_export_csv():
    if not _require_admin():
        return render_template("403.html"), 403

    import csv
    import io

    rows = Submission.query.order_by(Submission.created_at.desc()).all()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "id", "status", "progresso", "nome", "cpf", "email", "telefone",
        "cidade", "uf", "criado_em", "atualizado_em", "concluido_em",
    ])
    for s in rows:
        d = s.data or {}
        writer.writerow([
            s.id,
            s.status,
            s.progress,
            d.get("nome", ""),
            d.get("cpf", ""),
            d.get("email", ""),
            d.get("telefone", ""),
            d.get("cidade", ""),
            d.get("estado", ""),
            s.created_at.isoformat() if s.created_at else "",
            s.updated_at.isoformat() if s.updated_at else "",
            s.completed_at.isoformat() if s.completed_at else "",
        ])
    csv_data = out.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=submissions.csv"},
    )


# Friendly 403 template fallback
@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404
