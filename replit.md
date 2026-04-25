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

## Color palette refresh (Apr 2026)
- Replaced the old indigo→purple→pink palette with a modern **Indigo + Sky + Teal** SaaS palette (no magenta/pink). The brand colors now read as more professional/trustworthy.
- New CSS variables in `:root` and `[data-theme="dark"]` (`static/css/style.css`):
  - **Light**: `--primary #4f46e5`, `--primary-hover #4338ca`, `--primary-active #3730a3`, `--secondary #0ea5e9`, `--tertiary #14b8a6`. Background gradient is now `#eef2ff → #e0f2fe → #ccfbf1`. Blobs use indigo, sky, teal.
  - **Dark**: `--primary #818cf8`, `--primary-hover #a5b4fc`, `--primary-active #6366f1`, `--secondary #38bdf8`, `--tertiary #2dd4bf`. Background gradient `#0b1226 → #0f1a3a → #0c2438`. Blobs lifted to stay visible on the deeper navy base.
- Existing tokens (`--accent`, `--accent-2`, `--accent-gradient`, `--field-focus`, `--field-focus-ring`) now alias to the new primary, so every component (buttons, inputs, progress bar, stepper, choice-cards, modals) updated automatically without touching component-level CSS.
- Brand renamed in `templates/index.html`: header now says **"Cadastramento!"** (was "Cadastro Digital"); `<title>` and `theme-color` meta tag updated to match.

## Admin: delete submission (Apr 2026)
- New protected route `POST /admin/submissions/<sid>/delete` (`routes.py`): admin-only, deletes the row from `submissions` and flashes a success message.
- `templates/admin/dashboard.html` table: each row now has a 🗑️ icon button (red on hover) inside an inline form. JS `confirm()` asks before submitting, and the current search/status filters are preserved on the redirect back.
- `templates/admin/detail.html`: red **"Excluir"** button next to "Baixar PDF". After deletion the user is sent back to the dashboard list with the success flash.
- New CSS classes: `.row-action-danger` (icon button in the table), `.btn-danger` (full-size red button), `.inline-form` helper. Both reuse the existing `--error` token, so they automatically work in light and dark modes.

## Notify system — toasts + confirm modal (Apr 2026)
- New file `static/js/notify.js` exposes `window.Notify`:
  - `Notify.toast({ type, title, message, duration })` and shortcuts `Notify.success/error/warning/info(message[, title])` — slide-in cards (bottom-right on desktop, bottom-full on mobile) with icon, progress bar, hover-to-pause, click-to-dismiss, auto-dismiss after 4.5 s (errors 6 s).
  - `Notify.confirm({ title, message, confirmText, cancelText, danger })` — returns `Promise<boolean>`, blurred backdrop, focus-trap helpers (Esc cancels, Enter confirms, focus restored).
  - Global `submit` listener auto-intercepts any `<form data-confirm="…">` and replaces the native dialog.
- New CSS appended to `static/css/style.css`: `.toast-container/.toast/.toast-icon/.toast-progress` and `.confirm-overlay/.confirm-card/.confirm-icon/.confirm-actions`. All tokens come from existing palette so light/dark themes work automatically. Danger variants reuse `--error` red.
- `static/js/script.js`: "Limpar" button now uses `Notify.confirm` (danger) and follows up with a success toast before reload.
- `templates/admin/dashboard.html` + `templates/admin/detail.html`: delete forms switched from `onsubmit="return confirm(...)"` to `data-confirm/...-title/...-text/...-danger` attrs.
- Flash → toast bridge: `templates/index.html`, `templates/admin/dashboard.html`, `templates/admin/detail.html` render server-side `get_flashed_messages` into `Notify.toast(...)` calls on `DOMContentLoaded` (mapping `success → success`, `danger/error → error`, `warning → warning`, else `info`). On the landing page the legacy `.flash-stack` is removed after toasts are queued, avoiding double notification.
- No more `alert()/confirm()/prompt()` anywhere in the codebase (verified by grep).
