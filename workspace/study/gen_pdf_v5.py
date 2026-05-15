#!/usr/bin/env python3
"""
高中数学同步练习册 · 印刷级PDF排版 v5
商业练习册水准：必刷题/53天天练/一遍过风格
- 题目完整显示，不截断
- 思源黑体(标题) + 思源宋体(正文)
- 美观的排版布局
- 选项背景框 + 规范答题区
- 动态页眉(章节名) + 页脚(册别+页码)
- 答案册：只放题号+答案+解析，不重复题目
"""
import os, re, sys, json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Flowable, Frame, FrameBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = '/root/.openclaw/workspace-main/pixel-astro-blog/study'

# 字体注册
pdfmetrics.registerFont(TTFont('Sans', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Sans-Bold', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', subfontIndex=1))
pdfmetrics.registerFont(TTFont('Serif', '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'))
pdfmetrics.registerFont(TTFont('Serif-Bold', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', subfontIndex=1))

# 配色
C_PRIMARY   = colors.HexColor('#1A3C6E')
C_SECONDARY = colors.HexColor('#2C5F8A')
C_PRACTICE  = colors.HexColor('#1565C0')
C_EXAMPLE   = colors.HexColor('#2E7D32')
C_VARIANT   = colors.HexColor('#E65100')
C_QTYPE     = colors.HexColor('#C0392B')
C_TEST      = colors.HexColor('#C62828')
C_ACCENT    = colors.HexColor('#C0392B')
C_DARK      = colors.HexColor('#1A1A2E')
C_GRAY      = colors.HexColor('#666666')
C_BG_KP     = colors.HexColor('#E8EDF5')
C_BG_OPT    = colors.HexColor('#F5F6F8')

# 正则
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

def esc(text):
    """转义HTML特殊字符，但保留题目中的完整内容"""
    t = str(text)
    # 先转义HTML
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # 然后替换换行符
    t = t.replace('\n', '<br/>')
    # 保留中文、数字、字母、常用标点
    # 只过滤掉控制字符
    result = ''.join(c for c in t if ord(c) >= 32 or c in '\n')
    return result

def hex_c(c):
    r,g,b = int(c.red*255), int(c.green*255), int(c.blue*255)
    return f'#{r:02X}{g:02X}{b:02X}'

def split_opts(text):
    parts = re.split(r'(?=[A-D][．\.])', text)
    return [p.strip() for p in parts if p.strip()]

def classify(text, in_topic=False):
    if not text: return 'empty'
    if TEST_PAT.match(text): return 'test'
    if CH_PAT.match(text): return 'chapter'
    if SEC_PAT.match(text): return 'section'
    if TOPIC_PAT.match(text): return 'topic'
    if GRP_PAT.match(text): return 'group'
    if TYPE_HDR.match(text): return 'type_header'
    if ANSWER_PAT.match(text): return 'answer'
    if ANALYSIS_PAT.match(text): return 'analysis'
    if SOLUTION_PAT.match(text): return 'solution'
    if in_topic:
        if KP_PAT.match(text): return 'kp_header'
        if QTYPE_PAT.match(text): return 'qtype_tag'
        if EXAMPLE_PAT.match(text): return 'example'
        if VARIANT_PAT.match(text): return 'variant'
        if NOTE_PAT.match(text): return 'note'
        if BOOK_HDR.match(text): return 'book_header'
    if Q_NUM_PAT.match(text) and len(text) > 2: return 'question'
    # 数字+括号缺分隔
    if re.match(r'^\d+[（(]', text) and len(text) > 5: return 'question'
    if OPT_PAT.match(text) and len(text) < 80: return 'option'
    # 全角括号子题
    if re.match(r'^（\d+）', text): return 'sub_question'
    # 半角括号子题
    if re.match(r'^\(\d+\)', text): return 'sub_question'
    # ①②③编号
    if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩]', text): return 'sub_question'
    return 'text'

# ---- 自定义Flowable ----
class HLine(Flowable):
    def __init__(self, w, c=colors.HexColor('#CCCCCC'), t=0.5, dash=None):
        Flowable.__init__(self)
        self.width = w; self.color = c; self.thickness = t; self.dash = dash; self.height = 2
    def draw(self):
        self.canv.setStrokeColor(self.color); self.canv.setLineWidth(self.thickness)
        if self.dash: self.canv.setDash(*self.dash)
        self.canv.line(0, 1, self.width, 1)

class SectionBanner(Flowable):
    """章节横幅：背景色块+白色标题"""
    def __init__(self, text, color=C_PRACTICE, width=14*cm, height=26, font_size=11):
        Flowable.__init__(self)
        self._text = text; self._color = color; self._width = width
        self.height = height; self.width = width; self._fs = font_size
    def draw(self):
        c = self.canv
        c.setFillColor(self._color)
        c.roundRect(0, 0, self._width, self.height, 3, fill=1, stroke=0)
        # 左侧深色条
        darker = colors.Color(max(self._color.red-0.1,0), max(self._color.green-0.1,0), max(self._color.blue-0.1,0))
        c.setFillColor(darker)
        c.roundRect(0, 0, 5, self.height, 3, fill=1, stroke=0)
        # 白色标题
        c.setFillColor(colors.white)
        c.setFont('Sans-Bold', self._fs)
        c.drawString(14, 7, self._text)

class KPBox(Flowable):
    """知识点框：浅蓝背景+左侧深蓝条"""
    def __init__(self, text, width=14*cm, height=20):
        Flowable.__init__(self)
        self._text = text; self._width = width; self.height = height; self.width = width
    def draw(self):
        c = self.canv
        c.setFillColor(C_BG_KP)
        c.roundRect(0, 0, self._width, self.height, 2, fill=1, stroke=0)
        c.setFillColor(C_PRIMARY)
        c.roundRect(0, 0, 4, self.height, 2, fill=1, stroke=0)
        c.setFont('Sans-Bold', 9)
        c.drawString(10, 5, self._text)

class QTypeTag(Flowable):
    """题型标签：橙色左侧条"""
    def __init__(self, text, width=14*cm, height=18):
        Flowable.__init__(self)
        self._text = text; self._width = width; self.height = height; self.width = width
    def draw(self):
        c = self.canv
        c.setFillColor(C_QTYPE)
        c.roundRect(0, 0, 3, self.height, 1, fill=1, stroke=0)
        c.setFillColor(C_QTYPE)
        c.setFont('Sans-Bold', 9)
        c.drawString(8, 4, self._text)
        c.setStrokeColor(colors.HexColor('#FFE0B2'))
        c.setLineWidth(0.3)
        c.line(8, 0, self._width, 0)

class SectionMarker(Flowable):
    """隐形Flowable：更新当前章节名（用于页眉）"""
    def __init__(self, chapter_name):
        Flowable.__init__(self)
        self._name = chapter_name
        self.width = 0; self.height = 0
    def draw(self):
        self.canv._doc.chapter_name = self._name

class AnsSpace(Flowable):
    """规范答题区：带"解："提示的虚线格"""
    def __init__(self, lines=6, w=14*cm):
        Flowable.__init__(self)
        self.sw = w; self.lc = lines
        self.height = lines * 16 + 12
        self.width = w
    def draw(self):
        c = self.canv
        c.setFont('Serif', 9)
        c.setFillColor(C_GRAY)
        c.drawString(0, self.height - 10, '解：')
        c.setStrokeColor(colors.HexColor('#D0D0D0'))
        c.setLineWidth(0.3)
        c.setDash(3, 3)
        for i in range(self.lc):
            y = self.height - 12 - (i + 1) * 16
            c.line(0, y, self.sw, y)

# ---- 提取结构化数据 ----
def extract_sections(json_path, is_answer=False):
    print(f"📖 提取: {os.path.basename(json_path)}")
    with open(json_path, 'r', encoding='utf-8') as f:
        paras = json.load(f)
    sections = []; cur = None; cur_q = None; cur_kp = None; cur_qt = None; in_topic = False
    for p in paras:
        text = p['t'].strip()
        if not text: continue
        pt = classify(text, in_topic)
        if pt == 'section':
            if cur: sections.append(cur)
            m = SEC_PAT.match(text)
            cur = {'kind':'practice','title':text,'num':m.group(1) if m else '','questions':[]}
            in_topic=False; cur_q=None; continue
        if pt == 'topic':
            if cur:
                if cur['kind']=='topic':
                    if cur_kp: cur.setdefault('knowledge_points',[]).append(cur_kp); cur_kp=None
                    if cur_qt: cur.setdefault('question_types',[]).append(cur_qt); cur_qt=None
                sections.append(cur)
            m = TOPIC_PAT.match(text)
            cur = {'kind':'topic','title':text,'num':m.group(1) if m else '','knowledge_points':[],'question_types':[]}
            in_topic=True; cur_q=None; continue
        if pt == 'test':
            if cur: sections.append(cur)
            cur = {'kind':'test','title':text,'questions':[]}
            in_topic=False; cur_q=None; continue
        if pt in ('chapter','group','type_header','book_header'): continue
        if in_topic:
            if pt == 'kp_header':
                if cur_kp: cur.setdefault('knowledge_points',[]).append(cur_kp)
                m = KP_PAT.match(text)
                cur_kp = {'name':m.group(1).strip() if m else text,'content':[]}; cur_q=None; continue
            if pt == 'qtype_tag':
                if cur_kp: cur.setdefault('knowledge_points',[]).append(cur_kp); cur_kp=None
                if cur_qt: cur.setdefault('question_types',[]).append(cur_qt)
                m = QTYPE_PAT.match(text)
                cur_qt = {'kind':m.group(1) if m else '','name':m.group(2).strip() if m else text,'questions':[]}
                cur_q=None; continue
            if pt == 'example':
                cur_q = {'role':'example','text':text,'options':[],'sub_questions':[],'solution':{}}
                if cur_qt: cur_qt['questions'].append(cur_q); continue
            if pt == 'variant':
                cur_q = {'role':'variant','text':text,'options':[],'sub_questions':[],'solution':{}}
                if cur_qt: cur_qt['questions'].append(cur_q); continue
            if pt == 'answer' and is_answer and cur_q:
                m = ANSWER_PAT.match(text)
                if m: cur_q['solution']['答案'] = m.group(1); continue
            if pt == 'analysis' and is_answer and cur_q:
                m = ANALYSIS_PAT.match(text)
                if m: cur_q['solution']['解析'] = m.group(1); continue
            if pt == 'solution' and is_answer and cur_q:
                m = SOLUTION_PAT.match(text)
                if m: cur_q['solution'][m.group(1)] = m.group(2); continue
            if pt == 'option' and cur_q:
                cur_q['options'].extend(split_opts(text)); continue
            if pt == 'sub_question' and cur_q:
                cur_q['sub_questions'].append(text); continue
            if pt == 'question' and cur_qt:
                cur_q = {'role':'numbered','text':text,'options':[],'sub_questions':[],'solution':{}}
                cur_qt['questions'].append(cur_q); continue
            if pt == 'note' and cur_kp is not None:
                cur_kp['content'].append(text); continue
            if pt == 'text' and cur_kp is not None and cur_qt is None:
                cur_kp['content'].append(text); continue
            continue
        if pt == 'question' and cur:
            cur_q = {'role':'practice','text':text,'options':[],'sub_questions':[],'solution':{}}
            cur['questions'].append(cur_q); continue
        if pt == 'answer' and is_answer and cur_q:
            m = ANSWER_PAT.match(text)
            if m: cur_q['solution']['答案'] = m.group(1); continue
        if pt == 'analysis' and is_answer and cur_q:
            m = ANALYSIS_PAT.match(text)
            if m: cur_q['solution']['解析'] = m.group(1); continue
        if pt == 'solution' and is_answer and cur_q:
            m = SOLUTION_PAT.match(text)
            if m: cur_q['solution'][m.group(1)] = m.group(2); continue
        if pt == 'option' and cur_q:
            cur_q['options'].extend(split_opts(text)); continue
        if pt == 'sub_question' and cur_q:
            cur_q['sub_questions'].append(text); continue
    if cur:
        if cur['kind']=='topic':
            if cur_kp: cur.setdefault('knowledge_points',[]).append(cur_kp)
            if cur_qt: cur.setdefault('question_types',[]).append(cur_qt)
        sections.append(cur)
    p_t = sum(len(s.get('questions',[])) for s in sections if s['kind'] in ('practice','test'))
    t_t = sum(len(qt.get('questions',[])) for s in sections if s['kind']=='topic' for qt in s.get('question_types',[]))
    print(f"  精练:{len([s for s in sections if s['kind']=='practice'])}节/{p_t}题  "
          f"专题:{len([s for s in sections if s['kind']=='topic'])}个/{t_t}题  "
          f"测试:{len([s for s in sections if s['kind']=='test'])}个")
    if is_answer:
        total_q = 0; has_ans = 0
        for s in sections:
            for q in s.get('questions',[]):
                total_q += 1
                if q.get('solution'): has_ans += 1
            for qt in s.get('question_types',[]):
                for q in qt.get('questions',[]):
                    total_q += 1
                    if q.get('solution'): has_ans += 1
        print(f"  答案覆盖: {has_ans}/{total_q} ({has_ans*100//max(total_q,1)}%)")
    return sections

# ---- 样式 ----
def make_styles():
    ss = getSampleStyleSheet()
    # 封面
    ss.add(ParagraphStyle('CoverTitle', fontName='Sans-Bold', fontSize=36,
                          textColor=C_PRIMARY, alignment=TA_CENTER, leading=48, spaceAfter=6))
    ss.add(ParagraphStyle('CoverSub', fontName='Sans', fontSize=16,
                          textColor=C_SECONDARY, alignment=TA_CENTER, leading=24, spaceAfter=4))
    ss.add(ParagraphStyle('CoverVer', fontName='Sans-Bold', fontSize=26,
                          textColor=C_ACCENT, alignment=TA_CENTER, leading=34))
    ss.add(ParagraphStyle('CoverSlogan', fontName='Serif', fontSize=9,
                          textColor=C_GRAY, alignment=TA_CENTER, leading=14))
    # 目录
    ss.add(ParagraphStyle('TOCTitle', fontName='Sans-Bold', fontSize=22,
                          textColor=C_PRIMARY, alignment=TA_CENTER, leading=30, spaceBefore=20))
    ss.add(ParagraphStyle('TOCChap', fontName='Sans-Bold', fontSize=10.5,
                          textColor=C_PRIMARY, spaceBefore=8, spaceAfter=2, leading=15))
    ss.add(ParagraphStyle('TOCItem', fontName='Serif', fontSize=9,
                          textColor=C_DARK, spaceBefore=1, spaceAfter=1, leading=13, leftIndent=12))
    # 内容
    ss.add(ParagraphStyle('Q', fontName='Serif', fontSize=10.5,
                          textColor=C_DARK, spaceBefore=2, spaceAfter=1, leading=16, leftIndent=0))
    ss.add(ParagraphStyle('Opt', fontName='Serif', fontSize=9,
                          textColor=C_DARK, spaceBefore=0.5, spaceAfter=0.5, leading=12, leftIndent=18))
    ss.add(ParagraphStyle('SubQ', fontName='Serif', fontSize=9.5,
                          textColor=C_DARK, spaceBefore=0.5, spaceAfter=0.5, leading=13, leftIndent=18))
    ss.add(ParagraphStyle('KPTxt', fontName='Serif', fontSize=9,
                          textColor=colors.HexColor('#333'), spaceBefore=1, spaceAfter=1, leading=13.5, leftIndent=10))
    # 答案册
    ss.add(ParagraphStyle('AnsTitle', fontName='Sans-Bold', fontSize=9,
                          textColor=C_PRIMARY, spaceBefore=4, spaceAfter=1, leading=13))
    ss.add(ParagraphStyle('AnsBody', fontName='Serif', fontSize=8.5,
                          textColor=colors.HexColor('#444'), spaceBefore=1, spaceAfter=1, leading=12, leftIndent=8))
    return ss

# ---- 题目渲染(题目册) ----
def make_q_block(q, styles, q_num):
    elems = []; text = q.get('text',''); role = q.get('role','practice')
    if role in ('example','variant'):
        if role == 'example':
            m = EXAMPLE_PAT.match(text)
            tag = f'<b><font color="{hex_c(C_EXAMPLE)}">【例】</font></b> '
            ct = m.group(1).strip() if m else text
        else:
            m = VARIANT_PAT.match(text)
            tag = f'<b><font color="{hex_c(C_VARIANT)}">【变式{m.group(1)}-{m.group(2)}】</font></b> '
            ct = m.group(3).strip() if m else text
        elems.append(Paragraph(f'{tag}{esc(ct)}', styles['Q']))
    else:
        m = Q_NUM_PAT.match(text); num = m.group(1) if m else str(q_num)
        ct = re.sub(r'^\d+[．\.]\s*','',text)
        multi = '<font color="#C62828" size="7"> 〖多选〗</font>' if '多选' in text else ''
        elems.append(Paragraph(f'<font color="{hex_c(C_PRACTICE)}"><b>{num}.</b></font>{multi} {esc(ct)}', styles['Q']))
    opts = q.get('options',[])
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
                if j+1 < len(opts): r.append(Paragraph(f'<font size="9">{esc(opts[j+1])}</font>', styles['Opt']))
                od.append(r)
        t = Table(od, colWidths=[7*cm, 7*cm])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),1),
                               ('BOTTOMPADDING',(0,0),(-1,-1),1),('LEFTPADDING',(0,0),(-1,-1),0),
                               ('RIGHTPADDING',(0,0),(-1,-1),0),('BACKGROUND',(0,0),(-1,-1),C_BG_OPT)]))
        elems.append(t)
    for sub in q.get('sub_questions',[]): elems.append(Paragraph(esc(sub), styles['SubQ']))
    if role not in ('example','variant'):
        if '解答' in q.get('text','') or len(q.get('sub_questions',[])) >= 2:
            elems.append(Spacer(1,3)); elems.append(AnsSpace(6, 14*cm))
    return elems

# ---- 答案渲染(答案册——只放答案不重复题目) ----
def make_ans_block(q, styles, q_num, is_topic=False):
    elems = []; text = q.get('text',''); role = q.get('role','practice'); sol = q.get('solution',{})
    if not sol: return elems
    if role == 'example':
        tag = f'<font color="{hex_c(C_EXAMPLE)}"><b>【例】</b></font>'
    elif role == 'variant':
        m = VARIANT_PAT.match(text)
        tag = f'<font color="{hex_c(C_VARIANT)}"><b>【变式{m.group(1)}-{m.group(2)}】</b></font>' if m else '<b>【变式】</b>'
    else:
        m = Q_NUM_PAT.match(text); num = m.group(1) if m else str(q_num)
        tag = f'<font color="{hex_c(C_PRACTICE)}"><b>{num}.</b></font>'
    ans_text = sol.get('答案','').strip()
    analysis_text = sol.get('解析','').strip()
    thought = sol.get('解题思路','').strip()
    process = sol.get('解答过程','').strip()
    if ans_text:
        elems.append(Paragraph(f'{tag} <font color="{hex_c(C_ACCENT)}"><b>【答案】</b></font> {esc(ans_text)}', styles['AnsTitle']))
    if thought:
        elems.append(Paragraph(f'  <font color="{hex_c(C_SECONDARY)}"><b>【解题思路】</b></font> {esc(thought)}', styles['AnsBody']))
    if process:
        elems.append(Paragraph(f'  <font color="{hex_c(C_SECONDARY)}"><b>【解答过程】</b></font> {esc(process)}', styles['AnsBody']))
    if analysis_text:
        elems.append(Paragraph(f'  <font color="{hex_c(C_GRAY)}"><b>【解析】</b></font> {esc(analysis_text)}', styles['AnsBody']))
    return elems

# ---- 封面 ----
def make_cover(story, pw, doc_type, styles):
    story.append(Spacer(1, 2*cm))
    # 顶部装饰线
    story.append(HLine(pw, C_PRIMARY, 2)); story.append(Spacer(1, 8))
    story.append(Paragraph('高中数学同步练习', styles['CoverTitle']))
    story.append(Spacer(1, 4))
    story.append(HLine(pw*0.6, C_SECONDARY, 1)); story.append(Spacer(1, 10))
    story.append(Paragraph('基础巩固 · 能力提升 · 拔尖挑战', styles['CoverSub']))
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph('人教A版2019 · 全册同步', styles['CoverSub']))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(doc_type, styles['CoverVer']))
    story.append(Spacer(1, 2*cm))
    story.append(HLine(pw*0.3, C_SECONDARY, 0.6)); story.append(Spacer(1, 6))
    story.append(Paragraph('一隅三反 · 基础巩固 ｜ 举一反三 · 能力提升 ｜ 拔尖挑战', styles['CoverSlogan']))
    story.append(PageBreak())

# ---- 目录 ----
def make_toc(story, sections, styles):
    story.append(Paragraph('目  录', styles['TOCTitle']))
    story.append(Spacer(1, 8)); story.append(HLine(14*cm, C_PRIMARY, 1)); story.append(Spacer(1, 6))
    for sec in sections:
        t = sec['title']
        if sec['kind'] == 'practice':
            story.append(Paragraph(f'<b>▎{esc(t[:35])}</b>', styles['TOCChap']))
        elif sec['kind'] == 'topic':
            story.append(Paragraph(f'  ◇ {esc(t[:40])}', styles['TOCItem']))
        elif sec['kind'] == 'test':
            story.append(Paragraph(f'<b>  ★ {esc(t[:40])}</b>', styles['TOCItem']))
    story.append(PageBreak())

# ---- PDF生成 ----
def generate_pdf(sections, out_path, doc_type='题目册', is_ans=False):
    print(f"\n📄 生成 {doc_type} PDF...")
    styles = make_styles(); pw = A4[0] - 4*cm
    # chapter tracking via SectionMarker
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.4*cm, bottomMargin=2*cm,
                            title=f'高中数学同步练习·{doc_type}', author='一隅三反工作室')
    story = []; q_num = 0
    make_cover(story, pw, doc_type, styles)
    make_toc(story, sections, styles)
    for sec in sections:
        if sec['kind'] == 'practice':
            story.append(SectionMarker(sec['title'][:25]))
            story.append(SectionBanner(sec['title'][:32], C_PRACTICE, pw, 26, 11))
            story.append(Spacer(1, 6))
            for q in sec.get('questions',[]):
                q_num += 1
                if is_ans: block = make_ans_block(q, styles, q_num)
                else: block = make_q_block(q, styles, q_num)
                if block: story.append(KeepTogether(block))
        elif sec['kind'] == 'topic':
            story.append(SectionMarker(sec['title'][:25])); story.append(PageBreak())
            story.append(SectionBanner(sec['title'][:38], C_PRIMARY, pw, 28, 12))
            story.append(Spacer(1, 6))
            for kp in sec.get('knowledge_points',[]):
                story.append(KPBox(kp['name'], pw)); story.append(Spacer(1, 2))
                if not is_ans:
                    for c in kp.get('content',[])[:15]:
                        story.append(Paragraph(esc(c), styles['KPTxt']))
                story.append(Spacer(1, 3))
            for qt in sec.get('question_types',[]):
                story.append(QTypeTag(f'{qt["kind"]}：{qt["name"]}', pw)); story.append(Spacer(1, 3))
                for q in qt.get('questions',[]):
                    q_num += 1
                    if is_ans: block = make_ans_block(q, styles, q_num, True)
                    else: block = make_q_block(q, styles, q_num)
                    if block: story.append(KeepTogether(block))
                story.append(Spacer(1, 3))
        elif sec['kind'] == 'test':
            story.append(SectionMarker(sec['title'][:25])); story.append(PageBreak())
            story.append(SectionBanner(sec['title'][:38], C_TEST, pw, 28, 12))
            story.append(Spacer(1, 6))
            for q in sec.get('questions',[]):
                q_num += 1
                if is_ans: block = make_ans_block(q, styles, q_num)
                else: block = make_q_block(q, styles, q_num)
                if block: story.append(KeepTogether(block))
    def decorate(canvas, doc):
        pg = canvas.getPageNumber()
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#D0D0D0')); canvas.setLineWidth(0.4)
        canvas.line(2*cm, A4[1]-1.8*cm, A4[0]-2*cm, A4[1]-1.8*cm)
        canvas.setFont('Sans', 6.5); canvas.setFillColor(C_GRAY)
        canvas.drawString(2*cm, A4[1]-1.55*cm, '高中数学同步练习')
        chapter = getattr(canvas._doc, 'chapter_name', doc_type)
        canvas.drawRightString(A4[0]-2*cm, A4[1]-1.55*cm, chapter)
        canvas.line(2*cm, 1.5*cm, A4[0]-2*cm, 1.5*cm)
        canvas.setFont('Sans', 7); canvas.setFillColor(C_GRAY)
        canvas.drawString(2*cm, 1*cm, doc_type)
        canvas.drawCentredString(A4[0]/2, 1*cm, f'— {pg} —')
        canvas.restoreState()
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    sz = os.path.getsize(out_path)
    print(f"✅ {doc_type}完成! {sz/1024/1024:.1f}MB · {out_path}")

def main():
    q_secs = extract_sections(os.path.join(BASE, '高中数学同步练习_题目册_texts.json'), False)
    a_secs = extract_sections(os.path.join(BASE, '高中数学同步练习_答案册_texts.json'), True)
    generate_pdf(q_secs, os.path.join(BASE, '高中数学同步练习_题目册_v5.pdf'), '题目册', False)
    generate_pdf(a_secs, os.path.join(BASE, '高中数学同步练习_答案册_v5.pdf'), '答案册', True)
    print("\n🎉 全部完成!")

if __name__ == '__main__':
    main()
