from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import io
from datetime import datetime

def gerar_pdf(dados):
    """
    Função responsável por gerar o arquivo PDF com os dados completos do cadastro.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo do Título
    titulo_style = ParagraphStyle(
        'TituloPersonalizado',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#0d6efd"),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Estilo de Seção
    secao_style = ParagraphStyle(
        'SecaoPersonalizada',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#333333"),
        spaceBefore=15,
        spaceAfter=10,
        borderPadding=5,
        borderWidth=0,
        borderColor=colors.HexColor("#0d6efd")
    )

    # Estilo de Texto Normal
    normal_style = ParagraphStyle(
        'TextoNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )

    # --- Cabeçalho ---
    story.append(Paragraph("Ficha Cadastral", titulo_style))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", 
                          ParagraphStyle('Data', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey)))
    story.append(Spacer(1, 20))

    # --- Função auxiliar para criar tabelas de seção ---
    def criar_tabela_dados(lista_dados):
        # Converte dados em Paragraphs para permitir quebra de linha
        data_processed = []
        for row in lista_dados:
            label = Paragraph(f"<b>{row[0]}</b>", normal_style)
            value = Paragraph(str(row[1]) if row[1] else "-", normal_style)
            data_processed.append([label, value])
            
        t = Table(data_processed, colWidths=[2.5*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8f9fa")), # Cor de fundo coluna chaves
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")), # Linhas finas cinza
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#ced4da")), # Borda externa
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    # --- Dados Pessoais ---
    story.append(Paragraph("Dados Pessoais", secao_style))
    dados_pessoais = [
        ["Nome Completo", dados.get('nome')],
        ["CPF", dados.get('cpf')],
        ["RG", dados.get('rg')],
        ["Data de Nascimento", datetime.strptime(dados.get('data_nascimento'), '%Y-%m-%d').strftime('%d/%m/%Y') if dados.get('data_nascimento') else "-"],
        ["Idade", f"{datetime.now().year - int(dados.get('data_nascimento')[:4])} anos" if dados.get('data_nascimento') else "-"],
        ["Gênero", dados.get('genero')],
        ["Estado Civil", dados.get('estado_civil')],
        ["Nome da Mãe", dados.get('nome_mae')],
        ["Profissão", dados.get('profissao')],
    ]
    story.append(criar_tabela_dados(dados_pessoais))

    # --- Contato ---
    story.append(Paragraph("Informações de Contato", secao_style))
    dados_contato = [
        ["Email", dados.get('email')],
        ["Telefone Celular", dados.get('telefone')],
    ]
    story.append(criar_tabela_dados(dados_contato))

    # --- Endereço ---
    story.append(Paragraph("Endereço Completo", secao_style))
    endereco_completo = f"{dados.get('logradouro')}, {dados.get('numero')}"
    if dados.get('complemento'):
        endereco_completo += f" - {dados.get('complemento')}"
    
    dados_endereco = [
        ["CEP", dados.get('cep')],
        ["Endereço", endereco_completo],
        ["Bairro", dados.get('bairro')],
        ["Cidade/UF", f"{dados.get('cidade')} / {dados.get('estado')}"],
    ]
    story.append(criar_tabela_dados(dados_endereco))

    # --- Observações ---
    story.append(Paragraph("Observações", secao_style))
    obs_text = dados.get('observacao', '')
    if not obs_text:
        obs_text = "Nenhuma observação registrada."
    
    # Caixa de texto para observações
    tbl_obs = Table([[Paragraph(obs_text, normal_style)]], colWidths=[6.5*inch])
    tbl_obs.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#ced4da")),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
    ]))
    story.append(tbl_obs)

    # --- Rodapé ---
    story.append(Spacer(1, 40))
    texto_rodape = "Este documento é digital e foi gerado automaticamente pelo sistema de cadastro."
    story.append(Paragraph(texto_rodape, ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))

    doc.build(story)
    buffer.seek(0)
    return buffer
