from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from pdf_generator import gerar_pdf
import re
from datetime import datetime

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura'  # Necessário para flash messages

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
        data_nasc = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
        hoje = datetime.now()
        idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
        return idade >= 18
    except ValueError:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Rota principal da aplicação.
    """
    if request.method == 'POST':
        # Coleta de dados
        dados = {
            'nome': request.form.get('nome'),
            'cpf': request.form.get('cpf'),
            'rg': request.form.get('rg'),
            'data_nascimento': request.form.get('data_nascimento'),
            'genero': request.form.get('genero'),
            'estado_civil': request.form.get('estado_civil'),
            'nome_mae': request.form.get('nome_mae'),
            'profissao': request.form.get('profissao'),
            'email': request.form.get('email'),
            'email_confirmacao': request.form.get('email_confirmacao'),
            'telefone': request.form.get('telefone'),
            'cep': request.form.get('cep'),
            'logradouro': request.form.get('logradouro'),
            'numero': request.form.get('numero'),
            'complemento': request.form.get('complemento'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'estado': request.form.get('estado'),
            'observacao': request.form.get('observacao')
        }
        
        # Validações Server-Side
        erros = []
        
        if not dados['nome'] or len(dados['nome']) < 3:
            erros.append("Nome deve ter no mínimo 3 caracteres.")
            
        if not validar_cpf(dados['cpf']):
            erros.append("CPF inválido.")
            
        if not validar_idade(dados['data_nascimento']):
            erros.append("É necessário ser maior de 18 anos.")
            
        if dados['email'] != dados['email_confirmacao']:
            erros.append("Os emails não coincidem.")
            
        if len(dados['observacao']) > 500:
            erros.append("Observação excede o limite de 500 caracteres.")

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('index.html') # Retorna com os dados preenchidos se possível (navegador geralmente mantém)
            
        try:
            # Geração do PDF
            pdf_buffer = gerar_pdf(dados)
            
            # Formata nome do arquivo seguro
            safe_filename = re.sub(r'[^a-zA-Z0-9]', '_', dados['nome'])
            
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f"cadastro_{safe_filename}.pdf",
                mimetype='application/pdf'
            )
            
        except Exception as e:
            flash(f"Erro ao gerar PDF: {str(e)}", 'danger')
            return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
