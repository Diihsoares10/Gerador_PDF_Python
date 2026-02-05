from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from pdf_generator import gerar_pdf
from utils import validar_dados_formulario
import re
from datetime import datetime

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura'  # Necessário para flash messages

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
        
        # Validações
        erros = validar_dados_formulario(dados)

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('index.html') # Retorna com os dados preenchidos se possível
            
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
