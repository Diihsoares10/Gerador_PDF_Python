# Gerador de PDF - Versão Desktop

Esta aplicação foi convertida para funcionar como um aplicativo Desktop nativo do Windows.

## Funcionalidades Desktop
- **Instalação Local**: Funciona offline sem necessidade de servidor externo.
- **Interface Nativa**: Abre em janela própria, parecendo um aplicativo nativo.
- **Salvar Como**: Permite escolher onde salvar o arquivo PDF usando o diálogo padrão do Windows.
- **Histórico**: Mantém um registro local de todos os PDFs gerados.
- **Interface Híbrida**: Usa a mesma interface moderna (Bootstrap) da versão Web.

## Como Executar (Modo Desenvolvimento)
Para testar antes de compilar:
1. Certifique-se de ter o Python instalado.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o script principal:
   ```bash
   python desktop_main.py
   ```

## Como Gerar o Executável (.exe)
Para criar o arquivo `.exe` para distribuição:

1. Dê um clique duplo no arquivo `build_exe.bat` incluído na pasta.
2. Aguarde o processo terminar.
3. O executável será criado na pasta `dist/GeradorPDF.exe`.

### Requisitos do Build
- Python 3.x instalado e adicionado ao PATH.
- Internet (apenas para baixar as dependências na primeira vez).

## Estrutura de Arquivos Importantes
- `desktop_main.py`: Ponto de entrada da aplicação Desktop. Gerencia a janela e a API.
- `utils.py`: Funções de validação compartilhadas.
- `app.py`: Backend Flask (ainda usado internamente para renderizar o HTML).
- `static/js/script.js`: Contém lógica para detectar se está rodando no Desktop ou Web.
