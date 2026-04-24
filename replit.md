# Sistema de Cadastro e Geração de PDF

## Overview
Flask-based web application for user registration with automatic PDF report generation. Built with Python, Flask, ReportLab, and Bootstrap 5. Server-side validates CPF, age (18+), email confirmation, and generates a downloadable PDF.

## Project Structure
- `app.py`: Flask application (routes + server-side validation)
- `pdf_generator.py`: ReportLab PDF generation logic
- `templates/index.html`: Main form UI (Bootstrap 5 + Font Awesome via CDN)
- `static/js/script.js`: Client-side validation and input masks
- `requirements.txt`: Python dependencies (Flask, ReportLab)

## Replit Setup
- Language: Python 3.12
- Workflow: `Server` runs `python app.py` on port 5000 (host `0.0.0.0`)
- Deployment: configured as autoscale using Gunicorn

## Recent Changes
- 2026-04-24: Imported from GitHub. Bound Flask to `0.0.0.0:5000` and configured deployment.
- 2026-04-24: UI redesign — modern glassmorphism layout, light/dark mode, icons inside fields, real-time validation with inline help, progress indicator, ViaCEP autofill, autosaving draft, Inter typography, animated background blobs, accessibility (aria-live, prefers-reduced-motion, keyboard shortcut Ctrl/Cmd+Enter to submit).
