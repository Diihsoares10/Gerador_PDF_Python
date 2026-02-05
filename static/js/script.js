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

    // RG pode variar muito, vamos permitir números e alguns caracteres comuns
    // Mas geralmente RG não tem padrão nacional fixo como CPF.
    // Vamos deixar livre ou usar uma máscara genérica se necessário.
    // Aqui optamos por não mascarar estritamente o RG para evitar bloqueios indevidos, 
    // pois cada estado tem um formato.

    // --- Contagem de Caracteres ---
    const obsInput = document.getElementById('observacao');
    const charCount = document.getElementById('charCount');
    
    obsInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });

    // --- Validação de CPF ---
    function validarCPF(cpf) {
        cpf = cpf.replace(/[^\d]+/g, '');
        if (cpf == '') return false;
        // Elimina CPFs invalidos conhecidos
        if (cpf.length != 11 ||
            cpf == "00000000000" ||
            cpf == "11111111111" ||
            cpf == "22222222222" ||
            cpf == "33333333333" ||
            cpf == "44444444444" ||
            cpf == "55555555555" ||
            cpf == "66666666666" ||
            cpf == "77777777777" ||
            cpf == "88888888888" ||
            cpf == "99999999999")
            return false;
        // Valida 1o digito
        add = 0;
        for (i = 0; i < 9; i++)
            add += parseInt(cpf.charAt(i)) * (10 - i);
        rev = 11 - (add % 11);
        if (rev == 10 || rev == 11)
            rev = 0;
        if (rev != parseInt(cpf.charAt(9)))
            return false;
        // Valida 2o digito
        add = 0;
        for (i = 0; i < 10; i++)
            add += parseInt(cpf.charAt(i)) * (11 - i);
        rev = 11 - (add % 11);
        if (rev == 10 || rev == 11)
            rev = 0;
        if (rev != parseInt(cpf.charAt(10)))
            return false;
        return true;
    }

    // --- Validação de Idade ---
    function isMaiorDeIdade(dateString) {
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
        }

        form.classList.add('was-validated');
    }, false);

    // Limpar validação customizada ao digitar
    ['cpf', 'data_nascimento', 'email_confirmacao'].forEach(id => {
        document.getElementById(id).addEventListener('input', function() {
            this.setCustomValidity('');
        });
    });

    // --- LocalStorage (Salvar Rascunho) ---
    const btnSalvar = document.getElementById('btnSalvarRascunho');
    
    btnSalvar.addEventListener('click', function() {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        localStorage.setItem('formRascunho', JSON.stringify(data));
        alert('Rascunho salvo com sucesso!');
    });

    // Carregar Rascunho
    const rascunho = localStorage.getItem('formRascunho');
    if (rascunho) {
        try {
            const data = JSON.parse(rascunho);
            Object.keys(data).forEach(key => {
                const input = form.elements[key];
                if (input) {
                    input.value = data[key];
                    // Atualizar máscaras se necessário
                    if (key === 'cpf') cpfMask.value = data[key];
                    if (key === 'telefone') phoneMask.value = data[key];
                    if (key === 'cep') cepMask.value = data[key];
                    if (key === 'observacao') charCount.textContent = data[key].length;
                }
            });
        } catch (e) {
            console.error('Erro ao carregar rascunho', e);
        }
    }

    // --- Botão Limpar ---
    document.getElementById('btnLimpar').addEventListener('click', function() {
        if(confirm('Tem certeza que deseja limpar todo o formulário?')) {
            form.reset();
            form.classList.remove('was-validated');
            localStorage.removeItem('formRascunho');
            charCount.textContent = '0';
            // Limpar máscaras
            cpfMask.value = '';
            phoneMask.value = '';
            cepMask.value = '';
        }
    });
});
