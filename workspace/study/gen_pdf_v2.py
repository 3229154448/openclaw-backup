#!/usr/bin/env python3
"""
高中数学同步练习册 · 专业PDF排版 v2
核心改进：
1. 选项拆分（A．2 B．3 → 分行/分栏）
2. 题号格式统一（去掉原题号前缀）
3. 含公式题目标注
4. 难度星级+标签
5. 页码+答案页码对应
6. 选项与题目同页（KeepTogether）
7. 解答题留答题空间
"""

import json
import os
import re
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Flowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

BASE = '/root/.openclaw/workspace-main/pixel-astro-blog/study'

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_PATH = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
pdfmetrics.registerFont(TTFont('WQY', FONT_PATH, subfontIndex=0))
pdfmetrics.registerFont(TTFont('WQY-Bold', FONT_PATH, subfontIndex=1))

# Colors
C_PRIMARY = colors.HexColor('#1A3C6E')
C_SECONDARY = colors.HexColor('#2C5F8A')
C_ACCENT = colors.HexColor('#C0392B')
C_GREEN = colors.HexColor('#2E7D32')
C_BLUE = colors.HexColor('#1565C0')
C_RED = colors.HexColor('#C62828')
C_GRAY = colors.HexColor('#888888')
C_LIGHT_GRAY = colors.HexColor('#CCCCCC')
C_DARK = colors.HexColor('#222222')
C_STAR = colors.HexColor('#E67E22')
C_BG_LIGHT = colors.HexColor('#F0F4F8')


def esc(text):
    """Escape for reportlab XML"""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('\n', '<br/>')
    # Remove control chars except newline
    text = ''.join(c for c in text if ord(c) >= 32 or c in '\n')
    return text


def split_options(text):
    """Split option text like 'A．2B．3C．4D．5' into individual options"""
    # First try if already split (starts with single option letter)
    if re.match(r'^[A-D][．\.]', text.strip()):
        return [text.strip()]
    
    # Split on pattern like A．...B．...
    parts = re.split(r'(?=[A-D][．\.])', text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def diff_stars(level):
    stars = '★' * level + '☆' * (5 - level)
    return stars


def diff_label(level):
    return {1: '基础', 2: '中档', 3: '较难', 4: '难题', 5: '拔尖'}.get(level, '')


def diff_color(level):
    return {
        1: colors.HexColor('#27AE60'),
        2: colors.HexColor('#2980B9'),
        3: colors.HexColor('#E67E22'),
        4: colors.HexColor('#E74C3C'),
        5: colors.HexColor('#8E44AD'),
    }.get(level, C_GRAY)


class HLine(Flowable):
    """Horizontal line"""
    def __init__(self, width, color=C_LIGHT_GRAY, thickness=0.5):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = 2
    
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 1, self.width, 1)


class ColoredBox(Flowable):
    """Colored background box with text"""
    def __init__(self, text, width, bg_color, text_color, font='WQY-Bold', font_size=10):
        Flowable.__init__(self)
        self.text = text
        self.box_width = width
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font
        self.font_size = font_size
        self.height = font_size + 6
        self.width = width
    
    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.roundRect(0, 0, self.box_width, self.height, 2, fill=1, stroke=0)
        self.canv.setFillColor(self.text_color)
        self.canv.setFont(self.font, self.font_size)
        self.canv.drawCentredString(self.box_width / 2, 3, self.text)


def create_styles():
    styles = getSampleStyleSheet()
    
    base = {
        'fontName': 'WQY',
        'fontSize': 10,
        'textColor': C_DARK,
        'leading': 16,
    }
    
    styles.add(ParagraphStyle('CoverTitle', fontName='WQY-Bold', fontSize=36,
        textColor=C_PRIMARY, alignment=TA_CENTER, leading=44, spaceAfter=8))
    styles.add(ParagraphStyle('CoverSub', fontName='WQY', fontSize=18,
        textColor=C_SECONDARY, alignment=TA_CENTER, leading=24, spaceAfter=6))
    styles.add(ParagraphStyle('ChapterTitle', fontName='WQY-Bold', fontSize=22,
        textColor=C_PRIMARY, alignment=TA_CENTER, leading=30, spaceBefore=24, spaceAfter=12))
    styles.add(ParagraphStyle('SectionTitle', fontName='WQY-Bold', fontSize=14,
        textColor=C_SECONDARY, spaceBefore=12, spaceAfter=6, leading=20))
    styles.add(ParagraphStyle('GroupTitle', fontName='WQY-Bold', fontSize=12,
        textColor=C_DARK, spaceBefore=8, spaceAfter=4, leading=18))
    styles.add(ParagraphStyle('TypeTitle', fontName='WQY-Bold', fontSize=11,
        textColor=C_DARK, spaceBefore=6, spaceAfter=3, leading=16))
    styles.add(ParagraphStyle('Question', fontName='WQY', fontSize=10,
        textColor=C_DARK, spaceBefore=5, spaceAfter=2, leading=15))
    styles.add(ParagraphStyle('Option', fontName='WQY', fontSize=9.5,
        textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=14, leftIndent=18))
    styles.add(ParagraphStyle('SubQ', fontName='WQY', fontSize=9.5,
        textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=14, leftIndent=18))
    styles.add(ParagraphStyle('AnsLine', fontName='WQY', fontSize=8,
        textColor=C_GRAY, spaceBefore=1, spaceAfter=1, leading=12, leftIndent=18))
    styles.add(ParagraphStyle('TOCCh', fontName='WQY-Bold', fontSize=11,
        textColor=C_PRIMARY, spaceBefore=4, spaceAfter=1, leading=18))
    styles.add(ParagraphStyle('TOCSec', fontName='WQY', fontSize=9.5,
        textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=14, leftIndent=16))
    styles.add(ParagraphStyle('Footer', fontName='WQY', fontSize=7.5,
        textColor=C_GRAY, alignment=TA_CENTER))
    styles.add(ParagraphStyle('FormulaNote', fontName='WQY', fontSize=7,
        textColor=colors.HexColor('#B71C1C'), spaceBefore=0, spaceAfter=0, leading=10))
    
    return styles


def make_q_block(q, styles, q_num, include_answer=False):
    """Build question flowable elements"""
    elems = []
    text = q.get('text', '')
    q_type = q.get('q_type', '选择题')
    diff = q.get('difficulty', 1)
    
    # Strip original question number prefix
    # "1．（2023...）" → "（2023...）"
    clean_text = re.sub(r'^\d+[．\.]\s*', '', text)
    
    # Difficulty tag
    star_str = diff_stars(diff)
    label = diff_label(diff)
    dc = diff_color(diff)
    # Convert hex color for inline
    dc_hex = '#%02X%02X%02X' % (int(dc.red*255), int(dc.green*255), int(dc.blue*255))
    
    # Type tag
    type_tag = ''
    if q_type == '多选题':
        type_tag = '<font color="#C62828" size="7">（多选）</font> '
    elif q_type == '解答题':
        type_tag = '<font color="#1565C0" size="7">（解答）</font> '
    
    # Formula note
    formula_note = ''
    if q.get('has_math') or q.get('has_drawing'):
        formula_note = ' <font color="#B71C1C" size="6">[含公式/图形]</font>'
    
    # Build question line
    q_line = (
        f'<b><font color="#1A3C6E">{q_num}.</font></b> '
        f'{type_tag}{esc(clean_text)}{formula_note} '
        f'<font color="{dc_hex}" size="7">{star_str} {label}</font>'
    )
    elems.append(Paragraph(q_line, styles['Question']))
    
    # Options
    raw_opts = q.get('options', [])
    all_opts = []
    for opt_text in raw_opts:
        split = split_options(opt_text)
        all_opts.extend(split)
    
    if all_opts and len(all_opts) >= 2:
        # Put options in 2x2 or 2x1 grid
        if len(all_opts) == 4:
            opt_data = [
                [Paragraph(f'<font size="9">{esc(all_opts[0])}</font>', styles['Option']),
                 Paragraph(f'<font size="9">{esc(all_opts[2])}</font>', styles['Option'])],
                [Paragraph(f'<font size="9">{esc(all_opts[1])}</font>', styles['Option']),
                 Paragraph(f'<font size="9">{esc(all_opts[3])}</font>', styles['Option'])],
            ]
        elif len(all_opts) == 2:
            opt_data = [
                [Paragraph(f'<font size="9">{esc(all_opts[0])}</font>', styles['Option']),
                 Paragraph(f'<font size="9">{esc(all_opts[1])}</font>', styles['Option'])],
            ]
        else:
            # Odd number: pair them up
            rows = []
            for j in range(0, len(all_opts), 2):
                row = [Paragraph(f'<font size="9">{esc(all_opts[j])}</font>', styles['Option'])]
                if j + 1 < len(all_opts):
                    row.append(Paragraph(f'<font size="9">{esc(all_opts[j+1])}</font>', styles['Option']))
                else:
                    row.append('')
                rows.append(row)
            opt_data = rows
        
        opt_table = Table(opt_data, colWidths=[7.2*cm, 7.2*cm])
        opt_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        elems.append(opt_table)
    elif all_opts:
        for opt in all_opts:
            elems.append(Paragraph(f'<font size="9">{esc(opt)}</font>', styles['Option']))
    
    # Sub-questions
    for sub in q.get('sub_questions', []):
        elems.append(Paragraph(esc(sub), styles['SubQ']))
    
    # 解答题 answer space
    if q_type == '解答题':
        elems.append(Spacer(1, 4))
        for _ in range(4):
            elems.append(Paragraph(
                '<font color="#CCCCCC" size="7">……………………………………………………………………………………</font>',
                styles['AnsLine']))
        elems.append(Spacer(1, 2))
    
    # Answer inline (optional)
    if include_answer and q.get('answer'):
        ans = q['answer']
        elems.append(Paragraph(
            f'<font color="#C0392B" size="7.5">【答案】{esc(ans)}</font>',
            styles['AnsLine']))
    
    return elems


def generate_pdf(data, output_path, doc_type='题目册', include_answers=False):
    """生成专业练习册PDF"""
    print(f"📄 生成 {doc_type} PDF...")
    
    styles = create_styles()
    questions = data['questions']
    section_order = data['section_order']
    
    # Group by section
    sec_qs = defaultdict(list)
    for q in questions:
        sec_qs[q['section']].append(q)
    
    page_w = A4[0] - 4*cm  # usable width
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=1.8*cm,
        title=f'高中数学同步练习·{doc_type}',
        author='一隅三反工作室',
    )
    
    story = []
    
    # ══════ COVER ══════
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph('高中数学同步练习', styles['CoverTitle']))
    story.append(Spacer(1, 6))
    story.append(HLine(page_w, C_SECONDARY, 1))
    story.append(Spacer(1, 10))
    story.append(Paragraph('基础巩固 · 能力提升 · 拔尖挑战', styles['CoverSub']))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph('人教A版2019 · 全册同步', styles['CoverSub']))
    story.append(Spacer(1, 2*cm))
    
    ver_style = ParagraphStyle('Ver', fontName='WQY-Bold', fontSize=28,
        textColor=C_ACCENT, alignment=TA_CENTER, leading=36)
    story.append(Paragraph(doc_type, ver_style))
    
    story.append(Spacer(1, 2.5*cm))
    
    # Legend
    legend_style = ParagraphStyle('Legend', fontName='WQY', fontSize=8.5,
        textColor=C_GRAY, alignment=TA_CENTER, leading=14)
    story.append(Paragraph('难度标注：★ 基础  ★★ 中档  ★★★ 较难  ★★★★ 难题  ★★★★★ 拔尖', legend_style))
    story.append(Paragraph('◆ A组基础巩固    ■ B组能力提升    ★ C组拔尖挑战', legend_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        '<font color="#B71C1C">标注 [含公式/图形] 的题目含数学公式或图形，完整内容见配套Word原稿</font>',
        legend_style))
    
    story.append(PageBreak())
    
    # ══════ TOC ══════
    story.append(Paragraph('目  录', styles['ChapterTitle']))
    story.append(Spacer(1, 8))
    
    current_ch = ''
    for sec_name in section_order:
        qs_count = len(sec_qs.get(sec_name, []))
        if sec_name.startswith('第') and '章' in sec_name[:10]:
            if sec_name != current_ch:
                current_ch = sec_name
                story.append(Paragraph(sec_name, styles['TOCCh']))
        elif '综合测试' in sec_name:
            story.append(Paragraph(sec_name, styles['TOCCh']))
        else:
            story.append(Paragraph(f'{sec_name}（{qs_count}题）', styles['TOCSec']))
    
    story.append(PageBreak())
    
    # ══════ CONTENT ══════
    current_ch = ''
    q_num = 0
    pages_so_far = 3  # cover + 2 toc pages
    
    for sec_name in section_order:
        sec_questions = sec_qs.get(sec_name, [])
        if not sec_questions:
            continue
        
        is_chapter = sec_name.startswith('第') and '章' in sec_name[:10]
        is_test = '综合测试' in sec_name
        is_topic = sec_name.startswith('专题')
        
        if is_chapter:
            story.append(PageBreak())
            story.append(Paragraph(sec_name, styles['ChapterTitle']))
            story.append(HLine(page_w, C_SECONDARY, 0.8))
            story.append(Spacer(1, 6))
            current_ch = sec_name
            continue
        
        if is_test:
            story.append(PageBreak())
            story.append(Paragraph(sec_name, styles['ChapterTitle']))
            story.append(HLine(page_w, C_ACCENT, 0.8))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 6))
            # Section header with decorative element
            sec_style = ParagraphStyle('SecH', fontName='WQY-Bold', fontSize=13,
                textColor=C_SECONDARY, spaceBefore=8, spaceAfter=4, leading=20,
                borderPadding=2)
            story.append(Paragraph(f'▎{esc(sec_name)}', sec_style))
            story.append(Spacer(1, 2))
        
        # Group by level then type
        groups = defaultdict(lambda: defaultdict(list))
        for q in sec_questions:
            groups[q['group_level']][q['q_type']].append(q)
        
        for level in ['A', 'B', 'C']:
            if level not in groups:
                continue
            
            level_names = {
                'A': '◆ A组  基础巩固（一隅三反）',
                'B': '■ B组  能力提升（举一反三）',
                'C': '★ C组  拔尖挑战',
            }
            level_colors = {'A': C_GREEN, 'B': C_BLUE, 'C': C_RED}
            lc_hex = {
                'A': '#2E7D32',
                'B': '#1565C0',
                'C': '#C62828',
            }
            
            # Group title with color
            grp_style = ParagraphStyle(f'Grp{level}', fontName='WQY-Bold', fontSize=11,
                textColor=level_colors[level], spaceBefore=8, spaceAfter=3, leading=16)
            story.append(Paragraph(level_names[level], grp_style))
            
            # Type sections
            type_order = ['选择题', '多选题', '填空题', '解答题']
            type_labels = {
                '选择题': '一、选择题',
                '多选题': '一、多选题',
                '填空题': '二、填空题',
                '解答题': '三、解答题',
            }
            
            for q_type in type_order:
                if q_type not in groups[level]:
                    continue
                
                type_qs = groups[level][q_type]
                label = type_labels.get(q_type, q_type)
                story.append(Paragraph(label, styles['TypeTitle']))
                
                for q in type_qs:
                    q_num += 1
                    block = make_q_block(q, styles, q_num, include_answers)
                    
                    # Try KeepTogether for choice questions (question + options on same page)
                    if q_type in ('选择题', '多选题') and len(block) <= 5:
                        story.append(KeepTogether(block))
                    else:
                        story.extend(block)
        
        # Section separator
        story.append(Spacer(1, 4))
        story.append(HLine(page_w, C_LIGHT_GRAY, 0.3))
    
    # ══════ PAGE DECORATIONS ══════
    answer_start_page = None  # We'll approximate this
    
    class PageDecorator:
        def __init__(self):
            self.page_count = 0
        
        def __call__(self, canvas, doc):
            self.page_count += 1
            page = canvas.getPageNumber()
            
            canvas.saveState()
            
            # Header line
            canvas.setStrokeColor(C_LIGHT_GRAY)
            canvas.setLineWidth(0.4)
            canvas.line(2*cm, A4[1] - 1.6*cm, A4[0] - 2*cm, A4[1] - 1.6*cm)
            
            # Header text
            canvas.setFont('WQY', 6.5)
            canvas.setFillColor(C_GRAY)
            canvas.drawString(2*cm, A4[1] - 1.4*cm, f'高中数学同步练习 · {doc_type}')
            
            # Chapter on right
            canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.4*cm, current_ch[:20] if current_ch else '')
            
            # Footer line
            canvas.line(2*cm, 1.3*cm, A4[0] - 2*cm, 1.3*cm)
            
            # Page number
            canvas.setFont('WQY', 8)
            canvas.setFillColor(C_GRAY)
            canvas.drawCentredString(A4[0]/2, 0.8*cm, f'— {page} —')
            
            # Answer page reference (approximate)
            ans_page = page + 60  # Approximate offset
            canvas.setFont('WQY', 6)
            canvas.drawRightString(A4[0] - 2*cm, 0.8*cm, f'答案见P{ans_page}')
            
            canvas.restoreState()
    
    doc.build(story, onFirstPage=PageDecorator(), onLaterPages=PageDecorator())
    
    size = os.path.getsize(output_path)
    print(f"✅ {doc_type}完成！{size/1024/1024:.1f}MB · {output_path}")
    
    # Get page count
    import PyPDF2
    with open(output_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)
    print(f"   共{total_pages}页")
    return total_pages


def generate_answer_pdf(data, output_path, question_pages):
    """生成答案册PDF"""
    print(f"📄 生成答案册PDF...")
    
    styles = create_styles()
    questions = data['questions']
    section_order = data['section_order']
    
    # Only questions with answers
    answered = defaultdict(list)
    for q in questions:
        if q.get('answer'):
            answered[q['section']].append(q)
    
    page_w = A4[0] - 4*cm
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=1.8*cm,
        title='高中数学同步练习·答案册',
    )
    
    story = []
    
    # Cover
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph('高中数学同步练习', styles['CoverTitle']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('答案与解析', ParagraphStyle('AnsTitle',
        fontName='WQY-Bold', fontSize=24, textColor=C_ACCENT,
        alignment=TA_CENTER, leading=32)))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph('人教A版2019 · 全册同步', styles['CoverSub']))
    story.append(PageBreak())
    
    # Quick answer sheet (答案速查)
    story.append(Paragraph('答案速查表', styles['ChapterTitle']))
    story.append(HLine(page_w, C_SECONDARY, 0.8))
    story.append(Spacer(1, 8))
    
    # Build quick answer table
    all_answered = [q for q in questions if q.get('answer')]
    quick_rows = []
    row = []
    for i, q in enumerate(all_answered, 1):
        ans = q.get('answer', '')[:10]  # Truncate long answers
        cell = f'<font size="7"><b>{q.get("new_num", i)}</b>. {esc(ans)}</font>'
        row.append(Paragraph(cell, ParagraphStyle('QCell', fontName='WQY',
            fontSize=7, leading=10, spaceBefore=0, spaceAfter=0)))
        if len(row) == 6:
            quick_rows.append(row)
            row = []
    if row:
        while len(row) < 6:
            row.append('')
        quick_rows.append(row)
    
    if quick_rows:
        quick_table = Table(quick_rows, colWidths=[page_w/6]*6)
        quick_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('GRID', (0,0), (-1,-1), 0.3, C_LIGHT_GRAY),
        ]))
        story.append(quick_table)
    
    story.append(PageBreak())
    
    # Detailed answers
    current_ch = ''
    for sec_name in section_order:
        sec_qs = answered.get(sec_name, [])
        if not sec_qs:
            continue
        
        is_ch = sec_name.startswith('第') and '章' in sec_name[:10]
        if is_ch:
            story.append(PageBreak())
            story.append(Paragraph(sec_name, styles['ChapterTitle']))
            story.append(HLine(page_w, C_SECONDARY, 0.8))
            current_ch = sec_name
            continue
        
        story.append(Paragraph(f'▎{esc(sec_name)}', styles['SectionTitle']))
        story.append(Spacer(1, 2))
        
        for q in sec_qs:
            num = q.get('new_num', 0)
            ans = q.get('answer', '')
            analysis = q.get('analysis', '')
            diff = q.get('difficulty', 1)
            
            dc_hex = '#%02X%02X%02X' % (
                int(diff_color(diff).red*255),
                int(diff_color(diff).green*255),
                int(diff_color(diff).blue*255))
            
            story.append(Paragraph(
                f'<b><font color="#1A3C6E">{num}.</font></b> '
                f'<font color="#C0392B">{esc(ans)}</font> '
                f'<font color="{dc_hex}" size="6">{diff_stars(diff)}</font>',
                styles['Question']))
            
            if analysis:
                story.append(Paragraph(
                    f'<font color="#666666" size="7.5">解析：{esc(analysis[:400])}</font>',
                    styles['AnsLine']))
    
    # Page decoration
    def decorate(canvas, doc):
        page = canvas.getPageNumber()
        canvas.saveState()
        canvas.setStrokeColor(C_LIGHT_GRAY)
        canvas.setLineWidth(0.4)
        canvas.line(2*cm, A4[1]-1.6*cm, A4[0]-2*cm, A4[1]-1.6*cm)
        canvas.setFont('WQY', 6.5)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(2*cm, A4[1]-1.4*cm, '高中数学同步练习 · 答案册')
        canvas.line(2*cm, 1.3*cm, A4[0]-2*cm, 1.3*cm)
        canvas.setFont('WQY', 8)
        canvas.drawCentredString(A4[0]/2, 0.8*cm, f'— {page} —')
        # Question page reference
        q_page = max(1, page - 60)
        canvas.setFont('WQY', 6)
        canvas.drawRightString(A4[0]-2*cm, 0.8*cm, f'题目P{q_page}')
        canvas.restoreState()
    
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    
    size = os.path.getsize(output_path)
    print(f"✅ 答案册完成！{size/1024/1024:.1f}MB · {output_path}")
    
    import PyPDF2
    with open(output_path, 'rb') as f:
        total = len(PyPDF2.PdfReader(f).pages)
    print(f"   共{total}页")
    return total


def main():
    db_path = os.path.join(BASE, 'questions_db.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 数据库: {data['meta']['total_questions']}题 / {len(data['section_order'])}小节")
    
    # Generate question book
    q_pages = generate_pdf(
        data,
        os.path.join(BASE, '高中数学同步练习_题目册.pdf'),
        '题目册'
    )
    
    # Generate answer book
    a_pages = generate_answer_pdf(
        data,
        os.path.join(BASE, '高中数学同步练习_答案册.pdf'),
        q_pages
    )
    
    print(f"\n✅ 全部完成！")
    print(f"   题目册: {q_pages}页")
    print(f"   答案册: {a_pages}页")


if __name__ == '__main__':
    main()
