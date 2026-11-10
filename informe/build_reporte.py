"""Construye el informe APA 7 (GUIA APA CETO) de la Actividad 4.

Toma ``body.md`` como fuente unica de contenido y produce un .docx con:

* portada institucional, resumen, indice automatico (campo TOC);
* jerarquia de titulos APA 7 (niveles 1 a 3, sin numeracion);
* figuras con numero, titulo y nota (APA 7);
* tablas con numero, titulo, encabezado en negrita y bordes APA;
* referencias con sangria francesa y orden alfabetico;
* numeracion de pagina en el encabezado.

Marcas propias en ``body.md``:

    [[TABLA|Titulo de la tabla]]      precede a la tabla markdown
    [[FIG|ruta/relativa.png|Titulo|Nota]]

Uso:
    python build_reporte.py
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
BODY = ROOT / "body.md"
OUTPUT = ROOT / "Informe_Actividad4_Tejiendo_Redes.docx"

TITULO = "Tejiendo redes: arquitectura de software entre hilos y nodos"
SUBTITULO = "NexusAI 2.0: de la arquitectura a la red"
AUTORES = (
    "Juan Carlos Benítez Rojas\n"
    "Líder de proyecto y arquitecto de software\n"
    "\n"
    "Juan José Córdoba Eraso\n"
    "Desarrollador y evaluador de calidad"
)
INSTITUCION = "Corporación Escuela Tecnológica del Oriente"
PROGRAMA = "Ingeniería de Software"
CURSO = "Arquitectura de Software — Unidad 2"
DOCENTE = "Leidy Johana Polo"
FECHA = "11 de noviembre de 2026"
RUNNING_HEAD = "TEJIENDO REDES"

FONT = "Times New Roman"
TEXT_WIDTH_IN = 6.5


# ---------------------------------------------------------------------------
# Utilidades de formato
# ---------------------------------------------------------------------------
def set_run(run, size=12, bold=False, italic=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    return run


def base_paragraph(paragraph, first_indent=0.0, left_indent=0.0, spacing=2.0, align=None):
    pf = paragraph.paragraph_format
    pf.line_spacing = spacing
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = Inches(first_indent)
    pf.left_indent = Inches(left_indent)
    pf.widow_control = True
    if align is not None:
        paragraph.alignment = align
    return paragraph


def add_runs(paragraph, text, size=12, base_bold=False):
    """Interpreta **negrita**, *cursiva* y `codigo` dentro de un texto."""
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|`.*?`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            set_run(paragraph.add_run(part[2:-2]), size=size, bold=True)
        elif part.startswith("*") and part.endswith("*") and len(part) >= 2:
            set_run(paragraph.add_run(part[1:-1]), size=size, italic=True)
        elif part.startswith("`") and part.endswith("`") and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Courier New"
            run.font.size = Pt(size - 1.5)
        else:
            set_run(paragraph.add_run(part), size=size, bold=base_bold)


def add_page_number_header(section):
    header = section.header
    header.is_linked_to_previous = False
    paragraph = header.paragraphs[0]
    paragraph.text = ""
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(paragraph.add_run(RUNNING_HEAD + "\t"), size=9)
    fld_begin = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls("w"))
    fld_sep = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
    fld_end = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
    run = paragraph.add_run()
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)
    set_run(run, size=11)
    # tabulador derecho en el margen
    pPr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:pos"), str(int(TEXT_WIDTH_IN * 1440)))
    tabs.append(tab)
    pPr.append(tabs)


def heading(doc, text, level, page_break=False, page_break_before=False):
    if page_break:
        doc.add_page_break()
    paragraph = doc.add_paragraph()
    pf = paragraph.paragraph_format
    pf.line_spacing = 2.0
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.keep_with_next = True
    pf.keep_together = True
    if page_break_before:
        pf.page_break_before = True
    if level == 1:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(paragraph.add_run(text), bold=True)
    elif level == 2:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        set_run(paragraph.add_run(text), bold=True)
    else:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        set_run(paragraph.add_run(text), bold=True, italic=True)
    # nivel real de esquema para que el campo TOC lo reconozca
    pPr = paragraph._p.get_or_add_pPr()
    outline = OxmlElement("w:outlineLvl")
    outline.set(qn("w:val"), str(level - 1))
    pPr.append(outline)
    return paragraph


def add_toc(doc):
    paragraph = doc.add_paragraph()
    base_paragraph(paragraph, align=WD_ALIGN_PARAGRAPH.LEFT)
    run = paragraph.add_run()
    fld_begin = parse_xml(r'<w:fldChar %s w:fldCharType="begin" w:dirty="true"/>' % nsdecls("w"))
    instr = parse_xml(
        r'<w:instrText %s xml:space="preserve"> TOC \o "1-2" \h \z \u </w:instrText>' % nsdecls("w")
    )
    fld_sep = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
    placeholder = OxmlElement("w:t")
    placeholder.text = "Actualice el indice con clic derecho > Actualizar campo."
    fld_end = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(placeholder)
    run._r.append(fld_end)


# ---------------------------------------------------------------------------
# Tablas y figuras
# ---------------------------------------------------------------------------
def _set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        r'<w:tblBorders %s>'
        r'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        r'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        r'<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r"</w:tblBorders>" % nsdecls("w")
    )
    tblPr.append(borders)


def _mark_header_row(row):
    trPr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    trPr.append(header)
    cant_split = OxmlElement("w:cantSplit")
    cant_split.set(qn("w:val"), "true")
    trPr.append(cant_split)


def add_table(doc, rows, number, title, note=""):
    caption = doc.add_paragraph()
    base_paragraph(caption)
    caption.paragraph_format.keep_with_next = True
    set_run(caption.add_run(f"Tabla {number}"), bold=True)

    title_p = doc.add_paragraph()
    base_paragraph(title_p)
    title_p.paragraph_format.keep_with_next = True
    set_run(title_p.add_run(title), italic=True)

    cols = max(len(row) for row in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = True
    _set_table_borders(table)

    # Una cadena sin espacios (por ejemplo una URL) dentro de una celda
    # estrecha puede hacer que Word entre en un bucle de maquetacion al
    # exportar a PDF. Cuando la tabla es de dos columnas y aparece un token
    # largo se fijan anchos explicitos para que el texto quepa en una linea.
    longest_token = max(
        (len(token) for row in rows for value in row for token in value.split()),
        default=0,
    )
    if cols == 2 and longest_token >= 45:
        def _longest_word(text):
            return max((len(token) for token in text.split()), default=0)

        first = min(40, max(12, max(_longest_word(row[0]) for row in rows if row)))
        second = max(longest_token, 20)
        total = first + second
        widths = [max(1.4, TEXT_WIDTH_IN * first / total), 0]
        widths[1] = TEXT_WIDTH_IN - widths[0]
        table.autofit = False
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        table._tbl.tblPr.append(layout)
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Inches(width)

    for r_idx, row in enumerate(rows):
        for c_idx in range(cols):
            value = row[c_idx] if c_idx < len(row) else ""
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.line_spacing = 1.0
            paragraph.paragraph_format.space_before = Pt(3)
            paragraph.paragraph_format.space_after = Pt(3)
            add_runs(paragraph, value, size=10, base_bold=(r_idx == 0))
        if r_idx == 0:
            _mark_header_row(table.rows[0])
            for c_idx in range(cols):
                cell = table.cell(0, c_idx)
                tcPr = cell._tc.get_or_add_tcPr()
                tcBorders = parse_xml(
                    r'<w:tcBorders %s><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/></w:tcBorders>'
                    % nsdecls("w")
                )
                tcPr.append(tcBorders)

    if note:
        note_p = doc.add_paragraph()
        base_paragraph(note_p)
        set_run(note_p.add_run("Nota. "), size=10, italic=True)
        add_runs(note_p, note, size=10)


def add_figure(doc, rel_path, number, caption, note=""):
    path = (PROJECT / rel_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"no existe la figura: {path}")

    label = doc.add_paragraph()
    base_paragraph(label)
    label.paragraph_format.keep_with_next = True
    set_run(label.add_run(f"Figura {number}"), bold=True)

    title_p = doc.add_paragraph()
    base_paragraph(title_p)
    title_p.paragraph_format.keep_with_next = True
    set_run(title_p.add_run(caption), italic=True)

    with Image.open(path) as image:
        width_px, height_px = image.size
    width_in = min(TEXT_WIDTH_IN, 7.2 * width_px / height_px)
    height_in = width_in * height_px / width_px
    if height_in > 7.6:
        height_in = 7.6
        width_in = height_in * width_px / height_px

    picture_p = doc.add_paragraph()
    base_paragraph(picture_p, align=WD_ALIGN_PARAGRAPH.CENTER)
    picture_p.paragraph_format.keep_with_next = bool(note)
    picture_p.add_run().add_picture(str(path), width=Inches(width_in), height=Inches(height_in))

    if note:
        note_p = doc.add_paragraph()
        base_paragraph(note_p)
        set_run(note_p.add_run("Nota. "), size=10, italic=True)
        add_runs(note_p, note, size=10)


# ---------------------------------------------------------------------------
# Portada, resumen e indice
# ---------------------------------------------------------------------------
def build_cover(doc):
    for _ in range(3):
        base_paragraph(doc.add_paragraph())

    p = doc.add_paragraph()
    base_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(TITULO), bold=True)

    p = doc.add_paragraph()
    base_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(SUBTITULO), italic=True)

    for _ in range(2):
        base_paragraph(doc.add_paragraph())

    for line in AUTORES.split("\n"):
        p = doc.add_paragraph()
        base_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_run(p.add_run(line))

    for _ in range(2):
        base_paragraph(doc.add_paragraph())

    for line in (INSTITUCION, PROGRAMA, CURSO, DOCENTE, FECHA):
        p = doc.add_paragraph()
        base_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_run(p.add_run(line))

    doc.add_page_break()


def build_abstract(doc, abstract, keywords):
    p = doc.add_paragraph()
    base_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run("Resumen"), bold=True)

    p = doc.add_paragraph()
    base_paragraph(p)
    add_runs(p, abstract)

    p = doc.add_paragraph()
    base_paragraph(p, first_indent=0.5)
    set_run(p.add_run("Palabras clave: "), italic=True)
    set_run(p.add_run(keywords))

    doc.add_page_break()


def build_toc_page(doc):
    p = doc.add_paragraph()
    base_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run("Índice"), bold=True)
    add_toc(doc)


# ---------------------------------------------------------------------------
# Cuerpo
# ---------------------------------------------------------------------------
TABLE_MARK = re.compile(r"^\[\[TABLA\|(.+)\]\]$")
FIG_MARK = re.compile(r"^\[\[FIG\|(.+)\]\]$")
HEADING_MARK = re.compile(r"^(#{1,3})\s+(.*)$")
LEVEL_MARK = re.compile(r"^§\d§\s*")


def parse_markdown(doc, text, references: str = ""):
    lines = text.splitlines()
    pending_table_title = None
    table_rows: list[list[str]] = []
    table_note = ""
    table_number = 0
    figure_number = 0
    index = 0
    first_level_seen = False
    in_code = False
    code_buffer: list[str] = []

    def flush_code():
        nonlocal code_buffer
        if not code_buffer:
            return
        for code_line in code_buffer:
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing = 1.0
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            pf.left_indent = Inches(0.25)
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:fill"), "F2F2F2")
            pPr.append(shd)
            run = p.add_run(code_line if code_line else " ")
            run.font.name = "Courier New"
            run.font.size = Pt(8.5)
        code_buffer = []

    def flush_table():
        nonlocal table_rows, pending_table_title, table_number, table_note
        if table_rows:
            table_number += 1
            add_table(
                doc,
                table_rows,
                table_number,
                pending_table_title or "",
                table_note,
            )
            table_rows = []
            pending_table_title = None
            table_note = ""

    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        index += 1

        if not line:
            if in_code:
                code_buffer.append("")
            else:
                flush_table()
            continue

        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_table()
                in_code = True
            continue

        if in_code:
            code_buffer.append(raw.rstrip())
            continue

        match = TABLE_MARK.match(line)
        if match:
            flush_table()
            pending_table_title = match.group(1).strip()
            continue

        match = FIG_MARK.match(line)
        if match:
            flush_table()
            parts = [part.strip() for part in match.group(1).split("|")]
            rel_path, caption = parts[0], parts[1] if len(parts) > 1 else ""
            note = parts[2] if len(parts) > 2 else ""
            figure_number += 1
            add_figure(doc, rel_path, figure_number, caption, note)
            continue

        if line.startswith("|") and line.endswith("|"):
            if re.match(r"^\|[\s\-:\|]+\|$", line):
                continue
            table_rows.append([cell.strip() for cell in line[1:-1].split("|")])
            continue

        if table_rows:
            flush_table()

        match = HEADING_MARK.match(line)
        if match:
            level = len(match.group(1))
            title = LEVEL_MARK.sub("", match.group(2)).strip()
            if level == 1 and title.lower().startswith("referencias"):
                flush_code()
                in_code = False
                build_references(doc, references)
                continue
            page_break = level == 1 and title.lower().startswith("anexo")
            if level == 1 and not first_level_seen:
                page_break = False
                first_level_seen = True
                heading(doc, title, level, page_break_before=True)
            else:
                heading(doc, title, level, page_break=page_break)
            continue

        if line.startswith("> "):
            p = doc.add_paragraph()
            base_paragraph(p, left_indent=0.5)
            add_runs(p, line[2:])
            continue

        if line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            pf = p.paragraph_format
            pf.line_spacing = 2.0
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            pf.left_indent = Inches(0.5)
            pf.first_line_indent = Inches(-0.25)
            add_runs(p, line[2:])
            continue

        p = doc.add_paragraph()
        base_paragraph(p, first_indent=0.5)
        add_runs(p, line)

    flush_table()


def build_references(doc, references: str):
    heading(doc, "Referencias", 1, page_break=True)
    entries = [entry.strip() for entry in references.splitlines() if entry.strip()]
    entries.sort(key=lambda value: re.sub(r"^[^A-Za-zÁÉÍÓÚÑáéíóúñ]+", "", value).lower())
    for entry in entries:
        p = doc.add_paragraph()
        base_paragraph(p, left_indent=0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        add_runs(p, entry)


# ---------------------------------------------------------------------------
def main():
    body = BODY.read_text(encoding="utf-8")
    abstract_block = (ROOT / "resumen.md").read_text(encoding="utf-8")
    abstract_lines = [line.strip() for line in abstract_block.splitlines() if line.strip()]
    abstract = abstract_lines[0]
    keywords = abstract_lines[1].replace("Palabras clave:", "").strip()
    references = (ROOT / "referencias.md").read_text(encoding="utf-8")

    doc = Document()

    # Estilo base
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2.0
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.header_distance = Inches(0.5)
        section.footer_distance = Inches(0.5)
        add_page_number_header(section)

    build_cover(doc)
    build_abstract(doc, abstract, keywords)
    build_toc_page(doc)
    parse_markdown(doc, body, references)

    doc.core_properties.title = f"{TITULO}. {SUBTITULO}"
    doc.core_properties.author = "Juan Carlos Benítez Rojas; Juan José Córdoba Eraso"
    doc.core_properties.subject = "Actividad 4 — Arquitectura de Software — CETO"
    doc.save(OUTPUT)
    print(f"OK -> {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
