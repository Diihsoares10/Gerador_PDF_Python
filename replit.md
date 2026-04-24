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
