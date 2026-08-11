"""Печать пачки записок одним PDF на алтарь.

Лист печатают и кладут на жертвенник, поэтому вёрстка подчинена чтению
вслух: сначала все имена о здравии, потом все о упокоении; внутри —
блоками по подавшему, чтобы записку можно было отложить или уточнить.
Имена набраны крупнее контактов: контакты нужны один раз, имена —
сорок раз.

Шрифты лежат рядом с модулем, а не берутся из системы: на Render базовый
образ может приехать без кириллических TTF, и тогда весь лист выйдет
квадратами. 700 КБ в репозитории дешевле такой поломки.
"""

from html import escape
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT_DIR = Path(__file__).resolve().parent / "fonts"

REGULAR = "ParishSerif"
BOLD = "ParishSerif-Bold"

INK = colors.HexColor("#1c1712")
MUTED = colors.HexColor("#6a6258")
HAIRLINE = colors.HexColor("#d9d3c6")

NAME_COLUMNS = 4


def _register_fonts():
    if REGULAR in pdfmetrics.getRegisteredFontNames():
        return
    pdfmetrics.registerFont(TTFont(REGULAR, str(FONT_DIR / "DejaVuSerif.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD, str(FONT_DIR / "DejaVuSerif-Bold.ttf")))
    pdfmetrics.registerFontFamily(REGULAR, normal=REGULAR, bold=BOLD)


def _styles():
    return {
        "masthead": ParagraphStyle(
            "masthead", fontName=BOLD, fontSize=12, leading=14, textColor=INK
        ),
        "masthead_meta": ParagraphStyle(
            "masthead_meta", fontName=REGULAR, fontSize=7.5, leading=9.5,
            alignment=TA_RIGHT, textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "section", fontName=BOLD, fontSize=13, leading=15, textColor=INK
        ),
        "section_count": ParagraphStyle(
            "section_count", fontName=REGULAR, fontSize=8, leading=10,
            alignment=TA_RIGHT, textColor=MUTED,
        ),
        "submitter": ParagraphStyle(
            "submitter", fontName=BOLD, fontSize=9.5, leading=11.5, textColor=INK
        ),
        "contact": ParagraphStyle(
            "contact", fontName=REGULAR, fontSize=7, leading=9, textColor=MUTED
        ),
        "index": ParagraphStyle(
            "index", fontName=REGULAR, fontSize=6.5, leading=12,
            alignment=TA_RIGHT, textColor=MUTED,
        ),
        "name": ParagraphStyle(
            "name", fontName=REGULAR, fontSize=10, leading=12, textColor=INK
        ),
        "empty": ParagraphStyle(
            "empty", fontName=REGULAR, fontSize=9, leading=12,
            alignment=TA_CENTER, textColor=MUTED,
        ),
    }


def _p(text, style):
    """Абзац из простого текста. Перевод строки в исходнике становится
    переводом строки на листе — reportlab сам по себе его игнорирует."""
    body = "<br/>".join(escape(line) for line in str(text).split("\n"))
    return Paragraph(body, style)


def _plural_names(count):
    """1 имя, 2 имени, 5 имён — иначе шапка раздела читается как ошибка."""
    tail_100 = count % 100
    tail_10 = count % 10
    if 11 <= tail_100 <= 14 or tail_10 == 0 or tail_10 >= 5:
        word = "имён"
    elif tail_10 == 1:
        word = "имя"
    else:
        word = "имени"
    return f"{count} {word}"


def _plural_notes(count):
    tail_100 = count % 100
    tail_10 = count % 10
    if 11 <= tail_100 <= 14 or tail_10 == 0 or tail_10 >= 5:
        return f"{count} записок"
    if tail_10 == 1:
        return f"{count} записка"
    return f"{count} записки"


def _contact_line(note):
    bits = []
    if note.email:
        bits.append(note.email)
    if note.phone:
        bits.append(note.phone)
    bits.append(f"подана {timezone.localtime(note.submitted_at):%d.%m.%Y}")
    if note.total_liturgies > 1:
        current = min(note.printed_count + 1, note.total_liturgies)
        bits.append(f"сорокоуст, литургия {current} из {note.total_liturgies}")
        if note.last_service_date:
            bits.append(f"по {note.last_service_date:%d.%m.%Y}")
    if note.notes:
        bits.append(f"примечание: {note.notes}")
    return "  ·  ".join(bits)


def _names_table(names, width):
    """Имена одной записки в несколько колонок, читаемых сверху вниз.

    Весь список — одна таблица, без разбивки на блоки: высота колонки
    определяется числом имён, и нумерация идёт непрерывно. Разбивка на
    куски давала бы под первой сеткой вторую, и глаз после имени 15
    прыгал бы на 61.
    """
    per_column = max(1, -(-len(names) // NAME_COLUMNS))
    start_index = 1
    column_width = width / NAME_COLUMNS
    styles = _styles()
    columns = []
    for column_index in range(NAME_COLUMNS):
        start = column_index * per_column
        chunk = names[start:start + per_column]
        rows = [
            [
                _p(f"{start_index + start + offset}.", styles["index"]),
                _p(name, styles["name"]),
            ]
            for offset, name in enumerate(chunk)
        ] or [["", ""]]
        table = Table(rows, colWidths=[7 * mm, column_width - 10 * mm])
        commands = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]
        if chunk:
            commands.append(("LINEBELOW", (0, 0), (-1, -1), 0.25, HAIRLINE))
        table.setStyle(TableStyle(commands))
        columns.append(table)

    outer = Table([columns], colWidths=[column_width] * NAME_COLUMNS)
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def _group_header(index, note, width):
    styles = _styles()
    header = Table(
        [[
            _p(f"{index}.", styles["submitter"]),
            _p(note.requester_name or note.email or "без имени", styles["submitter"]),
            _p(_contact_line(note), styles["contact"]),
        ]],
        colWidths=[8 * mm, 38 * mm, width - 46 * mm],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return header


def _section(story, title, notes, attribute, width):
    styles = _styles()
    with_names = [(note, getattr(note, attribute)) for note in notes]
    with_names = [(note, names) for note, names in with_names if names]
    total = sum(len(names) for _note, names in with_names)
    if not total:
        return

    head = Table(
        [[_p(title, styles["section"]),
          _p(_plural_names(total), styles["section_count"])]],
        colWidths=[width * 0.7, width * 0.3],
    )
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, INK),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(KeepTogether([head, Spacer(1, 4 * mm)]))

    for index, (note, names) in enumerate(with_names, start=1):
        # заголовок записки не должен оторваться от своих имён
        story.append(KeepTogether([
            _group_header(index, note, width),
            _names_table(names, width),
            Spacer(1, 5 * mm),
        ]))

    story.append(Spacer(1, 3 * mm))


def render_batch_pdf(batch):
    """Собрать PDF пачки, сохранить его в приватное хранилище и вернуть байты."""
    if not batch.pk:
        raise ValueError("Пачку нужно сохранить до генерации PDF.")

    from core.models import SiteSettings

    _register_fonts()
    styles = _styles()
    site = SiteSettings.get_solo()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=16 * mm,
        title="Имена для поминовения",
        author=site.parish_name,
    )
    width = doc.width

    notes = list(batch.notes.order_by("kind", "submitted_at", "pk"))
    service_date = batch.service_date or timezone.localdate(batch.created_at)

    masthead = Table(
        [[
            _p(site.parish_name.upper(), styles["masthead"]),
            _p(f"Имена для поминовения\n"
               f"{service_date:%d.%m.%Y}  ·  {_plural_notes(len(notes))}",
               styles["masthead_meta"]),
        ]],
        colWidths=[width * 0.6, width * 0.4],
    )
    masthead.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, INK),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story = [masthead, Spacer(1, 6 * mm)]
    _section(story, "О ЗДРАВИИ", notes, "living_list", width)
    _section(story, "О УПОКОЕНИИ", notes, "departed_list", width)
    if len(story) == 2:
        story.append(_p("В этой пачке нет имён.", styles["empty"]))

    footer_line = "  ·  ".join(
        part for part in [site.parish_name, site.city, site.phone] if part
    )

    def draw_footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(HAIRLINE)
        canvas.setLineWidth(0.75)
        canvas.line(doc_obj.leftMargin, 12 * mm,
                    A4[0] - doc_obj.rightMargin, 12 * mm)
        canvas.setFont(REGULAR, 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc_obj.leftMargin, 7 * mm, footer_line)
        canvas.drawRightString(A4[0] - doc_obj.rightMargin, 7 * mm,
                               f"стр. {doc_obj.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    pdf_bytes = buffer.getvalue()

    stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
    batch.pdf_file.save(
        f"zapiski-{batch.pk}-{stamp}.pdf", ContentFile(pdf_bytes), save=False
    )
    batch.status = batch.Status.PDF_READY
    batch.error_message = ""
    batch.save(update_fields=["pdf_file", "status", "error_message"])
    return pdf_bytes
