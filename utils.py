import re
from datetime import datetime

def validar_cpf(cpf):
    """Valida um número de CPF."""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        return False
        
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
        
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False
        
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        return False
        
    return True

def validar_idade(data_nascimento_str):
    """Verifica se é maior de 18 anos."""
    try:
        if not data_nascimento_str:
            return False
        data_nasc = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
        hoje = datetime.now()
        idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
        return idade >= 18
    except ValueError:
        return False

def validar_dados_formulario(dados):
    """
    Realiza todas as validações de negócio nos dados do formulário.
    Retorna uma lista de erros (vazia se estiver tudo ok).
    """
    erros = []
    
    if not dados.get('nome') or len(dados.get('nome')) < 3:
        erros.append("Nome deve ter no mínimo 3 caracteres.")
        
    if not validar_cpf(dados.get('cpf', '')):
        erros.append("CPF inválido.")
        
    if not validar_idade(dados.get('data_nascimento')):
        erros.append("É necessário ser maior de 18 anos.")
        
    if dados.get('email') != dados.get('email_confirmacao'):
        erros.append("Os emails não coincidem.")
        
    if len(dados.get('observacao', '')) > 500:
        erros.append("Observação excede o limite de 500 caracteres.")
        
    return erros
