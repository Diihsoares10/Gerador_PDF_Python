/* ============================================================
   Notify — modern toast + confirm dialog system
   Replaces native alert(), confirm(), prompt().

   Public API:
     Notify.toast({ type, title, message, duration })
     Notify.success(message[, title])
     Notify.error(message[, title])
     Notify.info(message[, title])
     Notify.warning(message[, title])
     Notify.confirm({ title, message, confirmText, cancelText, danger })
        → returns a Promise<boolean>

   Also: any <form data-confirm="..."> automatically opens
   a styled confirm dialog instead of a native one.
   ============================================================ */
(function () {
    if (window.Notify) return;

    const ICONS = {
        success: 'fa-circle-check',
        error:   'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info:    'fa-circle-info',
    };

    /* ---------- Container ---------- */
    function getContainer() {
        let c = document.getElementById('toastContainer');
        if (!c) {
            c = document.createElement('div');
            c.id = 'toastContainer';
            c.className = 'toast-container';
            c.setAttribute('aria-live', 'polite');
            c.setAttribute('aria-atomic', 'false');
            document.body.appendChild(c);
        }
        return c;
    }

    /* ---------- Toast ---------- */
    function toast({ type = 'info', title = '', message = '', duration = 4500 } = {}) {
        const container = getContainer();
        const t = document.createElement('div');
        t.className = `toast toast-${type}`;
        t.setAttribute('role', type === 'error' ? 'alert' : 'status');
        const iconClass = ICONS[type] || ICONS.info;
        t.innerHTML = `
            <span class="toast-icon"><i class="fa-solid ${iconClass}"></i></span>
            <div class="toast-body">
                ${title ? `<strong class="toast-title"></strong>` : ''}
                <span class="toast-msg"></span>
            </div>
            <button type="button" class="toast-close" aria-label="Fechar">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <span class="toast-progress"></span>
        `;
        if (title) t.querySelector('.toast-title').textContent = title;
        t.querySelector('.toast-msg').textContent = message;

        const progress = t.querySelector('.toast-progress');
        if (duration > 0) progress.style.animationDuration = duration + 'ms';
        else progress.style.display = 'none';

        let timer = null;
        function dismiss() {
            if (t.dataset.dismissed) return;
            t.dataset.dismissed = '1';
            clearTimeout(timer);
            t.classList.add('is-leaving');
            setTimeout(() => t.remove(), 280);
        }
        t.querySelector('.toast-close').addEventListener('click', dismiss);
        t.addEventListener('mouseenter', () => { clearTimeout(timer); progress.style.animationPlayState = 'paused'; });
        t.addEventListener('mouseleave', () => {
            if (duration > 0) { timer = setTimeout(dismiss, 1200); progress.style.animationPlayState = 'running'; }
        });

        container.appendChild(t);
        requestAnimationFrame(() => t.classList.add('is-in'));
        if (duration > 0) timer = setTimeout(dismiss, duration);

        return { dismiss };
    }

    /* ---------- Confirm dialog ---------- */
    function confirmDialog({
        title = 'Tem certeza?',
        message = '',
        confirmText = 'Confirmar',
        cancelText = 'Cancelar',
        danger = false,
        icon = null,
    } = {}) {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'confirm-overlay';
            overlay.setAttribute('role', 'dialog');
            overlay.setAttribute('aria-modal', 'true');

            const iconClass = icon || (danger ? 'fa-triangle-exclamation' : 'fa-circle-question');
            overlay.innerHTML = `
                <div class="confirm-backdrop"></div>
                <div class="confirm-card ${danger ? 'is-danger' : ''}">
                    <div class="confirm-icon"><i class="fa-solid ${iconClass}"></i></div>
                    <h2 class="confirm-title"></h2>
                    <p class="confirm-msg"></p>
                    <div class="confirm-actions">
                        <button type="button" class="btn btn-ghost confirm-cancel"></button>
                        <button type="button" class="btn ${danger ? 'btn-danger' : 'btn-primary'} confirm-ok"></button>
                    </div>
                </div>
            `;
            overlay.querySelector('.confirm-title').textContent = title;
            overlay.querySelector('.confirm-msg').textContent = message;
            overlay.querySelector('.confirm-cancel').textContent = cancelText;
            overlay.querySelector('.confirm-ok').textContent = confirmText;

            const previouslyFocused = document.activeElement;
            document.body.appendChild(overlay);
            requestAnimationFrame(() => overlay.classList.add('is-in'));

            const okBtn = overlay.querySelector('.confirm-ok');
            const cancelBtn = overlay.querySelector('.confirm-cancel');
            const backdrop = overlay.querySelector('.confirm-backdrop');

            function close(result) {
                overlay.classList.add('is-leaving');
                document.removeEventListener('keydown', onKey);
                setTimeout(() => {
                    overlay.remove();
                    if (previouslyFocused && previouslyFocused.focus) previouslyFocused.focus();
                    resolve(result);
                }, 220);
            }
            function onKey(e) {
                if (e.key === 'Escape') close(false);
                else if (e.key === 'Enter') close(true);
            }
            okBtn.addEventListener('click', () => close(true));
            cancelBtn.addEventListener('click', () => close(false));
            backdrop.addEventListener('click', () => close(false));
            document.addEventListener('keydown', onKey);
            setTimeout(() => okBtn.focus(), 80);
        });
    }

    /* ---------- Form interception (data-confirm) ---------- */
    document.addEventListener('submit', async function (e) {
        const form = e.target.closest('form[data-confirm]');
        if (!form || form.dataset.confirmDone === '1') return;
        e.preventDefault();
        const ok = await confirmDialog({
            title: form.dataset.confirmTitle || 'Tem certeza?',
            message: form.dataset.confirm,
            confirmText: form.dataset.confirmText || 'Confirmar',
            cancelText: form.dataset.cancelText || 'Cancelar',
            danger: form.dataset.confirmDanger === '1',
        });
        if (ok) {
            form.dataset.confirmDone = '1';
            form.submit();
        }
    }, true);

    /* ---------- Public API ---------- */
    window.Notify = {
        toast,
        success: (msg, title = 'Tudo certo!') => toast({ type: 'success', title, message: msg }),
        error:   (msg, title = 'Algo deu errado') => toast({ type: 'error',   title, message: msg, duration: 6000 }),
        warning: (msg, title = 'Atenção')        => toast({ type: 'warning', title, message: msg }),
        info:    (msg, title = '')               => toast({ type: 'info',    title, message: msg }),
        confirm: confirmDialog,
    };
})();
