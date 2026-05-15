#!/usr/bin/env python3
"""
高中数学同步练习册 · 印刷级PDF排版 v3
参照市面练习册风格：53天天练/一遍过/必刷题
OMML公式完整转Unicode数学文本
从预处理JSON读取，快速生成PDF
"""
import os, re, sys, json
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = '/root/.openclaw/workspace-main/pixel-astro-blog/study'

# 字体注册
FONT_PATH = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
pdfmetrics.registerFont(TTFont('WQY', FONT_PATH, subfontIndex=0))
pdfmetrics.registerFont(TTFont('WQY-Bold', FONT_PATH, subfontIndex=1))

# ============ 配色 ============
C_PRIMARY = colors.HexColor('#1A3C6E')
C_SECONDARY = colors.HexColor('#2C5F8A')
C_ACCENT = colors.HexColor('#C0392B')
C_GREEN = colors.HexColor('#2E7D32')
C_BLUE = colors.HexColor('#1565C0')
C_RED = colors.HexColor('#C62828')
C_DARK = colors.HexColor('#222222')
C_GRAY = colors.HexColor('#888888')
C_LIGHT_GRAY = colors.HexColor('#CCCCCC')

# ============ 正则 ============
SEC_PAT = re.compile(r'^(\d+\.\d+)\s+.*（精练）')
TOPIC_PAT = re.compile(r'^专题(\d+\.\d+)\s+(.*)')
TEST_PAT = re.compile(r'.*综合测试卷')
CH_PAT = re.compile(r'^第[一二三四五六七八九十]+章')
KP_PAT = re.compile(r'^【知识点\d+\s+(.*)】')
QTYPE_PAT = re.compile(r'^【(题型|类型)\d+\s+(.*)】')
EXAMPLE_PAT = re.compile(r'^【例\d+】(.*)')
VARIANT_PAT = re.compile(r'^【变式(\d+)-(\d+)】(.*)')
NOTE_PAT = re.compile(r'^【注】')
SOLUTION_PAT = re.compile(r'^【(解题思路|解答过程)】\s*(.*)')
ANSWER_PAT = re.compile(r'^【答案】\s*(.*)')
ANALYSIS_PAT = re.compile(r'^【解析】\s*(.*)')
BOOK_HDR = re.compile(r'^【人教A版')
Q_NUM_PAT = re.compile(r'^(\d+)[．\.]')
OPT_PAT = re.compile(r'^[A-D][．\.]')
TYPE_HDR = re.compile(r'^[一二三四五六七八九十]+[．.]\s*(选择题|多选题|填空题|解答题)')
GRP_PAT = re.compile(r'^([ABC])组')

# ============ 工具函数 ============
def esc(text):
    t = str(text).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('\n','<br/>')
    return ''.join(c for c in t if ord(c) >= 32 or c in '\n')

def hex_c(c):
    return '#%02X%02X%02X' % (int(c.red*255), int(c.green*255), int(c.blue*255))

def split_opts(text):
    parts = re.split(r'(?=[A-D][．\.])', text)
    return [p.strip() for p in parts if p.strip()]

def classify(text, in_topic=False, is_ans=False):
    if not text:
        return 'empty'
    # 综合测试优先匹配（否则被chapter拦截）
    if TEST_PAT.match(text):
        return 'test'
    if CH_PAT.match(text):
        return 'chapter'
    if SEC_PAT.match(text):
        return 'section'
    if TOPIC_PAT.match(text):
        return 'topic'
    if TEST_PAT.match(text):
        return 'test'
    if GRP_PAT.match(text):
        return 'group'
    if TYPE_HDR.match(text):
        return 'type_header'
    # 答案/解析（不论是否在topic内）
    if ANSWER_PAT.match(text):
        return 'answer'
    if ANALYSIS_PAT.match(text):
        return 'analysis'
    if SOLUTION_PAT.match(text):
        return 'solution'
    if in_topic:
        if KP_PAT.match(text):
            return 'kp_header'
        if QTYPE_PAT.match(text):
            return 'qtype_tag'
        if EXAMPLE_PAT.match(text):
            return 'example'
        if VARIANT_PAT.match(text):
            return 'variant'
        if NOTE_PAT.match(text):
            return 'note'
        if BOOK_HDR.match(text):
            return 'book_header'
    # 答案册模式：识别题号和标签
    if is_ans:
        if Q_NUM_PAT.match(text) and len(text) > 2:
            return 'question'
        if EXAMPLE_PAT.match(text):
            return 'example'
        if VARIANT_PAT.match(text):
            return 'variant'
    if Q_NUM_PAT.match(text) and len(text) > 2:
        return 'question'
    if OPT_PAT.match(text) and len(text) < 80:
        return 'option'
    if re.match(r'^（\d+）', text):
        return 'sub_question'
    return 'text'

# ============ 提取结构化数据 ============
def extract_sections(json_path, is_answer=False):
    print(f"📖 提取: {os.path.basename(json_path)}")
    with open(json_path, 'r', encoding='utf-8') as f:
        paras = json.load(f)
    
    sections = []
    cur = None
    cur_q = None
    cur_kp = None
    cur_qt = None
    in_topic = False
    
    for p in paras:
        text = p['t'].strip()
        if not text:
            continue
        pt = classify(text, in_topic, is_answer)
        
        if pt == 'section':
            if cur:
                sections.append(cur)
            m = SEC_PAT.match(text)
            cur = {'kind': 'practice', 'title': text, 'num': m.group(1) if m else '', 'questions': []}
            in_topic = False
            cur_q = None
            continue
        
        if pt == 'topic':
            if cur:
                # 保存当前专题的残留数据
                if cur['kind'] == 'topic':
                    if cur_kp:
                        cur.setdefault('knowledge_points', []).append(cur_kp)
                        cur_kp = None
                    if cur_qt:
                        cur.setdefault('question_types', []).append(cur_qt)
                        cur_qt = None
                sections.append(cur)
            m = TOPIC_PAT.match(text)
            cur = {'kind': 'topic', 'title': text, 'num': m.group(1) if m else '',
                   'knowledge_points': [], 'question_types': []}
            in_topic = True
            cur_q = None
            continue
        
        if pt == 'test':
            if cur:
                sections.append(cur)
            cur = {'kind': 'test', 'title': text, 'questions': []}
            in_topic = False
            cur_q = None
            continue
        
        if pt in ('chapter', 'group', 'type_header', 'book_header'):
            continue
        
        # ---- 专题内部 ----
        if in_topic:
            if pt == 'kp_header':
                if cur_kp:
                    cur.setdefault('knowledge_points', []).append(cur_kp)
                m = KP_PAT.match(text)
                cur_kp = {'name': m.group(1).strip() if m else text, 'content': []}
                cur_q = None
                continue
            
            if pt == 'qtype_tag':
                if cur_kp:
                    cur.setdefault('knowledge_points', []).append(cur_kp)
                    cur_kp = None
                if cur_qt:
                    cur.setdefault('question_types', []).append(cur_qt)
                m = QTYPE_PAT.match(text)
                cur_qt = {'kind': m.group(1) if m else '', 'name': m.group(2).strip() if m else text, 'questions': []}
                cur_q = None
                continue
            
            if pt == 'example':
                cur_q = {'role': 'example', 'text': text, 'options': [], 'sub_questions': [], 'solution': {}}
                if cur_qt:
                    cur_qt['questions'].append(cur_q)
                continue
            
            if pt == 'variant':
                cur_q = {'role': 'variant', 'text': text, 'options': [], 'sub_questions': [], 'solution': {}}
                if cur_qt:
                    cur_qt['questions'].append(cur_q)
                continue
            
            # 答案/解析/解题思路/解答过程 → 归入当前题目
            if pt == 'answer' and is_answer and cur_q:
                m = ANSWER_PAT.match(text)
                if m:
                    cur_q['solution']['答案'] = m.group(1)
                continue
            if pt == 'analysis' and is_answer and cur_q:
                m = ANALYSIS_PAT.match(text)
                if m:
                    cur_q['solution']['解析'] = m.group(1)
                continue
            if pt == 'solution' and is_answer and cur_q:
                m = SOLUTION_PAT.match(text)
                if m:
                    cur_q['solution'][m.group(1)] = m.group(2)
                continue
            
            if pt == 'option' and cur_q:
                cur_q['options'].extend(split_opts(text))
                continue
            if pt == 'sub_question' and cur_q:
                cur_q['sub_questions'].append(text)
                continue
            if pt == 'question' and cur_qt:
                cur_q = {'role': 'numbered', 'text': text, 'options': [], 'sub_questions': [], 'solution': {}}
                cur_qt['questions'].append(cur_q)
                continue
            if pt == 'note' and cur_kp is not None:
                cur_kp['content'].append(text)
                continue
            if pt == 'text' and cur_kp is not None and cur_qt is None:
                cur_kp['content'].append(text)
                continue
            continue
        
        # ---- 精练/测试 ----
        if pt == 'question' and cur:
            cur_q = {'role': 'practice', 'text': text, 'options': [], 'sub_questions': [], 'solution': {}}
            cur['questions'].append(cur_q)
            continue
        if pt == 'answer' and is_answer and cur_q:
            m = ANSWER_PAT.match(text)
            if m:
                cur_q['solution']['答案'] = m.group(1)
            continue
        if pt == 'analysis' and is_answer and cur_q:
            m = ANALYSIS_PAT.match(text)
            if m:
                cur_q['solution']['解析'] = m.group(1)
            continue
        if pt == 'solution' and is_answer and cur_q:
            m = SOLUTION_PAT.match(text)
            if m:
                cur_q['solution'][m.group(1)] = m.group(2)
            continue
        if pt == 'option' and cur_q:
            cur_q['options'].extend(split_opts(text))
            continue
        if pt == 'sub_question' and cur_q:
            cur_q['sub_questions'].append(text)
            continue
    
    # 收尾
    if cur:
        if cur['kind'] == 'topic':
            if cur_kp:
                cur.setdefault('knowledge_points', []).append(cur_kp)
            if cur_qt:
                cur.setdefault('question_types', []).append(cur_qt)
        sections.append(cur)
    
    p_t = sum(len(s.get('questions', [])) for s in sections if s['kind'] in ('practice', 'test'))
    t_t = sum(len(qt.get('questions', [])) for s in sections if s['kind'] == 'topic' for qt in s.get('question_types', []))
    print(f"  精练:{len([s for s in sections if s['kind']=='practice'])}节/{p_t}题  "
          f"专题:{len([s for s in sections if s['kind']=='topic'])}个/{t_t}题  "
          f"测试:{len([s for s in sections if s['kind']=='test'])}个")
    
    # 统计答案覆盖率
    if is_answer:
        total_q = 0
        has_ans = 0
        for s in sections:
            for q in s.get('questions', []):
                total_q += 1
                if q.get('solution'):
                    has_ans += 1
            for qt in s.get('question_types', []):
                for q in qt.get('questions', []):
                    total_q += 1
                    if q.get('solution'):
                        has_ans += 1
        print(f"  答案覆盖: {has_ans}/{total_q} ({has_ans*100//max(total_q,1)}%)")
    
    return sections

# ============ 自定义Flowable ============
class HLine(Flowable):
    def __init__(self, w, c=C_LIGHT_GRAY, t=0.5):
        Flowable.__init__(self)
        self.width = w
        self.color = c
        self.thickness = t
        self.height = 2
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 1, self.width, 1)

class DecoBox(Flowable):
    """左侧装饰条的知识点/题型框"""
    def __init__(self, text, color=C_PRIMARY, font_size=10, width=14*cm):
        Flowable.__init__(self)
        self._text = text
        self._color = color
        self._fs = font_size
        self._width = width
        self.height = font_size + 8
        self.width = width
    def draw(self):
        c = self.canv
        # 左侧装饰条
        c.setFillColor(self._color)
        c.rect(0, 0, 3, self.height, fill=1, stroke=0)
        # 文字
        c.setFont('WQY-Bold', self._fs)
        c.setFillColor(self._color)
        c.drawString(8, 4, self._text)

class AnsSpace(Flowable):
    def __init__(self, lines=4, w=14*cm):
        Flowable.__init__(self)
        self.sw = w
        self.lc = lines
        self.height = lines * 18
        self.width = w
    def draw(self):
        self.canv.setStrokeColor(C_LIGHT_GRAY)
        self.canv.setLineWidth(0.3)
        self.canv.setDash(3, 3)
        for i in range(self.lc):
            y = self.height - (i + 1) * 18
            self.canv.line(0, y, self.sw, y)

# ============ 样式 ============
def make_styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle('CoverTitle', fontName='WQY-Bold', fontSize=32,
                          textColor=C_PRIMARY, alignment=TA_CENTER, leading=42, spaceAfter=8))
    ss.add(ParagraphStyle('CoverSub', fontName='WQY', fontSize=16,
                          textColor=C_SECONDARY, alignment=TA_CENTER, leading=22, spaceAfter=6))
    ss.add(ParagraphStyle('CoverVer', fontName='WQY-Bold', fontSize=22,
                          textColor=C_ACCENT, alignment=TA_CENTER, leading=30))
    ss.add(ParagraphStyle('ChTitle', fontName='WQY-Bold', fontSize=18,
                          textColor=C_PRIMARY, alignment=TA_CENTER, leading=26, spaceBefore=20, spaceAfter=8))
    ss.add(ParagraphStyle('SecTitle', fontName='WQY-Bold', fontSize=13,
                          textColor=C_SECONDARY, spaceBefore=14, spaceAfter=4, leading=18))
    ss.add(ParagraphStyle('TopTitle', fontName='WQY-Bold', fontSize=13,
                          textColor=C_SECONDARY, spaceBefore=14, spaceAfter=4, leading=18))
    ss.add(ParagraphStyle('TypeH', fontName='WQY-Bold', fontSize=10,
                          textColor=C_DARK, spaceBefore=6, spaceAfter=2, leading=15))
    ss.add(ParagraphStyle('KPH', fontName='WQY-Bold', fontSize=10,
                          textColor=C_PRIMARY, spaceBefore=8, spaceAfter=2, leading=15))
    ss.add(ParagraphStyle('QTT', fontName='WQY-Bold', fontSize=10,
                          textColor=C_DARK, spaceBefore=8, spaceAfter=2, leading=15))
    ss.add(ParagraphStyle('KPTxt', fontName='WQY', fontSize=8.5,
                          textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=13, leftIndent=8))
    ss.add(ParagraphStyle('Q', fontName='WQY', fontSize=10,
                          textColor=C_DARK, spaceBefore=4, spaceAfter=1, leading=15))
    ss.add(ParagraphStyle('Opt', fontName='WQY', fontSize=9.5,
                          textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=13, leftIndent=14))
    ss.add(ParagraphStyle('SubQ', fontName='WQY', fontSize=9.5,
                          textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=13, leftIndent=14))
    ss.add(ParagraphStyle('Ans', fontName='WQY', fontSize=8,
                          textColor=C_GRAY, spaceBefore=1, spaceAfter=1, leading=11, leftIndent=14))
    ss.add(ParagraphStyle('Legend', fontName='WQY', fontSize=8,
                          textColor=C_GRAY, alignment=TA_CENTER, leading=12))
    return ss

# ============ 题目渲染 ============
def make_q_block(q, styles, q_num, is_ans=False):
    elems = []
    text = q.get('text', '')
    role = q.get('role', 'practice')
    
    # 答案册模式：只显示题号+答案+解析
    if is_ans:
        # 提取题号或标签
        if role in ('example', 'variant'):
            if role == 'example':
                m = EXAMPLE_PAT.match(text)
                tag = f'【例】'
                ct = m.group(1).strip() if m else ''
            else:
                m = VARIANT_PAT.match(text)
                tag = f'【变式{m.group(1)}-{m.group(2)}】'
                ct = m.group(3).strip() if m else ''
            elems.append(Paragraph(f'{tag}', styles['Q']))
        else:
            m = Q_NUM_PAT.match(text)
            num = m.group(1) if m else str(q_num)
            ct = re.sub(r'^\d+[．\.]\s*', '', text)
            # 多选题标记
            mt = '<font color="#C62828" size="7">（多选）</font> ' if '多选' in text else ''
            elems.append(Paragraph(
                f'<b><font color="{hex_c(C_PRIMARY)}">{num}.</font></b> {mt}{esc(ct)}',
                styles['Q']))
        
        # 答案册：只显示解题思路、解答过程、答案、解析
        if q.get('solution'):
            sol = q['solution']
            # 优先显示解题思路和解答过程
            for kind, content in sol.items():
                if content:
                    lb = {'解题思路': '【解题思路】', '解答过程': '【解答过程】',
                          '答案': '【答案】', '解析': '【解析】'}.get(kind, kind)
                    ct = esc(content)
                    elems.append(Paragraph(
                        f'<font color="{hex_c(C_ACCENT)}" size="8"><b>{lb}</b></font> '
                        f'<font color="#555" size="8">{ct}</font>',
                        styles['Ans']))
        return elems
    
    # 题目册模式：显示完整题目
    if role in ('example', 'variant'):
        if role == 'example':
            m = EXAMPLE_PAT.match(text)
            tag = f'<b><font color="{hex_c(C_PRIMARY)}">【例】</font></b> '
            ct = m.group(1).strip() if m else text
        else:
            m = VARIANT_PAT.match(text)
            tag = f'<b><font color="{hex_c(C_BLUE)}">【变式{m.group(1)}-{m.group(2)}】</font></b> '
            ct = m.group(3).strip() if m else text
        elems.append(Paragraph(f'{tag}{esc(ct)}', styles['Q']))
    else:
        m = Q_NUM_PAT.match(text)
        num = m.group(1) if m else str(q_num)
        ct = re.sub(r'^\d+[．\.]\s*', '', text)
        # 多选题标记
        mt = '<font color="#C62828" size="7">（多选）</font> ' if '多选' in text else ''
        elems.append(Paragraph(
            f'<b><font color="{hex_c(C_PRIMARY)}">{num}.</font></b> {mt}{esc(ct)}',
            styles['Q']))
    
    # 选项2x2网格
    opts = q.get('options', [])
    if len(opts) >= 2:
        if len(opts) == 4:
            od = [[Paragraph(f'<font size="9">{esc(opts[0])}</font>', styles['Opt']),
                   Paragraph(f'<font size="9">{esc(opts[2])}</font>', styles['Opt'])],
                  [Paragraph(f'<font size="9">{esc(opts[1])}</font>', styles['Opt']),
                   Paragraph(f'<font size="9">{esc(opts[3])}</font>', styles['Opt'])]]
        elif len(opts) == 2:
            od = [[Paragraph(f'<font size="9">{esc(opts[0])}</font>', styles['Opt']),
                   Paragraph(f'<font size="9">{esc(opts[1])}</font>', styles['Opt'])]]
        else:
            od = []
            for j in range(0, len(opts), 2):
                r = [Paragraph(f'<font size="9">{esc(opts[j])}</font>', styles['Opt'])]
                if j + 1 < len(opts):
                    r.append(Paragraph(f'<font size="9">{esc(opts[j+1])}</font>', styles['Opt']))
                od.append(r)
        t = Table(od, colWidths=[7*cm, 7*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elems.append(t)
    
    # 子题
    for sub in q.get('sub_questions', []):
        elems.append(Paragraph(esc(sub), styles['SubQ']))
    
    # 答题空间（题目册中解答题）
    if role not in ('example', 'variant'):
        if len(q.get('sub_questions', [])) >= 2 or '解答' in q.get('text', ''):
            elems.append(Spacer(1, 4))
            elems.append(AnsSpace(4))
    
    # 答案册：解题内容
    if is_ans and q.get('solution'):
        sol = q['solution']
        for kind, content in sol.items():
            if content:
                lb = {'解题思路': '【解题思路】', '解答过程': '【解答过程】',
                      '答案': '【答案】', '解析': '【解析】'}.get(kind, kind)
                ct = esc(content)
                elems.append(Paragraph(
                    f'<font color="{hex_c(C_ACCENT)}" size="8"><b>{lb}</b></font> '
                    f'<font color="#555" size="8">{ct}</font>',
                    styles['Ans']))
    
    return elems

# ============ PDF生成 ============
def generate_pdf(sections, out_path, doc_type='题目册', is_ans=False):
    print(f"\n📄 生成 {doc_type} PDF...")
    styles = make_styles()
    pw = A4[0] - 4*cm  # 可用宽度
    
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=1.8*cm,
        title=f'高中数学同步练习·{doc_type}',
        author='一隅三反工作室')
    
    story = []
    q_num = 0
    
    # ============ 封面 ============
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph('高中数学同步练习', styles['CoverTitle']))
    story.append(Spacer(1, 6))
    story.append(HLine(pw, C_SECONDARY, 1.5))
    story.append(Spacer(1, 10))
    story.append(Paragraph('基础巩固 · 能力提升 · 拔尖挑战', styles['CoverSub']))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph('人教A版2019 · 全册同步', styles['CoverSub']))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(doc_type, styles['CoverVer']))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph('一隅三反 · 基础巩固 ｜ 举一反三 · 能力提升 ｜ 拔尖挑战', styles['Legend']))
    story.append(PageBreak())
    
    # ============ 遍历章节 ============
    for sec in sections:
        if sec['kind'] == 'practice':
            # 精练标题
            story.append(Paragraph(f'▎{esc(sec["title"])}', styles['SecTitle']))
            story.append(HLine(pw, C_SECONDARY, 0.8))
            story.append(Spacer(1, 4))
            for q in sec.get('questions', []):
                q_num += 1
                block = make_q_block(q, styles, q_num, is_ans)
                story.append(KeepTogether(block))
        
        elif sec['kind'] == 'topic':
            # 专题标题（新页开始）
            story.append(PageBreak())
            story.append(Paragraph(f'◆ {esc(sec["title"])}', styles['TopTitle']))
            story.append(HLine(pw, C_SECONDARY, 0.8))
            story.append(Spacer(1, 4))
            
            # 知识点
            for kp in sec.get('knowledge_points', []):
                story.append(DecoBox(kp['name'], C_PRIMARY, 10, pw))
                story.append(Spacer(1, 2))
                for c in kp.get('content', [])[:12]:
                    story.append(Paragraph(esc(c), styles['KPTxt']))
                story.append(Spacer(1, 3))
            
            # 题型
            for qt in sec.get('question_types', []):
                kind_icon = '🔷' if qt['kind'] == '题型' else '🔸'
                story.append(DecoBox(f'{kind_icon} {qt["name"]}', C_DARK, 10, pw))
                story.append(Spacer(1, 2))
                for q in qt.get('questions', []):
                    q_num += 1
                    block = make_q_block(q, styles, q_num, is_ans)
                    story.append(KeepTogether(block))
        
        elif sec['kind'] == 'test':
            # 综合测试（新页开始）
            story.append(PageBreak())
            story.append(Paragraph(f'★ {esc(sec["title"])}', styles['ChTitle']))
            story.append(HLine(pw, C_ACCENT, 1))
            story.append(Spacer(1, 4))
            for q in sec.get('questions', []):
                q_num += 1
                block = make_q_block(q, styles, q_num, is_ans)
                story.append(KeepTogether(block))
    
    # ============ 页面装饰 ============
    def decorate(canvas, doc):
        pg = canvas.getPageNumber()
        canvas.saveState()
        # 页眉线
        canvas.setStrokeColor(C_LIGHT_GRAY)
        canvas.setLineWidth(0.4)
        canvas.line(2*cm, A4[1] - 1.6*cm, A4[0] - 2*cm, A4[1] - 1.6*cm)
        canvas.setFont('WQY', 6.5)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(2*cm, A4[1] - 1.4*cm, '高中数学同步练习 · ' + doc_type)
        # 页脚线+页码
        canvas.line(2*cm, 1.3*cm, A4[0] - 2*cm, 1.3*cm)
        canvas.setFont('WQY', 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawCentredString(A4[0] / 2, 0.8*cm, f'— {pg} —')
        canvas.restoreState()
    
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    sz = os.path.getsize(out_path)
    print(f"✅ {doc_type}完成! {sz/1024/1024:.1f}MB · {out_path}")
    return sz

# ============ 主程序 ============
def main():
    q_secs = extract_sections(os.path.join(BASE, '高中数学同步练习_题目册_texts.json'), False)
    a_secs = extract_sections(os.path.join(BASE, '高中数学同步练习_答案册_texts.json'), True)
    
    generate_pdf(q_secs, os.path.join(BASE, '高中数学同步练习_题目册_v3.pdf'), '题目册', False)
    generate_pdf(a_secs, os.path.join(BASE, '高中数学同步练习_答案册_v3.pdf'), '答案册', True)
    print("\n🎉 全部完成!")

if __name__ == '__main__':
    main()
