import webview
import threading
import sys
import os
import json
import re
from time import sleep
from app import app
from pdf_generator import gerar_pdf
from utils import validar_dados_formulario
from datetime import datetime

# Define onde o histórico será salvo (pasta do usuário)
HISTORY_FILE = os.path.join(os.path.expanduser("~"), "gerador_pdf_historico.json")

class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def gerar_pdf_desktop(self, dados):
        """
        Função chamada pelo Javascript para gerar o PDF no modo Desktop.
        """
        print("Recebendo dados para geração de PDF via Desktop App...")
        
        # 1. Validação
        erros = validar_dados_formulario(dados)
        if erros:
            return {'status': 'error', 'messages': erros}

        # 2. Sugerir nome de arquivo
        safe_filename = re.sub(r'[^a-zA-Z0-9]', '_', dados.get('nome', 'documento'))
        default_name = f"cadastro_{safe_filename}.pdf"

        # 3. Abrir diálogo de salvar arquivo
        # O pywebview abre o diálogo nativo do SO
        file_path = self.window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory='',
            save_filename=default_name,
            file_types=('PDF Files (*.pdf)', 'All files (*.*)')
        )

        if not file_path:
            return {'status': 'cancelled'}

        # file_path retorna uma string no modo SAVE_DIALOG (ou None se cancelado)
        # Em algumas versões retorna tupla, vamos garantir
        if isinstance(file_path, (tuple, list)):
            file_path = file_path[0]

        try:
            # 4. Gerar PDF
            pdf_buffer = gerar_pdf(dados)
            
            # 5. Salvar no disco
            with open(file_path, 'wb') as f:
                f.write(pdf_buffer.read())

            # 6. Atualizar Histórico
            self.salvar_historico(dados, file_path)

            return {'status': 'success', 'path': file_path}
            
        except Exception as e:
            return {'status': 'error', 'messages': [str(e)]}

    def salvar_historico(self, dados, file_path):
        """Salva registro da geração no histórico."""
        registro = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nome': dados.get('nome'),
            'cpf': dados.get('cpf'),
            'arquivo': file_path
        }
        
        historico = self.ler_historico_raw()
        historico.insert(0, registro) # Adiciona no início
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(historico, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def ler_historico_raw(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def obter_historico(self):
        """Retorna o histórico para o frontend."""
        return self.ler_historico_raw()

def start_server():
    app.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == '__main__':
    # Inicia o servidor Flask em uma thread separada
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Aguarda um pouco para garantir que o servidor subiu
    sleep(1)

    api = Api()
    
    # Cria a janela desktop
    window = webview.create_window(
        'Gerador de PDF Profissional', 
        'http://127.0.0.1:5000',
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600)
    )
    
    api.set_window(window)
    
    # Inicia o loop da GUI
    webview.start(debug=True)
