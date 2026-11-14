import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

FONT_FAMILY = "Times New Roman"
BODY_FONT_SIZE = Pt(12)
SECTION_FONT_SIZE = Pt(16)
SUBSECTION_FONT_SIZE = Pt(14)
CHAPTER_NUM_SIZE = Pt(16)
CHAPTER_TITLE_SIZE = Pt(18)
TABLE_TITLE_SIZE = Pt(11)
FIGURE_CAPTION_SIZE = Pt(10.5)

PROJECT_TITLE = "INTELLIGENT CLOUD OUTAGE DETECTION AND PREDICTION SYSTEM"
FOOTER_LEFT = "Dept. of CS&E, BIT"
FOOTER_CENTER = "2026–2027"

def create_base_document():
    doc = docx.Document()
    
    # Set default style
    normal_style = doc.styles['Normal']
    normal_style.font.name = FONT_FAMILY
    normal_style.font.size = BODY_FONT_SIZE
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Configure first section margins
    s0 = doc.sections[0]
    apply_bit_margins(s0)
    return doc

def apply_bit_margins(section):
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(1.25)
    section.right_margin = Inches(1.0)
    section.header_distance = Inches(0.4)
    section.footer_distance = Inches(0.4)

def set_page_number_type(section, fmt="decimal", start=None):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    pgNumType.set(qn('w:fmt'), fmt)
    if start is not None:
        pgNumType.set(qn('w:start'), str(start))

def add_field(p, field_name):
    run = p.add_run()
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), field_name)
    run._r.append(fldSimple)
    run.font.name = FONT_FAMILY
    run.font.size = Pt(10)
    return run

def configure_footer(footer_obj):
    # Use a 1-row, 3-column borderless table for robust left-center-right footer alignment
    tbl = footer_obj.add_table(1, 3, Inches(6.02))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_l, cell_c, cell_r = tbl.rows[0].cells
    
    # Left
    pl = cell_l.paragraphs[0]
    pl.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pl.paragraph_format.space_after = Pt(0)
    rl = pl.add_run(FOOTER_LEFT)
    rl.font.name = FONT_FAMILY
    rl.font.size = Pt(10)

    # Center
    pc = cell_c.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_after = Pt(0)
    rc = pc.add_run(FOOTER_CENTER)
    rc.font.name = FONT_FAMILY
    rc.font.size = Pt(10)

    # Right
    pr = cell_r.paragraphs[0]
    pr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pr.paragraph_format.space_after = Pt(0)
    add_field(pr, "PAGE")

    # Clear cell borders
    for cell in (cell_l, cell_c, cell_r):
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(r'<w:tcBorders %s><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>' % nsdecls('w'))
        tcPr.append(tcBorders)

def configure_header(header_obj):
    p = header_obj.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(PROJECT_TITLE)
    r.font.name = FONT_FAMILY
    r.font.size = Pt(9.5)
    r.font.italic = True
    r.font.color.rgb = RGBColor(70, 70, 70)

def add_chapter_title_sheet(doc, chapter_num_str, chapter_title_str):
    # A separate chapter title sheet must be inserted before every chapter
    p_num = doc.add_paragraph()
    p_num.paragraph_format.space_before = Pt(200)
    p_num.paragraph_format.space_after = Pt(18)
    p_num.paragraph_format.line_spacing = 1.5
    p_num.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_num = p_num.add_run(chapter_num_str)
    r_num.font.name = FONT_FAMILY
    r_num.font.size = CHAPTER_NUM_SIZE
    r_num.font.bold = True

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(200)
    p_title.paragraph_format.line_spacing = 1.5
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(chapter_title_str.upper())
    r_title.font.name = FONT_FAMILY
    r_title.font.size = CHAPTER_TITLE_SIZE
    r_title.font.bold = True

    doc.add_page_break()

def add_chapter_header_block(doc, chapter_num_str, chapter_title_str):
    # Chapter heading on the first page of chapter content
    p_num = doc.add_paragraph()
    p_num.paragraph_format.space_before = Pt(12)
    p_num.paragraph_format.space_after = Pt(6)
    p_num.paragraph_format.line_spacing = 1.5
    p_num.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_num = p_num.add_run(chapter_num_str)
    r_num.font.name = FONT_FAMILY
    r_num.font.size = CHAPTER_NUM_SIZE
    r_num.font.bold = True

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(18)
    p_title.paragraph_format.line_spacing = 1.5
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(chapter_title_str.upper())
    r_title.font.name = FONT_FAMILY
    r_title.font.size = CHAPTER_TITLE_SIZE
    r_title.font.bold = True

def add_section(doc, heading_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(heading_text)
    r.font.name = FONT_FAMILY
    r.font.size = SECTION_FONT_SIZE
    r.font.bold = True
    return p

def add_subsection(doc, heading_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(heading_text)
    r.font.name = FONT_FAMILY
    r.font.size = SUBSECTION_FONT_SIZE
    r.font.bold = True
    return p

def add_subsubsection(doc, heading_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(heading_text)
    r.font.name = FONT_FAMILY
    r.font.size = Pt(12)
    r.font.bold = True
    return p

def add_body_paragraph(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    r.font.name = FONT_FAMILY
    r.font.size = BODY_FONT_SIZE
    return p

def add_bullet_point(doc, lead_in, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run(lead_in + ": ")
    r1.font.name = FONT_FAMILY
    r1.font.size = BODY_FONT_SIZE
    r1.font.bold = True
    r2 = p.add_run(text)
    r2.font.name = FONT_FAMILY
    r2.font.size = BODY_FONT_SIZE
    return p

def add_table_title(doc, title_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(title_text)
    r.font.name = FONT_FAMILY
    r.font.size = TABLE_TITLE_SIZE
    r.font.bold = True
    return p

def add_figure_caption(doc, caption_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(caption_text)
    r.font.name = FONT_FAMILY
    r.font.size = FIGURE_CAPTION_SIZE
    r.font.italic = True
    return p

def add_image_figure(doc, img_path, caption_text, width_inches=5.8):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(img_path, width=Inches(width_inches))
        add_figure_caption(doc, caption_text)
    else:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"[Figure: {caption_text} - Image file {os.path.basename(img_path)}]")
        r.font.bold = True
        add_figure_caption(doc, caption_text)

def create_styled_table(doc, headers, rows_data, col_widths=None):
    num_cols = len(headers)
    tbl = doc.add_table(rows=1 + len(rows_data), cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Format header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = FONT_FAMILY
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
        # Background color #1E293B (Dark Navy Slate)
        shading = parse_xml(r'<w:shd %s w:fill="1E293B"/>' % nsdecls('w'))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

    # Format data rows
    for r_idx, row in enumerate(rows_data):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_fill = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = FONT_FAMILY
                run.font.size = Pt(9.5)
            # Background shading
            if bg_fill != "FFFFFF":
                shd = parse_xml(r'<w:shd %s w:fill="%s"/>' % (nsdecls('w'), bg_fill))
                row_cells[c_idx]._tc.get_or_add_tcPr().append(shd)

    # Set table borders (thin light gray)
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        r'<w:tblBorders %s>'
        r'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        r'<w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        r'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="A0AEC0"/>'
        r'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        r'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        r'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(borders)

    # Set column widths if provided
    if col_widths and len(col_widths) == num_cols:
        for row in tbl.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl

def add_code_snippet(doc, code_str, caption=None):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(2)
        p_cap.paragraph_format.keep_with_next = True
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = FONT_FAMILY
        r_cap.font.size = Pt(10)
        r_cap.font.bold = True

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.02)
    
    # Border & Shading
    shd = parse_xml(r'<w:shd %s w:fill="F8FAFC"/>' % nsdecls('w'))
    cell._tc.get_or_add_tcPr().append(shd)
    tcBorders = parse_xml(
        r'<w:tcBorders %s>'
        r'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        r'<w:left w:val="single" w:sz="18" w:space="0" w:color="3B82F6"/>'
        r'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        r'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
        r'</w:tcBorders>' % nsdecls('w')
    )
    cell._tc.get_or_add_tcPr().append(tcBorders)

    lines = code_str.strip().split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.1
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_formula_callout(doc, formula_title, formula_text, variable_explanations):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.02)

    shd = parse_xml(r'<w:shd %s w:fill="F1F5F9"/>' % nsdecls('w'))
    cell._tc.get_or_add_tcPr().append(shd)
    tcBorders = parse_xml(
        r'<w:tcBorders %s>'
        r'<w:top w:val="none"/>'
        r'<w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>'
        r'<w:bottom w:val="none"/>'
        r'<w:right w:val="none"/>'
        r'</w:tcBorders>' % nsdecls('w')
    )
    cell._tc.get_or_add_tcPr().append(tcBorders)

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(2)
    p0.paragraph_format.space_after = Pt(2)
    r0 = p0.add_run(formula_title)
    r0.font.name = FONT_FAMILY
    r0.font.size = Pt(10.5)
    r0.font.bold = True

    p1 = cell.add_paragraph()
    p1.paragraph_format.space_before = Pt(2)
    p1.paragraph_format.space_after = Pt(3)
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run(formula_text)
    r1.font.name = "Cambria Math"
    r1.font.size = Pt(11)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(15, 23, 42)

    for var, desc in variable_explanations:
        pv = cell.add_paragraph()
        pv.paragraph_format.space_before = Pt(0)
        pv.paragraph_format.space_after = Pt(1)
        rv1 = pv.add_run(f"  • {var}: ")
        rv1.font.name = FONT_FAMILY
        rv1.font.size = Pt(9.5)
        rv1.font.bold = True
        rv2 = pv.add_run(desc)
        rv2.font.name = FONT_FAMILY
        rv2.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
