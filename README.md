Gerador de PDF a partir de documentos DOCX em Python
Este é um projeto Python que oferece uma solução simples e eficaz para gerar arquivos PDF a partir de documentos DOCX. O objetivo é fornecer uma ferramenta leve e fácil de usar para a conversão de documentos, tornando mais simples o processo de criação de arquivos PDF a partir de documentos editáveis.

Funcionalidades
Conversão de DOCX para PDF: O projeto permite a conversão de documentos DOCX para o formato PDF com apenas algumas linhas de código.
Personalização do PDF: É possível personalizar o PDF gerado conforme necessário, incluindo configurações de página, margens, fontes e muito mais.
Facilidade de Uso: A API é projetada para ser intuitiva e simples de usar, permitindo que você integre facilmente a funcionalidade de conversão em seus próprios projetos.
Requisitos
Python 3.x
Bibliotecas Python:
python-docx para manipulação de documentos DOCX.
pdfkit para a conversão de HTML para PDF.
Você pode instalar as bibliotecas necessárias executando:

bash
Copy code
pip install python-docx pdfkit
Uso
Instale as DependênciasAntes de usar o projeto, instale as dependências necessárias com o comando:
bash
Copy code
pip install python-docx pdfkit
Convertendo DOCX para PDFPara converter um documento DOCX para PDF, utilize o seguinte código Python:
python
Copy code
from docx_to_pdf import convert_to_pdf

# Caminho do arquivo DOCX de entrada e PDF de saída
docx_file = "caminho/do/seu/arquivo.docx"
pdf_file = "caminho/do/seu/arquivo.pdf"

# Convertendo o documento DOCX para PDF
convert_to_pdf(docx_file, pdf_file)
Este código irá ler o arquivo DOCX especificado e gerar um arquivo PDF correspondente.
Personalização (Opcional)Você pode personalizar o PDF gerado ajustando as opções de conversão. Consulte a documentação da biblioteca pdfkit para mais detalhes sobre as opções disponíveis.
Exemplo
Aqui está um exemplo completo de como converter um documento DOCX para PDF:

python
Copy code
from docx_to_pdf import convert_to_pdf

# Caminho do arquivo DOCX de entrada e PDF de saída
docx_file = "caminho/do/seu/arquivo.docx"
pdf_file = "caminho/do/seu/arquivo.pdf"

# Convertendo o documento DOCX para PDF
convert_to_pdf(docx_file, pdf_file)
Contribuição
Contribuições são bem-vindas! Se você encontrar um problema ou deseja melhorar este projeto, fique à vontade para abrir uma issue ou enviar um pull request.

Licença
Este projeto é licenciado sob a MIT License.
