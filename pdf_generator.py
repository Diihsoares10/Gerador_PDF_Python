"""Modern PDF generator for Cadastramento!

Visual identity matches the website: indigo + sky + teal palette,
glassy section cards, hero header with key fields, footer with page
numbers and brand mark.
"""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ---------- Brand palette (matches static/css/style.css :root) ----------
PRIMARY = colors.HexColor("#4f46e5")        # indigo-600
PRIMARY_DARK = colors.HexColor("#3730a3")   # indigo-800
SECONDARY = colors.HexColor("#0ea5e9")      # sky-500
TERTIARY = colors.HexColor("#14b8a6")       # teal-500
TEXT_PRIMARY = colors.HexColor("#0f172a")   # slate-900
TEXT_SECONDARY = colors.HexColor("#475569") # slate-600
TEXT_MUTED = colors.HexColor("#94a3b8")     # slate-400
SURFACE = colors.HexColor("#f8fafc")        # slate-50
SURFACE_ALT = colors.HexColor("#f1f5f9")    # slate-100
BORDER = colors.HexColor("#e2e8f0")         # slate-200
SUCCESS = colors.HexColor("#10b981")        # emerald-500
SUCCESS_BG = colors.HexColor("#d1fae5")

PAGE_W, PAGE_H = A4
MARGIN_X = 18 * mm
HEADER_H = 56 * mm
FOOTER_H = 18 * mm


# ---------- Helpers ----------
def _safe(value, fallback="—"):
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _calc_idade(data_nasc_str):
    if not data_nasc_str:
        return None
    try:
        d = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    try:
        from app import BR_TZ
        hoje = datetime.now(BR_TZ).date()
    except Exception:
        hoje = datetime.now().date()
    return hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day))


def _now_brt():
    try:
        from app import BR_TZ
        return datetime.now(BR_TZ)
    except Exception:
        return datetime.now()


def _fmt_data(data_str):
    if not data_str:
        return "—"
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return data_str


def _draw_logo_mark(c, x, y, size=10 * mm):
    """Small rounded square with a stylised feather (mimics the site's brand chip)."""
    c.saveState()
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.white)
    c.roundRect(x, y, size, size, 2 * mm, stroke=0, fill=1)
    # Inner gradient simulation: a darker square overlay
    c.setFillColor(PRIMARY_DARK)
    c.roundRect(x + 1.5 * mm, y + 1.5 * mm, size - 3 * mm, size - 3 * mm, 1.5 * mm, stroke=0, fill=1)
    # Tiny accent dot
    c.setFillColor(TERTIARY)
    c.circle(x + size * 0.72, y + size * 0.72, 1.1 * mm, stroke=0, fill=1)
    c.restoreState()


def _draw_header(canv, doc, hero_data):
    """Render the colored hero band on every page."""
    canv.saveState()

    # Solid indigo band
    band_top = PAGE_H
    band_bottom = PAGE_H - HEADER_H
    canv.setFillColor(PRIMARY)
    canv.rect(0, band_bottom, PAGE_W, HEADER_H, stroke=0, fill=1)

    # Subtle teal accent stripe at the very bottom of the band
    canv.setFillColor(TERTIARY)
    canv.rect(0, band_bottom, PAGE_W, 1.6 * mm, stroke=0, fill=1)
    canv.setFillColor(SECONDARY)
    canv.rect(0, band_bottom + 1.6 * mm, PAGE_W * 0.55, 0.8 * mm, stroke=0, fill=1)

    # Brand mark + product name (top-left)
    logo_x = MARGIN_X
    logo_y = PAGE_H - 16 * mm
    _draw_logo_mark(canv, logo_x, logo_y, size=10 * mm)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 13)
    canv.drawString(logo_x + 13 * mm, logo_y + 6 * mm, "Cadastramento!")
    canv.setFont("Helvetica", 8.5)
    canv.setFillColor(colors.HexColor("#c7d2fe"))
    canv.drawString(logo_x + 13 * mm, logo_y + 1.5 * mm, "Ficha cadastral digital")

    # Status pill top-right
    pill_text = "Cadastro completo"
    canv.setFont("Helvetica-Bold", 8)
    pill_w = canv.stringWidth(pill_text, "Helvetica-Bold", 8) + 14
    pill_h = 16
    pill_x = PAGE_W - MARGIN_X - pill_w
    pill_y = PAGE_H - 14 * mm
    canv.setFillColor(colors.HexColor("#ecfdf5"))
    canv.roundRect(pill_x, pill_y, pill_w, pill_h, 8, stroke=0, fill=1)
    canv.setFillColor(SUCCESS)
    canv.circle(pill_x + 7, pill_y + 8, 2.3, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#047857"))
    canv.drawString(pill_x + 12, pill_y + 4.5, pill_text)

    # Big title centred
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 22)
    canv.drawString(MARGIN_X, PAGE_H - 32 * mm, hero_data.get("title", "Ficha de Cadastro"))

    # Sub-row: nome + CPF
    canv.setFont("Helvetica", 10)
    canv.setFillColor(colors.HexColor("#e0e7ff"))
    canv.drawString(MARGIN_X, PAGE_H - 38 * mm,
                    f"Titular: {hero_data.get('nome', '—')}   ·   CPF: {hero_data.get('cpf', '—')}")

    # Generation timestamp (right)
    canv.setFont("Helvetica", 8.5)
    canv.setFillColor(colors.HexColor("#c7d2fe"))
    gen_label = f"Emitido em {hero_data.get('gen_at', '')}"
    canv.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 38 * mm, gen_label)

    canv.restoreState()


def _draw_footer(canv, doc):
    canv.saveState()
    # Thin separator
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(MARGIN_X, FOOTER_H, PAGE_W - MARGIN_X, FOOTER_H)

    canv.setFont("Helvetica", 8)
    canv.setFillColor(TEXT_MUTED)
    canv.drawString(MARGIN_X, FOOTER_H - 10,
                    "Documento gerado eletronicamente · Cadastramento!")
    page_num = canv.getPageNumber()
    canv.drawRightString(PAGE_W - MARGIN_X, FOOTER_H - 10, f"Página {page_num}")
    canv.restoreState()


def _section_header(text, accent=PRIMARY):
    """Section title rendered as a 1-row table with a coloured left bar."""
    style = ParagraphStyle(
        "SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=TEXT_PRIMARY,
        leading=14,
        spaceBefore=0,
        spaceAfter=0,
    )
    para = Paragraph(text.upper(), style)
    tbl = Table([[para]], colWidths=[PAGE_W - 2 * MARGIN_X])
    tbl.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE_ALT),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return tbl


def _info_table(rows):
    """Two-column key/value table with alternating row backgrounds."""
    label_style = ParagraphStyle(
        "Label",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=TEXT_MUTED,
        leading=11,
        spaceAfter=2,
    )
    value_style = ParagraphStyle(
        "Value",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        textColor=TEXT_PRIMARY,
        leading=14,
    )

    cells = []
    pair = []
    for label, value in rows:
        block = [
            Paragraph(label.upper(), label_style),
            Paragraph(_safe(value), value_style),
        ]
        # Stack label and value vertically inside one cell using a mini-table.
        inner = Table([[block[0]], [block[1]]], colWidths=[(PAGE_W - 2 * MARGIN_X) / 2 - 16])
        inner.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (0, 0), 1),
            ("BOTTOMPADDING", (0, 1), (0, 1), 0),
        ]))
        pair.append(inner)
        if len(pair) == 2:
            cells.append(pair)
            pair = []
    if pair:
        pair.append("")
        cells.append(pair)

    col_w = (PAGE_W - 2 * MARGIN_X) / 2
    tbl = Table(cells, colWidths=[col_w, col_w])
    style_cmds = [
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
    ]
    # Alternating row backgrounds
    for i in range(len(cells)):
        bg = colors.white if i % 2 == 0 else SURFACE
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def _full_width_block(label, text, accent=SECONDARY):
    """A single full-width card (used for endereço, observações)."""
    label_style = ParagraphStyle(
        "BlockLabel",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=TEXT_MUTED,
        leading=11,
    )
    value_style = ParagraphStyle(
        "BlockValue",
        fontName="Helvetica",
        fontSize=11,
        textColor=TEXT_PRIMARY,
        leading=15,
    )
    inner = Table(
        [[Paragraph(label.upper(), label_style)], [Paragraph(_safe(text), value_style)]],
        colWidths=[PAGE_W - 2 * MARGIN_X - 28],
    )
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 4),
        ("BOTTOMPADDING", (0, 1), (0, 1), 0),
    ]))
    wrap = Table([[inner]], colWidths=[PAGE_W - 2 * MARGIN_X])
    wrap.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
    ]))
    return wrap


# ---------- Main entry ----------
def gerar_pdf(dados):
    """Generate the modern Cadastramento! PDF and return a BytesIO buffer."""
    dados = dados or {}
    buffer = io.BytesIO()

    hero = {
        "title": "Ficha de Cadastro",
        "nome": _safe(dados.get("nome")),
        "cpf": _safe(dados.get("cpf")),
        "gen_at": _now_brt().strftime("%d/%m/%Y às %H:%M"),
    }

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=HEADER_H + 8 * mm,
        bottomMargin=FOOTER_H + 6 * mm,
        title=f"Ficha de Cadastro — {hero['nome']}",
        author="Cadastramento!",
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        showBoundary=0,
    )

    def on_page(canv, d):
        _draw_header(canv, d, hero)
        _draw_footer(canv, d)

    doc.addPageTemplates([PageTemplate(id="Main", frames=[frame], onPage=on_page)])

    story = []

    # ------ Resumo destacado ------
    idade = _calc_idade(dados.get("data_nascimento"))
    summary_rows = [
        ("Cidade", _safe(dados.get("cidade"))),
        ("UF", _safe(dados.get("estado"))),
        ("Data de nascimento", _fmt_data(dados.get("data_nascimento"))),
        ("Idade", f"{idade} anos" if idade is not None else "—"),
    ]
    summary_cells = []
    for label, value in summary_rows:
        cell = Table(
            [[Paragraph(label.upper(),
                        ParagraphStyle("sl", fontName="Helvetica", fontSize=7.5,
                                       textColor=TEXT_MUTED, leading=10))],
             [Paragraph(_safe(value),
                        ParagraphStyle("sv", fontName="Helvetica-Bold", fontSize=11.5,
                                       textColor=PRIMARY, leading=14))]],
            colWidths=[(PAGE_W - 2 * MARGIN_X) / 4 - 8],
        )
        cell.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (0, 0), 0),
            ("BOTTOMPADDING", (0, 0), (0, 0), 2),
            ("TOPPADDING", (0, 1), (0, 1), 0),
            ("BOTTOMPADDING", (0, 1), (0, 1), 0),
        ]))
        summary_cells.append(cell)

    quarter = (PAGE_W - 2 * MARGIN_X) / 4
    summary = Table([summary_cells], colWidths=[quarter] * 4)
    summary.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#c7d2fe")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEAFTER", (0, 0), (-2, -1), 0.4, colors.HexColor("#c7d2fe")),
    ]))
    story.append(summary)
    story.append(Spacer(1, 14))

    # ------ Dados pessoais ------
    story.append(KeepTogether([
        _section_header("Dados pessoais", accent=PRIMARY),
        Spacer(1, 4),
        _info_table([
            ("Nome completo", dados.get("nome")),
            ("CPF", dados.get("cpf")),
            ("RG", dados.get("rg")),
            ("Data de nascimento", _fmt_data(dados.get("data_nascimento"))),
            ("Gênero", dados.get("genero")),
            ("Estado civil", dados.get("estado_civil")),
            ("Nome da mãe", dados.get("nome_mae")),
            ("Profissão", dados.get("profissao")),
        ]),
    ]))
    story.append(Spacer(1, 14))

    # ------ Contato ------
    story.append(KeepTogether([
        _section_header("Informações de contato", accent=SECONDARY),
        Spacer(1, 4),
        _info_table([
            ("Email", dados.get("email")),
            ("Telefone celular", dados.get("telefone")),
        ]),
    ]))
    story.append(Spacer(1, 14))

    # ------ Endereço ------
    logradouro = _safe(dados.get("logradouro"), "")
    numero = _safe(dados.get("numero"), "")
    complemento = dados.get("complemento")
    end_line = ", ".join([p for p in [logradouro, numero] if p and p != "—"])
    if complemento:
        end_line = f"{end_line} — {complemento}" if end_line else complemento
    end_text = end_line or "—"

    story.append(_section_header("Endereço", accent=TERTIARY))
    story.append(Spacer(1, 4))
    story.append(_full_width_block("Logradouro completo", end_text, accent=TERTIARY))
    story.append(Spacer(1, 6))
    story.append(_info_table([
        ("CEP", dados.get("cep")),
        ("Bairro", dados.get("bairro")),
        ("Cidade", dados.get("cidade")),
        ("Estado (UF)", dados.get("estado")),
    ]))
    story.append(Spacer(1, 14))

    # ------ Observações ------
    obs = (dados.get("observacao") or "").strip() or "Nenhuma observação registrada."
    story.append(_section_header("Observações", accent=PRIMARY))
    story.append(Spacer(1, 4))
    story.append(_full_width_block("Comentários adicionais", obs, accent=PRIMARY))

    # ------ Carimbo de autenticidade ------
    story.append(Spacer(1, 18))
    stamp_para = Paragraph(
        '<font color="#475569">Este documento foi gerado eletronicamente pelo sistema '
        '<b>Cadastramento!</b>. Os dados acima foram informados pelo próprio titular '
        f'em {hero["gen_at"]} (horário de Brasília).</font>',
        ParagraphStyle("Stamp", fontName="Helvetica", fontSize=8.5,
                       textColor=TEXT_SECONDARY, leading=12, alignment=TA_CENTER),
    )
    stamp_wrap = Table([[stamp_para]], colWidths=[PAGE_W - 2 * MARGIN_X])
    stamp_wrap.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(stamp_wrap)

    doc.build(story)
    buffer.seek(0)
    return buffer
