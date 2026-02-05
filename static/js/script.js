document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('cadastroForm');

    // --- Máscaras de Entrada (usando IMask) ---
    const phoneMask = IMask(document.getElementById('telefone'), {
        mask: '(00) 00000-0000'
    });

    const cpfMask = IMask(document.getElementById('cpf'), {
        mask: '000.000.000-00'
    });

    const cepMask = IMask(document.getElementById('cep'), {
        mask: '00000-000'
    });

    // --- Contagem de Caracteres ---
    const obsInput = document.getElementById('observacao');
    const charCount = document.getElementById('charCount');
    
    if (obsInput) {
        obsInput.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });
    }

    // --- Validação de CPF ---
    function validarCPF(cpf) {
        cpf = cpf.replace(/[^\d]+/g, '');
        if (cpf == '') return false;
        if (cpf.length != 11 || cpf == cpf[0] * 11) return false;
        
        let add = 0;
        for (i = 0; i < 9; i++) add += parseInt(cpf.charAt(i)) * (10 - i);
        let rev = 11 - (add % 11);
        if (rev == 10 || rev == 11) rev = 0;
        if (rev != parseInt(cpf.charAt(9))) return false;
        
        add = 0;
        for (i = 0; i < 10; i++) add += parseInt(cpf.charAt(i)) * (11 - i);
        rev = 11 - (add % 11);
        if (rev == 10 || rev == 11) rev = 0;
        if (rev != parseInt(cpf.charAt(10))) return false;
        
        return true;
    }

    // --- Validação de Idade ---
    function isMaiorDeIdade(dateString) {
        if (!dateString) return false;
        const today = new Date();
        const birthDate = new Date(dateString);
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age >= 18;
    }

    // --- Validação Customizada do Bootstrap ---
    form.addEventListener('submit', function (event) {
        let isValid = true;

        // Validação CPF
        const cpfInput = document.getElementById('cpf');
        if (!validarCPF(cpfInput.value)) {
            cpfInput.setCustomValidity('CPF inválido');
            isValid = false;
        } else {
            cpfInput.setCustomValidity('');
        }

        // Validação Idade
        const dataNascInput = document.getElementById('data_nascimento');
        if (!isMaiorDeIdade(dataNascInput.value)) {
            dataNascInput.setCustomValidity('Menor de 18 anos');
            isValid = false;
        } else {
            dataNascInput.setCustomValidity('');
        }

        // Validação Confirmação de Email
        const email = document.getElementById('email');
        const emailConf = document.getElementById('email_confirmacao');
        if (email.value !== emailConf.value) {
            emailConf.setCustomValidity('Emails não conferem');
            isValid = false;
        } else {
            emailConf.setCustomValidity('');
        }

        if (!form.checkValidity() || !isValid) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            // Verifica se está rodando no Desktop (PyWebView)
            if (window.pywebview) {
                event.preventDefault(); // Impede o submit normal
                
                // Coleta dados
                const formData = new FormData(form);
                const data = {};
                formData.forEach((value, key) => data[key] = value);

                // Feedback visual de carregamento
                Swal.fire({
                    title: 'Processando...',
                    text: 'Aguarde enquanto geramos seu PDF.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                // Chama API Python
                window.pywebview.api.gerar_pdf_desktop(data).then(response => {
                    if (response.status === 'success') {
                        Swal.fire({
                            title: 'Sucesso!',
                            text: `PDF salvo com sucesso em:\n${response.path}`,
                            icon: 'success',
                            confirmButtonColor: '#0d6efd'
                        });
                    } else if (response.status === 'error') {
                         Swal.fire({
                            title: 'Erro!',
                            html: response.messages.join('<br>'),
                            icon: 'error',
                            confirmButtonColor: '#d33'
                        });
                    } else if (response.status === 'cancelled') {
                        Swal.close(); // Fecha o loading se cancelado
                    }
                }).catch(err => {
                    Swal.fire({
                        title: 'Erro Crítico',
                        text: 'Falha na comunicação com a aplicação desktop.',
                        icon: 'error'
                    });
                });
            } else {
                // Modo Web: Submit normal
                Swal.fire({
                    title: 'Gerando PDF!',
                    text: 'Seu download começará em instantes.',
                    icon: 'success',
                    timer: 4000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
            }
        }

        form.classList.add('was-validated');
    }, false);

    // Limpar validação customizada ao digitar
    ['cpf', 'data_nascimento', 'email_confirmacao'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', function() {
                this.setCustomValidity('');
            });
        }
    });

    // --- LocalStorage (Salvar Rascunho) ---
    const btnSalvar = document.getElementById('btnSalvarRascunho');
    
    if (btnSalvar) {
        btnSalvar.addEventListener('click', function() {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            localStorage.setItem('formRascunho', JSON.stringify(data));
            
            Swal.fire({
                title: 'Sucesso!',
                text: 'Rascunho salvo com sucesso!',
                icon: 'success',
                confirmButtonText: 'OK',
                confirmButtonColor: '#0d6efd'
            });
        });
    }

    // Carregar Rascunho
    const rascunho = localStorage.getItem('formRascunho');
    if (rascunho) {
        try {
            const data = JSON.parse(rascunho);
            Object.keys(data).forEach(key => {
                if (form.elements[key]) {
                    const input = form.elements[key];
                    input.value = data[key];
                    // Atualizar máscaras se necessário
                    if (key === 'cpf') cpfMask.value = data[key];
                    if (key === 'telefone') phoneMask.value = data[key];
                    if (key === 'cep') cepMask.value = data[key];
                    if (key === 'observacao' && charCount) charCount.textContent = data[key].length;
                }
            });
        } catch (e) {
            console.error('Erro ao carregar rascunho', e);
        }
    }

    // --- Botão Limpar ---
    const btnLimpar = document.getElementById('btnLimpar');
    if (btnLimpar) {
        btnLimpar.addEventListener('click', function() {
            Swal.fire({
                title: 'Tem certeza?',
                text: "Deseja limpar todo o formulário? Esta ação não pode ser desfeita.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#0d6efd',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sim, limpar!',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.reset();
                    form.classList.remove('was-validated');
                    localStorage.removeItem('formRascunho');
                    if (charCount) charCount.textContent = '0';
                    // Limpar máscaras
                    cpfMask.value = '';
                    phoneMask.value = '';
                    cepMask.value = '';
                    
                    Swal.fire(
                        'Limpo!',
                        'O formulário foi reiniciado.',
                        'success'
                    );
                }
            });
        });
    }

    // --- Modo Desktop: Histórico ---
    // Este evento é disparado quando o pywebview está pronto
    window.addEventListener('pywebviewready', function() {
        const btnHistorico = document.getElementById('btnHistorico');
        if (btnHistorico) {
            btnHistorico.style.display = 'inline-block';
            
            btnHistorico.addEventListener('click', function() {
                window.pywebview.api.obter_historico().then(historico => {
                    const tbody = document.getElementById('historicoTbody');
                    tbody.innerHTML = '';
                    
                    if (historico.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum registro encontrado.</td></tr>';
                    } else {
                        historico.forEach(reg => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td>${reg.data}</td>
                                <td>${reg.nome}</td>
                                <td>${reg.cpf}</td>
                                <td class="text-truncate" style="max-width: 200px;" title="${reg.arquivo}">${reg.arquivo}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                    
                    const modal = new bootstrap.Modal(document.getElementById('historicoModal'));
                    modal.show();
                });
            });
        }
    });

});
