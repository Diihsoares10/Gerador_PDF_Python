# Sistema de Cadastro e Geração de PDF

## Overview
Flask-based web application for user registration with automatic PDF report generation. Built with Python, Flask, ReportLab, and Bootstrap 5. Server-side validates CPF, age (18+), email confirmation, and generates a downloadable PDF.

## Project Structure
- `main.py`: Entry point (`from app import app`)
- `app.py`: Flask app + SQLAlchemy initialization
- `models.py`: `User`, `OAuth`, `Submission` (JSONB data, `resume_token`, status, progress)
- `replit_auth.py`: Replit Auth (OpenID Connect) blueprint and `@require_login`
- `routes.py`: All HTTP endpoints (form, autosave API, resume-by-token, admin panel, CSV export)
- `pdf_generator.py`: ReportLab PDF generation logic
- `templates/index.html`: Main form UI (with prefill from DB + share-link modal)
- `templates/admin/dashboard.html` & `detail.html`: Admin panel
- `templates/403.html`, `templates/404.html`: Error pages
- `static/js/script.js`: Validation, masks, server autosave, theme, share modal
- `static/css/style.css`: Glassmorphism design system + admin/modal styles

## Replit Setup
- Language: Python 3.12, PostgreSQL (DATABASE_URL)
- Workflow: `Server` runs `python main.py` on port 5000
- Deployment: autoscale with Gunicorn (`app:app`)
- Env: `SESSION_SECRET`, `REPL_ID`, `DATABASE_URL` (managed by platform)

## Phase 1 — SaaS foundation (current)
- PostgreSQL persistence for every submission (drafts + completed)
- Server-side autosave via `POST /api/draft` (debounced ~1s)
- Resume-by-link: every visit gets a unique `/r/<uuid>` URL — share modal in top bar
- Replit Auth login at `/auth/login`, logout at `/auth/logout`
- Admin panel at `/admin`: stats, search/filter, paginated table, detail view, PDF re-download, CSV export
- First user to log in becomes admin automatically (`User.is_admin`)

## Recent Changes
- 2026-04-24: Imported from GitHub. Bound Flask to `0.0.0.0:5000` and configured deployment.
- 2026-04-24: UI redesign — glassmorphism, light/dark mode, in-field icons, real-time validation, progress bar, ViaCEP autofill, animated blobs, a11y.
- 2026-04-24: Phase 1 — added PostgreSQL + SQLAlchemy, `Submission` model with JSONB, server-side draft autosave, resume-by-link, Replit Auth, admin panel with search/filter/CSV export.
- 2026-04-24: Email notifications — added `replit_mail.py` helper and async notification on form submission. Sends a styled HTML summary plus the generated PDF as an attachment to the workspace owner's verified email.

## Recent UX overhaul (Apr 2026)
- **Landing screen** added before the form (`#landing` in `templates/index.html`): eyebrow badge, gradient headline, 3 tip cards, big "Começar agora" CTA. Shown when there is no draft; hidden automatically when the user lands via a resume URL `/r/<token>`.
- **Multi-step form (4 steps)**: Pessoais → Contato → Endereço → Revisão. Stepper at the top + percentage progress bar + per-step required-field validation in `static/js/script.js` (`stepRequired` map). Step 4 renders a read-only review (`#reviewGrid`) before submission. Autosave continues to fire on every input.
- **Dark-mode select fix**: replaced the native `<select>` for `genero` and `estado_civil` with custom `.choice-card` radio buttons (file-based icons + label). They use the same theme tokens as the rest of the form, so they are fully legible in both themes. Native selects (if reintroduced) get a forced color/background fix in CSS so options stay readable on dark backgrounds.

## CPF lookup (Apr 2026)
- New endpoint `POST /api/lookup` (`routes.py`): accepts `{cpf}`, validates format with the official mod-11 algorithm (`_validar_cpf`), applies a per-session rate limit (8 attempts/min, returns HTTP 429), then queries `Submission` matching either the digits-only or formatted version of the CPF (column already indexed). Returns the resume URL + name + progress + status, or HTTP 400/404 with a generic message — never reveals which CPFs exist.
- Landing screen got a secondary button **"Já tenho cadastro · continuar pelo CPF"** that swaps to a dedicated lookup card (`#lookupCard`): icon, big centered CPF input with IMask, "Buscar cadastro" button with spinner, and "Não tenho cadastro — começar do zero" fallback.
- On a successful match the JS shows a personalised greeting (`Olá, <primeiro nome>`) and redirects the browser to the resume URL after 800ms, dropping the user back into the multi-step form pre-filled with everything they had.
