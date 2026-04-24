/* ============================================================
   Modern Form — Validation, UX helpers, theme, draft autosave
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('cadastroForm');

    /* ---------- Theme toggle ---------- */
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        themeIcon.className = t === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        try { localStorage.setItem('theme', t); } catch (e) {}
    }
    applyTheme(document.documentElement.getAttribute('data-theme') || 'light');
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });

    /* ---------- Input masks ---------- */
    const phoneMask = IMask(document.getElementById('telefone'), { mask: '(00) 00000-0000' });
    const cpfMask   = IMask(document.getElementById('cpf'),      { mask: '000.000.000-00' });
    const cepMask   = IMask(document.getElementById('cep'),      { mask: '00000-000' });

    /* ---------- Helpers: field state ---------- */
    function fieldOf(input) { return input.closest('.field'); }

    function setHelp(input, msg) {
        const f = fieldOf(input);
        if (!f) return;
        const help = f.querySelector('.field-help');
        if (!help) return;
        if (msg) {
            help.textContent = msg;
        } else {
            help.textContent = help.dataset.default || '';
        }
    }

    function setValid(input) {
        const f = fieldOf(input); if (!f) return;
        f.classList.add('is-valid');
        f.classList.remove('is-invalid');
        input.setCustomValidity('');
        setHelp(input, null);
    }
    function setInvalid(input, msg) {
        const f = fieldOf(input); if (!f) return;
        f.classList.add('is-invalid');
        f.classList.remove('is-valid');
        input.setCustomValidity(msg || 'Inválido');
        setHelp(input, msg);
    }
    function clearState(input) {
        const f = fieldOf(input); if (!f) return;
        f.classList.remove('is-valid', 'is-invalid');
        input.setCustomValidity('');
        setHelp(input, null);
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

    /* ---------- Per-field live validation ---------- */
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
        genero: (el) => {
            if (!el.value) return { ok: false, msg: 'Selecione uma opção.' };
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
        if (!el) return true;
        const v = validators[name](el);
        if (v.ok) setValid(el); else setInvalid(el, v.msg);
        return v.ok;
    }

    Object.keys(validators).forEach(name => {
        const el = document.getElementById(name);
        if (!el) return;
        // Validate on blur (first interaction)
        el.addEventListener('blur', () => {
            if (el.value || el.required) runValidator(name);
        });
        // Live re-validate while typing — but only after a first invalid attempt
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

    // Re-validate confirmation if main email changes
    document.getElementById('email').addEventListener('input', () => {
        const conf = document.getElementById('email_confirmacao');
        if (conf.value) runValidator('email_confirmacao');
    });

    /* ---------- Character counter (textarea) ---------- */
    const obs = document.getElementById('observacao');
    const charCount = document.getElementById('charCount');
    const charCounter = document.getElementById('charCounter');
    obs.addEventListener('input', () => {
        const n = obs.value.length;
        charCount.textContent = n;
        charCounter.classList.toggle('warn', n > 400 && n <= 480);
        charCounter.classList.toggle('danger', n > 480);
    });

    /* ---------- Progress indicator ---------- */
    const progressFill = document.getElementById('progressFill');
    const progressPct = document.getElementById('progressPct');
    const progressBar = document.getElementById('progressBar');

    const requiredIds = ['nome','cpf','rg','data_nascimento','genero','email','email_confirmacao','observacao'];
    function updateProgress() {
        let filled = 0;
        requiredIds.forEach(id => {
            const el = document.getElementById(id);
            if (el && el.value && el.value.trim() !== '') filled++;
        });
        const pct = Math.round((filled / requiredIds.length) * 100);
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
            if (data.erro) {
                setInvalid(cepInput, 'CEP não encontrado.');
                return;
            }
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
            // Move focus to "número" for speed
            const numero = document.getElementById('numero');
            if (numero && !numero.value) numero.focus();
        } catch (err) {
            setHelp(cepInput, 'Não foi possível buscar o CEP agora.');
        }
    });

    /* ---------- Submit ---------- */
    const btnEnviar = document.getElementById('btnEnviar');
    form.addEventListener('submit', function (event) {
        let allOk = true;
        let firstInvalid = null;
        Object.keys(validators).forEach(name => {
            const ok = runValidator(name);
            if (!ok && !firstInvalid) firstInvalid = document.getElementById(name);
            if (!ok) allOk = false;
        });
        if (!allOk) {
            event.preventDefault();
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(() => firstInvalid.focus({ preventScroll: true }), 350);
            }
            return;
        }
        // UX feedback
        btnEnviar.classList.add('loading');
        btnEnviar.disabled = true;
        // Re-enable after 8s in case of slow PDF or browser back
        setTimeout(() => {
            btnEnviar.classList.remove('loading');
            btnEnviar.disabled = false;
        }, 8000);
    });

    /* ---------- Draft autosave (localStorage) ---------- */
    const draftStatus = document.getElementById('draftStatus');
    const draftText = draftStatus.querySelector('.draft-text');
    const btnSalvar = document.getElementById('btnSalvarRascunho');
    let saveTimer = null;

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

    function saveDraft(silent) {
        try {
            localStorage.setItem('formRascunho', JSON.stringify(collectFormData()));
            localStorage.setItem('formRascunhoTs', String(Date.now()));
            if (!silent) setDraftState('saved', 'Rascunho salvo agora');
            else setDraftState('saved', 'Salvo automaticamente');
        } catch (e) {
            setDraftState(null, 'Não foi possível salvar o rascunho.');
        }
    }

    function scheduleAutosave() {
        setDraftState('saving', 'Salvando...');
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => saveDraft(true), 800);
    }

    btnSalvar.addEventListener('click', () => saveDraft(false));

    // Load draft on page open
    try {
        const raw = localStorage.getItem('formRascunho');
        if (raw) {
            const data = JSON.parse(raw);
            Object.keys(data).forEach(key => {
                const input = form.elements[key];
                if (input) {
                    input.value = data[key];
                    if (key === 'cpf') cpfMask.value = data[key];
                    if (key === 'telefone') phoneMask.value = data[key];
                    if (key === 'cep') cepMask.value = data[key];
                }
            });
            charCount.textContent = (data.observacao || '').length;
            const ts = parseInt(localStorage.getItem('formRascunhoTs') || '0', 10);
            if (ts) {
                const mins = Math.round((Date.now() - ts) / 60000);
                setDraftState('saved', mins < 1 ? 'Rascunho restaurado' : `Rascunho restaurado (há ${mins} min)`);
            } else {
                setDraftState('saved', 'Rascunho restaurado');
            }
        } else {
            setDraftState(null, 'Rascunho automático ativo');
        }
    } catch (e) {
        console.error('Erro ao carregar rascunho', e);
    }

    updateProgress();

    /* ---------- Limpar ---------- */
    document.getElementById('btnLimpar').addEventListener('click', function () {
        if (!confirm('Tem certeza que deseja limpar todo o formulário?')) return;
        form.reset();
        cpfMask.value = '';
        phoneMask.value = '';
        cepMask.value = '';
        charCount.textContent = '0';
        charCounter.classList.remove('warn', 'danger');
        document.querySelectorAll('.field').forEach(f => f.classList.remove('is-valid', 'is-invalid'));
        document.querySelectorAll('.field-help').forEach(h => h.textContent = h.dataset.default || '');
        try { localStorage.removeItem('formRascunho'); localStorage.removeItem('formRascunhoTs'); } catch (e) {}
        setDraftState(null, 'Rascunho limpo');
        updateProgress();
    });

    /* ---------- Keyboard shortcut: Ctrl/Cmd + Enter to submit ---------- */
    form.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            btnEnviar.click();
        }
    });
});
