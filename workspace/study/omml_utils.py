#!/usr/bin/env python3
"""
OMML → Unicode 数学文本转换器
从DOCX段落提取完整文本（Word文本 + OMML公式）
"""

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'


def omml_to_unicode(om_elem):
    """递归将OMML元素转为unicode可读数学文本"""
    result = []
    for child in om_elem:
        tag = etree.QName(child.tag).localname
        ns = etree.QName(child.tag).namespace
        if ns != M:
            continue

        if tag == 'r':  # math run
            for t in child.iter(f'{{{M}}}t'):
                if t.text:
                    result.append(t.text)
        elif tag == 'f':  # fraction
            num = child.find(f'{{{M}}}num')
            den = child.find(f'{{{M}}}den')
            nt = omml_to_unicode(num) if num is not None else ''
            dt = omml_to_unicode(den) if den is not None else ''
            if nt and dt:
                result.append(f'{nt}/{dt}')
        elif tag == 'sSup':  # superscript
            base = child.find(f'{{{M}}}e')
            sup = child.find(f'{{{M}}}sup')
            bt = omml_to_unicode(base) if base is not None else ''
            st = omml_to_unicode(sup) if sup is not None else ''
            result.append(f'{bt}^{st}')
        elif tag == 'sSub':  # subscript
            base = child.find(f'{{{M}}}e')
            sub = child.find(f'{{{M}}}sub')
            bt = omml_to_unicode(base) if base is not None else ''
            st = omml_to_unicode(sub) if sub is not None else ''
            result.append(f'{bt}_{st}')
        elif tag == 'sSubSup':  # sub+superscript
            base = child.find(f'{{{M}}}e')
            sub = child.find(f'{{{M}}}sub')
            sup = child.find(f'{{{M}}}sup')
            bt = omml_to_unicode(base) if base is not None else ''
            st = omml_to_unicode(sub) if sub is not None else ''
            pt = omml_to_unicode(sup) if sup is not None else ''
            result.append(f'{bt}_{st}^{pt}')
        elif tag == 'rad':  # radical (root)
            e = child.find(f'{{{M}}}e')
            et = omml_to_unicode(e) if e is not None else ''
            deg = child.find(f'{{{M}}}deg')
            if deg is not None:
                deg_text = omml_to_unicode(deg)
                if deg_text and deg_text != '2':
                    result.append(f'{deg_text}√({et})')
                else:
                    result.append(f'√({et})')
            else:
                result.append(f'√({et})')
        elif tag == 'd':  # delimiter (brackets)
            dPr = child.find(f'{{{M}}}dPr')
            beg = '('
            end = ')'
            if dPr is not None:
                begChr = dPr.find(f'{{{M}}}begChr')
                endChr = dPr.find(f'{{{M}}}endChr')
                if begChr is not None:
                    beg = begChr.get(f'{{{M}}}val', '(')
                if endChr is not None:
                    end = endChr.get(f'{{{M}}}val', ')')
            parts = []
            for e in child.findall(f'{{{M}}}e'):
                parts.append(omml_to_unicode(e))
            result.append(f'{beg}{" , ".join(parts)}{end}')
        elif tag == 'func':  # function
            fname = child.find(f'{{{M}}}fName')
            e = child.find(f'{{{M}}}e')
            ft = omml_to_unicode(fname) if fname is not None else ''
            et = omml_to_unicode(e) if e is not None else ''
            if ft and et:
                result.append(f'{ft}({et})')
            elif et:
                result.append(et)
        elif tag == 'acc':  # accent (hat, tilde, etc.)
            e = child.find(f'{{{M}}}e')
            result.append(omml_to_unicode(e) if e is not None else '')
        elif tag == 'bar':  # overbar
            e = child.find(f'{{{M}}}e')
            et = omml_to_unicode(e) if e is not None else ''
            result.append(f'‾{et}')
        elif tag == 'nary':  # n-ary (sum, product, integral)
            e = child.find(f'{{{M}}}e')
            sub_elem = child.find(f'{{{M}}}sub')
            sup_elem = child.find(f'{{{M}}}sup')
            chr_elem = child.find(f'{{{M}}}naryPr/{{{M}}}chr')
            nary_char = chr_elem.get(f'{{{M}}}val') if chr_elem is not None else '∑'
            et = omml_to_unicode(e) if e is not None else ''
            st = omml_to_unicode(sub_elem) if sub_elem is not None else ''
            pt = omml_to_unicode(sup_elem) if sup_elem is not None else ''
            if st and pt:
                result.append(f'{nary_char}[{st},{pt}]({et})')
            elif st:
                result.append(f'{nary_char}[{st}]({et})')
            else:
                result.append(f'{nary_char}({et})')
        elif tag == 'eqArr':  # equation array
            for e in child.findall(f'{{{M}}}e'):
                result.append(omml_to_unicode(e))
        elif tag == 'm':  # matrix
            rows = []
            for mr in child.findall(f'{{{M}}}mr'):
                row = []
                for e in mr.findall(f'{{{M}}}e'):
                    row.append(omml_to_unicode(e))
                rows.append('(' + ','.join(row) + ')')
            result.append(' '.join(rows))
        elif tag == 'rPr':  # run properties - skip
            pass
        elif tag in ('e', 'num', 'den', 'sup', 'sub', 'deg', 'oMath', 'oMathPara'):
            result.append(omml_to_unicode(child))
        elif tag == 'sPre':  # pre-sub-superscript
            e = child.find(f'{{{M}}}e')
            sub = child.find(f'{{{M}}}sub')
            sup = child.find(f'{{{M}}}sup')
            et = omml_to_unicode(e) if e is not None else ''
            st = omml_to_unicode(sub) if sub is not None else ''
            pt = omml_to_unicode(sup) if sup is not None else ''
            result.append(f'_{st}^{pt}{et}')
        elif tag == 'groupChr':  # group character (underbrace etc.)
            e = child.find(f'{{{M}}}e')
            result.append(omml_to_unicode(e) if e is not None else '')
        elif tag == 'limLow':  # lower limit
            e = child.find(f'{{{M}}}e')
            lim = child.find(f'{{{M}}}lim')
            et = omml_to_unicode(e) if e is not None else ''
            lt = omml_to_unicode(lim) if lim is not None else ''
            result.append(f'{et}_{lt}')
        elif tag == 'limUpp':  # upper limit
            e = child.find(f'{{{M}}}e')
            lim = child.find(f'{{{M}}}lim')
            et = omml_to_unicode(e) if e is not None else ''
            lt = omml_to_unicode(lim) if lim is not None else ''
            result.append(f'{et}^{lt}')
        # else: skip unknown tags

    return ''.join(result)


def extract_full_text(para):
    """提取段落的完整文本（Word文本 + OMML公式转Unicode）"""
    parts = []
    for child in para._element:
        ns = etree.QName(child.tag).namespace if '}' in child.tag else ''
        tag = etree.QName(child.tag).localname if '}' in child.tag else child.tag

        if ns == W:
            if tag == 'r':  # Word run
                for t in child.iter(f'{{{W}}}t'):
                    if t.text:
                        parts.append(t.text)
            elif tag == 'pPr':  # paragraph properties - skip
                pass
            elif tag == 'bookmarkStart' or tag == 'bookmarkEnd':
                pass
            # Hyperlinks etc - extract text
            else:
                for t in child.iter(f'{{{W}}}t'):
                    if t.text:
                        parts.append(t.text)
        elif ns == M:
            if tag == 'oMathPara':
                math_text = omml_to_unicode(child)
                if math_text:
                    parts.append(math_text)
            elif tag == 'oMath':
                math_text = omml_to_unicode(child)
                if math_text:
                    parts.append(math_text)

    return ''.join(parts)
