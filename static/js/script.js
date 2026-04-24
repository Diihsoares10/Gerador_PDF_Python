/* ============================================================
   Modern Form — landing, multi-step, validation, autosave, theme
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('cadastroForm');
    const body = document.body;

    /* ---------- Theme toggle ---------- */
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        if (themeIcon) themeIcon.className = t === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        try { localStorage.setItem('theme', t); } catch (e) {}
    }
    applyTheme(document.documentElement.getAttribute('data-theme') || 'light');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    /* ---------- Landing → Form transition ---------- */
    const landing = document.getElementById('landing');
    const formCard = document.getElementById('formCard');
    const btnStart = document.getElementById('btnStart');

    function showForm() {
        if (landing) landing.hidden = true;
        if (formCard) {
            formCard.hidden = false;
            formCard.classList.add('reveal');
            setTimeout(() => formCard.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
            const firstInput = formCard.querySelector('.step-panel.is-active input, .step-panel.is-active select, .step-panel.is-active textarea');
            if (firstInput) setTimeout(() => firstInput.focus(), 350);
        }
    }
    if (btnStart) btnStart.addEventListener('click', showForm);

    if (!form) return;

    /* ---------- Input masks ---------- */
    IMask(document.getElementById('telefone'), { mask: '(00) 00000-0000' });
    IMask(document.getElementById('cpf'),      { mask: '000.000.000-00' });
    IMask(document.getElementById('cep'),      { mask: '00000-000' });

    /* ---------- Field state helpers ---------- */
    function fieldOf(input) { return input.closest('.field'); }
    function setHelp(input, msg) {
        const f = fieldOf(input); if (!f) return;
        const help = f.querySelector('.field-help'); if (!help) return;
        help.textContent = msg || help.dataset.default || '';
    }
    function setValid(input) {
        const f = fieldOf(input); if (!f) return;
        f.classList.add('is-valid');
        f.classList.remove('is-invalid');
        if (input.setCustomValidity) input.setCustomValidity('');
        setHelp(input, null);
    }
    function setInvalid(input, msg) {
        const f = fieldOf(input); if (!f) return;
        f.classList.add('is-invalid');
        f.classList.remove('is-valid');
        if (input.setCustomValidity) input.setCustomValidity(msg || 'Inválido');
        setHelp(input, msg);
    }

    /* ---------- Validators ---------- */
    function validarCPF(cpf) {
        cpf = (cpf || '').replace(/[^\d]+/g, '');
        if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;
        let add = 0;
        for (let i = 0; i < 9; i++) add += parseInt(cpf.charAt(i)) * (10 - i);
        let rev = 11 - (add % 11); if (rev >= 10) rev = 0;
        if (rev !== parseInt(cpf.charAt(9))) return false;
        add = 0;
        for (let i = 0; i < 10; i++) add += parseInt(cpf.charAt(i)) * (11 - i);
        rev = 11 - (add % 11); if (rev >= 10) rev = 0;
        return rev === parseInt(cpf.charAt(10));
    }
    function isMaiorDeIdade(dateString) {
        if (!dateString) return false;
        const today = new Date();
        const birthDate = new Date(dateString);
        if (isNaN(birthDate.getTime())) return false;
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) age--;
        return age >= 18 && age <= 120;
    }
    function isValidEmail(v) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test((v || '').trim());
    }

    const validators = {
        nome: (el) => {
            const v = el.value.trim();
            if (!v) return { ok: false, msg: 'Por favor, informe seu nome.' };
            if (v.length < 3) return { ok: false, msg: 'Use ao menos 3 caracteres.' };
            if (!/\s/.test(v)) return { ok: false, msg: 'Inclua nome e sobrenome.' };
            return { ok: true };
        },
        cpf: (el) => {
            if (!el.value) return { ok: false, msg: 'Informe o CPF.' };
            if (!validarCPF(el.value)) return { ok: false, msg: 'CPF inválido — verifique os dígitos.' };
            return { ok: true };
        },
        rg: (el) => {
            const v = el.value.trim();
            if (!v) return { ok: false, msg: 'Informe seu RG.' };
            if (v.replace(/[^0-9a-zA-Z]/g, '').length < 5) return { ok: false, msg: 'RG parece curto demais.' };
            return { ok: true };
        },
        data_nascimento: (el) => {
            if (!el.value) return { ok: false, msg: 'Selecione sua data de nascimento.' };
            if (!isMaiorDeIdade(el.value)) return { ok: false, msg: 'Você precisa ter 18 anos ou mais.' };
            return { ok: true };
        },
        email: (el) => {
            if (!el.value) return { ok: false, msg: 'Informe seu email.' };
            if (!isValidEmail(el.value)) return { ok: false, msg: 'Email inválido. Ex: nome@dominio.com' };
            return { ok: true };
        },
        email_confirmacao: (el) => {
            const email = document.getElementById('email').value;
            if (!el.value) return { ok: false, msg: 'Confirme seu email.' };
            if (el.value !== email) return { ok: false, msg: 'Os emails não coincidem.' };
            return { ok: true };
        },
        observacao: (el) => {
            const v = el.value.trim();
            if (!v) return { ok: false, msg: 'Adicione uma observação.' };
            if (v.length > 500) return { ok: false, msg: 'Máximo 500 caracteres.' };
            return { ok: true };
        }
    };

    function runValidator(name) {
        const el = document.getElementById(name);
        if (!el || !validators[name]) return true;
        const v = validators[name](el);
        if (v.ok) setValid(el); else setInvalid(el, v.msg);
        return v.ok;
    }

    /* ---------- Special validation for radio groups ---------- */
    function validateGenero() {
        const group = document.querySelector('[data-validates="genero"]');
        if (!group) return true;
        const checked = group.querySelector('input[type="radio"]:checked');
        if (checked) {
            group.classList.remove('is-invalid');
            group.classList.add('is-valid');
            const help = group.parentElement.querySelector('.field-help');
            if (help) help.textContent = help.dataset.default || '';
            return true;
        }
        group.classList.add('is-invalid');
        group.classList.remove('is-valid');
        const help = group.parentElement.querySelector('.field-help');
        if (help) help.textContent = 'Selecione uma opção.';
        return false;
    }

    Object.keys(validators).forEach(name => {
        const el = document.getElementById(name);
        if (!el) return;
        el.addEventListener('blur', () => { if (el.value || el.required) runValidator(name); });
        el.addEventListener('input', () => {
            const f = fieldOf(el);
            if (f && (f.classList.contains('is-valid') || f.classList.contains('is-invalid'))) {
                runValidator(name);
            }
            updateProgress();
            scheduleAutosave();
        });
        el.addEventListener('change', () => {
            if (el.value) runValidator(name);
            updateProgress();
            scheduleAutosave();
        });
    });

    document.getElementById('email').addEventListener('input', () => {
        const conf = document.getElementById('email_confirmacao');
        if (conf.value) runValidator('email_confirmacao');
    });

    // Radios + optional fields
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', () => {
            if (radio.name === 'genero') validateGenero();
            updateProgress();
            scheduleAutosave();
        });
    });

    ['nome_mae','profissao','telefone','cep','logradouro',
     'numero','complemento','bairro','cidade','estado'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', scheduleAutosave);
        el.addEventListener('change', scheduleAutosave);
    });

    /* ---------- Character counter ---------- */
    const obs = document.getElementById('observacao');
    const charCount = document.getElementById('charCount');
    const charCounter = document.getElementById('charCounter');
    obs.addEventListener('input', () => {
        const n = obs.value.length;
        charCount.textContent = n;
        charCounter.classList.toggle('warn', n > 400 && n <= 480);
        charCounter.classList.toggle('danger', n > 480);
    });

    /* ---------- Progress (overall) ---------- */
    const progressFill = document.getElementById('progressFill');
    const progressPct = document.getElementById('progressPct');
    const progressBar = document.getElementById('progressBar');
    function updateProgress() {
        const required = ['nome','cpf','rg','data_nascimento','email','email_confirmacao','observacao'];
        let filled = 0;
        required.forEach(id => {
            const el = document.getElementById(id);
            if (el && el.value && el.value.trim() !== '') filled++;
        });
        if (document.querySelector('input[name="genero"]:checked')) filled++;
        const total = required.length + 1;
        const pct = Math.round((filled / total) * 100);
        progressFill.style.width = pct + '%';
        progressPct.textContent = pct + '%';
        progressBar.setAttribute('aria-valuenow', pct);
    }

    /* ---------- CEP autofill (ViaCEP) ---------- */
    const cepInput = document.getElementById('cep');
    cepInput.addEventListener('blur', async () => {
        const cep = cepInput.value.replace(/\D/g, '');
        if (cep.length !== 8) return;
        try {
            setHelp(cepInput, 'Buscando endereço...');
            const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await res.json();
            if (data.erro) { setInvalid(cepInput, 'CEP não encontrado.'); return; }
            const fill = (id, v) => {
                const el = document.getElementById(id);
                if (el && !el.value) { el.value = v || ''; el.dispatchEvent(new Event('input')); }
            };
            fill('logradouro', data.logradouro);
            fill('bairro', data.bairro);
            fill('cidade', data.localidade);
            fill('estado', (data.uf || '').toUpperCase());
            setValid(cepInput);
            setHelp(cepInput, 'Endereço preenchido automaticamente.');
            const numero = document.getElementById('numero');
            if (numero && !numero.value) numero.focus();
            scheduleAutosave();
        } catch (err) {
            setHelp(cepInput, 'Não foi possível buscar o CEP agora.');
        }
    });

    /* ---------- Server-side autosave ---------- */
    const draftStatus = document.getElementById('draftStatus');
    const draftText = draftStatus.querySelector('.draft-text');
    let saveTimer = null;
    let inflight = null;

    function collectFormData() {
        const fd = new FormData(form);
        const obj = {};
        fd.forEach((v, k) => { obj[k] = v; });
        return obj;
    }
    function setDraftState(state, text) {
        draftStatus.classList.remove('saved', 'saving');
        if (state) draftStatus.classList.add(state);
        draftText.textContent = text;
    }
    async function saveDraft() {
        if (inflight) return;
        setDraftState('saving', 'Salvando...');
        try {
            inflight = fetch('/api/draft', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: collectFormData() }),
                credentials: 'same-origin',
            });
            const res = await inflight;
            const json = await res.json();
            if (!res.ok || !json.ok) throw new Error('save failed');
            const t = new Date(json.saved_at);
            const hh = String(t.getHours()).padStart(2, '0');
            const mm = String(t.getMinutes()).padStart(2, '0');
            setDraftState('saved', `Salvo às ${hh}:${mm}`);
        } catch (e) {
            setDraftState(null, 'Não foi possível salvar agora.');
        } finally {
            inflight = null;
        }
    }
    function scheduleAutosave() {
        setDraftState('saving', 'Salvando...');
        clearTimeout(saveTimer);
        saveTimer = setTimeout(saveDraft, 1000);
    }

    /* ---------- Multi-step navigation ---------- */
    const STEP_TOTAL = 4;
    let currentStep = 1;
    const stepperItems = document.querySelectorAll('#stepper .step');
    const panels = document.querySelectorAll('.step-panel');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnEnviar = document.getElementById('btnEnviar');
    const stepCurrent = document.getElementById('stepCurrent');

    // required fields per step (only those that block "Próximo")
    const stepRequired = {
        1: ['nome', 'cpf', 'rg', 'data_nascimento'],   // genero validated separately
        2: ['email', 'email_confirmacao'],
        3: [],
        4: ['observacao'],
    };

    function showStep(step) {
        currentStep = Math.max(1, Math.min(STEP_TOTAL, step));
        panels.forEach(p => p.classList.toggle('is-active', Number(p.dataset.panel) === currentStep));
        stepperItems.forEach(s => {
            const n = Number(s.dataset.step);
            s.classList.toggle('is-active', n === currentStep);
            s.classList.toggle('is-done', n < currentStep);
        });
        stepCurrent.textContent = currentStep;
        btnPrev.hidden = currentStep === 1;
        btnNext.hidden = currentStep === STEP_TOTAL;
        btnEnviar.hidden = currentStep !== STEP_TOTAL;

        if (currentStep === STEP_TOTAL) renderReview();

        const top = formCard.getBoundingClientRect().top + window.scrollY - 16;
        window.scrollTo({ top, behavior: 'smooth' });

        const firstInput = panels[currentStep - 1].querySelector('input:not([type="hidden"]):not([type="radio"]), select, textarea');
        if (firstInput) setTimeout(() => firstInput.focus({ preventScroll: true }), 350);
    }

    function validateStep(step) {
        let allOk = true;
        let firstInvalid = null;
        const requiredIds = stepRequired[step] || [];
        requiredIds.forEach(id => {
            const ok = runValidator(id);
            if (!ok && !firstInvalid) firstInvalid = document.getElementById(id);
            if (!ok) allOk = false;
        });
        if (step === 1) {
            const ok = validateGenero();
            if (!ok && !firstInvalid) firstInvalid = document.querySelector('[data-validates="genero"]');
            if (!ok) allOk = false;
        }
        if (firstInvalid) {
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            if (firstInvalid.focus) setTimeout(() => firstInvalid.focus({ preventScroll: true }), 250);
        }
        return allOk;
    }

    btnNext.addEventListener('click', () => {
        if (validateStep(currentStep)) showStep(currentStep + 1);
    });
    btnPrev.addEventListener('click', () => showStep(currentStep - 1));

    // Allow clicking a step in the stepper (only to go back to a previously-completed one)
    stepperItems.forEach(item => {
        item.addEventListener('click', () => {
            const target = Number(item.dataset.step);
            if (target < currentStep) showStep(target);
        });
    });

    /* ---------- Review (step 4) ---------- */
    function renderReview() {
        const grid = document.getElementById('reviewGrid');
        const fields = [
            ['Nome', 'nome'],
            ['CPF', 'cpf'],
            ['RG', 'rg'],
            ['Nascimento', 'data_nascimento'],
            ['Email', 'email'],
            ['Telefone', 'telefone'],
            ['Cidade', 'cidade'],
            ['UF', 'estado'],
        ];
        let html = '';
        fields.forEach(([label, id]) => {
            const el = document.getElementById(id);
            const v = (el && el.value) ? el.value : '—';
            html += `<div class="review-row"><dt>${label}</dt><dd>${escapeHtml(v)}</dd></div>`;
        });
        const genero = document.querySelector('input[name="genero"]:checked');
        html = `<div class="review-row"><dt>Gênero</dt><dd>${escapeHtml(genero ? genero.value : '—')}</dd></div>` + html;
        grid.innerHTML = html;
    }
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    }

    /* ---------- Submit ---------- */
    form.addEventListener('submit', function (event) {
        let allOk = true;
        for (let step = 1; step <= STEP_TOTAL; step++) {
            if (!validateStep(step)) { allOk = false; showStep(step); break; }
        }
        if (!allOk) { event.preventDefault(); return; }
        btnEnviar.classList.add('loading');
        btnEnviar.disabled = true;
        setTimeout(() => {
            btnEnviar.classList.remove('loading');
            btnEnviar.disabled = false;
        }, 8000);
    });

    /* ---------- Limpar ---------- */
    document.getElementById('btnLimpar').addEventListener('click', async function () {
        if (!confirm('Tem certeza que deseja limpar todo o formulário? Isso também apaga o rascunho salvo.')) return;
        try {
            await fetch('/api/draft/clear', { method: 'POST', credentials: 'same-origin' });
        } catch (e) {}
        window.location.reload();
    });

    /* ---------- Share modal ---------- */
    const shareModal = document.getElementById('shareModal');
    const btnShare = document.getElementById('btnShare');
    const btnCopy = document.getElementById('btnCopy');
    const shareUrl = document.getElementById('shareUrl');
    function openModal() { shareModal.classList.add('open'); shareModal.setAttribute('aria-hidden', 'false'); }
    function closeModal() { shareModal.classList.remove('open'); shareModal.setAttribute('aria-hidden', 'true'); }
    if (btnShare) btnShare.addEventListener('click', openModal);
    shareModal.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', closeModal));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
    if (btnCopy) {
        btnCopy.addEventListener('click', async () => {
            try { await navigator.clipboard.writeText(shareUrl.value); }
            catch (e) { shareUrl.select(); document.execCommand('copy'); }
            const span = btnCopy.querySelector('span');
            const orig = span.textContent;
            span.textContent = 'Copiado!';
            btnCopy.querySelector('i').className = 'fa-solid fa-check';
            setTimeout(() => {
                span.textContent = orig;
                btnCopy.querySelector('i').className = 'fa-solid fa-copy';
            }, 2000);
        });
    }

    /* ---------- Init ---------- */
    updateProgress();
    setDraftState(null, 'Rascunho automático ativo');

    // If user has a saved draft, jump straight to the form (landing was already hidden server-side)
    if (body.dataset.hasDraft === 'true') {
        // Keep step 1 active by default, but if first step is fully valid, advance
        // (subtle nicety: skip ahead until first incomplete step)
        for (let s = 1; s < STEP_TOTAL; s++) {
            const ids = stepRequired[s] || [];
            const allFilled = ids.every(id => {
                const el = document.getElementById(id);
                return el && el.value && el.value.trim() !== '';
            });
            const generoOk = s === 1 ? !!document.querySelector('input[name="genero"]:checked') : true;
            if (allFilled && generoOk) currentStep = s + 1;
            else break;
        }
        showStep(currentStep);
    }
});
