# -*- coding: utf-8 -*-
"""医美技术栈系列配图生成器。运行后在本目录输出全部 SVG，并做 XML 良构校验。"""
from pathlib import Path
from xml.dom import minidom

OUT = Path(__file__).parent

INK = '#22424A'
SUB = '#5E7A80'
TEAL = '#0E6E5F'
TEAL_DK = '#0A4A41'
GOLD = '#C9A063'
GOLD_BG = '#F6EEDD'
TERRA = '#B4562F'
TERRA_BG = '#F9EDE5'
BG = '#F7F8F6'
CARD = '#FFFFFF'
LINE = '#D9E1DD'
BLUE = '#4A6FA5'
BLUE_BG = '#EBF0F8'
SCALE7 = ['#0A4A41', '#0E6E5F', '#2E8A79', '#5FA292', '#93C2B6', '#C6E0D8', '#E7F2EE']  # 深到浅

FONT_CSS = "text{font-family:'PingFang SC','Microsoft YaHei','Noto Sans SC','Source Han Sans SC',sans-serif;}"


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def tw(s, fs):
    w = 0.0
    for c in s:
        o = ord(c)
        if o > 0x2E7F:
            w += fs
        elif c.isdigit() or c in '.%':
            w += fs * 0.56
        elif c.isupper():
            w += fs * 0.68
        elif c in ' ':
            w += fs * 0.3
        else:
            w += fs * 0.55
    return w


def txt(x, y, s, fs=16, fill=INK, w=400, anchor='start', ls=0, opacity=None):
    extra = f' letter-spacing="{ls}"' if ls else ''
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{fs}" fill="{fill}" '
            f'font-weight="{w}" text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def mtext(x, y, lines, fs=15, fill=INK, lh=None, w=400, anchor='start'):
    lh = lh or int(fs * 1.72)
    return ''.join(txt(x, y + i * lh, ln, fs, fill, w, anchor) for i, ln in enumerate(lines))


def rect(x, y, w, h, rx=12, fill=CARD, stroke=LINE, sw=1.4, dash=None, opacity=None):
    s = f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        s += f' fill-opacity="{opacity}"'
    return s + '/>'


def circle(cx, cy, r, fill, stroke='none', sw=1, opacity=None, dash=None):
    s = f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{fill}"'
    if stroke != 'none':
        s += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            s += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        s += f' fill-opacity="{opacity}"'
    return s + '/>'


def line(x1, y1, x2, y2, stroke=TEAL, sw=1.6, dash=None, marker=None, opacity=None):
    s = f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if marker:
        s += f' marker-end="url(#{marker})"'
    if opacity is not None:
        s += f' opacity="{opacity}"'
    return s + '/>'


def path(d, stroke=TEAL, sw=1.6, fill='none', marker=None, dash=None, opacity=None):
    s = f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if marker:
        s += f' marker-end="url(#{marker})"'
    if opacity is not None:
        s += f' opacity="{opacity}"'
    return s + '/>'


def pill(x, y, s, fs=13, fill=TEAL, tfill='#FFFFFF', h=None, padx=14):
    h = h or int(fs + 12)
    w = tw(s, fs) + padx * 2
    return (rect(x, y, w, h, rx=h / 2, fill=fill) +
            txt(x + w / 2, y + h / 2 + fs * 0.36, s, fs, tfill, 600, 'middle')), w, h


def pill_c(cx, y, s, fs=13, fill=TEAL, tfill='#FFFFFF', h=None, padx=14):
    h = h or int(fs + 12)
    w = tw(s, fs) + padx * 2
    return (rect(cx - w / 2, y, w, h, rx=h / 2, fill=fill) +
            txt(cx, y + h / 2 + fs * 0.36, s, fs, tfill, 600, 'middle')), w, h


def markers(ids_colors):
    out = ['<defs>']
    for mid, c in ids_colors:
        out.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" '
                   f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                   f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    out.append('</defs>')
    return ''.join(out)


def page(w, h, fig_no, title, sub):
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    p.append(f'<style>{FONT_CSS}</style>')
    p.append(markers([('ar', TEAL), ('arT', TERRA), ('arG', SUB), ('arB', BLUE), ('arGd', GOLD)]))
    p.append(rect(0, 0, w, h, rx=0, fill=BG, stroke=None))
    chip, _, _ = pill(46, 42, f'医美技术栈 · 图 {fig_no}', 13, TEAL_DK, '#FFFFFF')
    p.append(chip)
    p.append(txt(w / 2, 84, title, 33, INK, 700, 'middle'))
    p.append(txt(w / 2, 118, sub, 16.5, SUB, 400, 'middle'))
    p.append(line(46, 140, w - 46, 140, LINE, 1.2))
    p.append(txt(46, h - 24, '医美技术栈系列 · B 端', 12.5, SUB))
    p.append(txt(w - 46, h - 24, '事实核验 2026-08-18', 12.5, SUB, 400, 'end'))
    return p


# ---------- 图 00 三栈总览 ----------
def fig00():
    w, h = 1080, 800
    p = page(w, h, '00', '三张技术栈，医美的专业结构', '医生对标 IT 工程师，咨询师对标售前顾问 SC，机构对标工程组织')
    cols = [
        ('美容医生', '七层 · 纵深型', ['审美沟通', '规范安全', '评估', '材料', '设备', '底层语言', '准入'], 1),
        ('医美咨询师', '七层 · 广度型', ['边界', '流程客户', '呈现', '方案', '项目知识', '医学常识', '行业结构'], 0),
        ('医美机构', '八系统 · 组织型', ['经营', '获客品牌', '客户', '质量安全', '诊疗流程', '设备供应链', '人才', '资质'], 3),
    ]
    cw, gap, x0, ytop = 310, 35, 70, 168
    for ci, (name, tag, layers, gold_i) in enumerate(cols):
        x = x0 + ci * (cw + gap)
        p.append(rect(x, ytop, cw, 74, rx=14, fill=TEAL_DK if ci != 1 else TEAL))
        p.append(txt(x + cw / 2, ytop + 32, name, 21, '#FFFFFF', 700, 'middle'))
        p.append(txt(x + cw / 2, ytop + 56, tag, 13, '#D8ECE6', 400, 'middle'))
        n = len(layers)
        area_top, area_h = ytop + 96, 366
        bh = (area_h - (n - 1) * 8) / n
        for i, ln in enumerate(layers):
            y = area_top + i * (bh + 8)
            is_gold = (i == gold_i)
            fill = GOLD if is_gold else SCALE7[min(6, i + 1)]
            p.append(rect(x, y, cw, bh, rx=9, fill=fill))
            p.append(txt(x + cw / 2, y + bh / 2 + 6, ln, 16.5, '#FFFFFF' if i < 4 or is_gold else TEAL_DK, 600, 'middle'))
    ys = ytop + 96 + 366 + 26
    p.append(rect(70, ys, 940, 64, rx=14, fill=GOLD_BG, stroke=GOLD, sw=1.2))
    p.append(txt(540, ys + 27, '金色标记的三处是医疗属性多出的层', 16, '#8A6A33', 600, 'middle'))
    p.append(txt(540, ys + 50, '医生的规范安全层，咨询师的边界层，机构的质量安全系统。同构来自体例，分野来自医疗', 13.5, SUB, 400, 'middle'))
    return ''.join(p) + '</svg>'


# ---------- 图 01 医生七层全景 ----------
def fig01():
    w, h = 1080, 1500
    p = page(w, h, '01', '美容医生的技术栈，七层全景', '对标 IT 工程师 · 栈顶在上，准入为底，持续学习贯穿全栈')
    layers = [
        ('L7 审美沟通层', ['动态审美判断，概率语言沟通，预期管理', '与咨询师的协作接口'], '产品思维', False),
        ('L6 规范安全层', ['适应症与禁忌筛查，知情同意与病历', '并发症处置预案，感控与急救配置'], '工程规范（加厚）', True),
        ('L5 评估层', ['皮肤分型，皮肤镜与影像分析', '主诉需求轴评估，面部美学评估'], '调试与测试工具', False),
        ('L4 材料层', ['肉毒毒素剂量学，透明质酸特性与层次', '胶原与再生材料，外用口服药物证据'], '数据与存储', False),
        ('L3 设备层', ['波长脉宽光斑密度的参数思维', '光电声设备品类，注册类别意识'], '框架与库', False),
        ('L2 底层语言层', ['面部解剖，血管地图，脂肪室与韧带', '皮肤生理，色素病理，药理'], '编程语言', False),
        ('L1 准入层', ['执业医师资格与注册，主诊医师备案', '美容外科六年以上，皮肤科等三年以上经历'], '上岗认证', False),
    ]
    x0, cw = 64, 880
    y = 168
    bh, gp = 150, 14
    for i, (name, items, it, gold) in enumerate(layers):
        fill = SCALE7[i]
        p.append(rect(x0, y, cw, bh, rx=14, fill=fill))
        if gold:
            p.append(rect(x0, y, 10, bh, rx=5, fill=GOLD, stroke=None))
        tf = '#FFFFFF' if i <= 3 else TEAL_DK
        p.append(txt(x0 + 34, y + 52, name, 22, tf, 700))
        p.append(mtext(x0 + 34, y + 88, items, 15, '#F2F8F6' if i <= 3 else '#2A5A50', lh=27))
        pw = tw(it, 12.5) + 24
        p.append(rect(x0 + cw - pw - 22, y + 24, pw, 30, rx=15, fill='#FFFFFF', opacity=0.92 if i <= 3 else None))
        p.append(txt(x0 + cw - pw / 2 - 22, y + 44, it, 12.5, TEAL_DK, 600, 'middle'))
        if gold:
            p.append(txt(x0 + cw - pw - 22 - 12, y + 44, '医疗特有', 12.5, GOLD, 700, 'end'))
        y += bh + gp
    ax = 1000
    p.append(line(ax, 168 + 7 * bh + 6 * gp - 6, ax, 180, SUB, 2.2, marker='arG'))
    p.append(line(ax - 14, 168 + 7 * bh + 6 * gp - 6, ax - 14, 180, LINE, 1.2, dash='3 5'))
    p.append(txt(ax, 206, '持续学习', 13, SUB, 600, 'end'))
    p.append(txt(ax, 226, '版本升级', 13, SUB, 600, 'end'))
    ys = y + 6
    p.append(rect(x0, ys, 940, 96, rx=14, fill=CARD, stroke=LINE))
    p.append(txt(x0 + 26, ys + 32, '底部的两层是硬门槛', 16, INK, 700))
    p.append(mtext(x0 + 26, ys + 58, ['准入依据《医疗美容服务管理办法》（卫生部令第 19 号，2022 年修订），多数省份限备案一个专业类别。',
                                      '语言层决定上限，血管地图不清，后面的设备与材料全都无处安放。'], 13.5, SUB, lh=24))
    return ''.join(p) + '</svg>'


# ---------- 图 02 面部危险区与组织层次 ----------
def fig02():
    w, h = 1080, 830
    p = page(w, h, '02', '底层语言层，血管与层次', '血管地图决定注射路径，组织层次决定注入位置')
    # 左 面部危险区
    lx, ly, lw, lh_ = 60, 164, 520, 560
    p.append(rect(lx, ly, lw, lh_, rx=16, fill=CARD, stroke=LINE))
    p.append(txt(lx + 24, ly + 38, '面部注射的高危区（示意）', 18, INK, 700))
    fx, fy = lx + lw / 2, ly + 320
    p.append(f'<ellipse cx="{fx}" cy="{fy}" rx="150" ry="192" fill="#FDFCF9" stroke="{INK}" stroke-width="2"/>')
    # 眉眼鼻唇 示意
    p.append(path(f'M{fx-92} {fy-72} Q{fx-58} {fy-88} {fx-24} {fy-70}', INK, 2.2))
    p.append(path(f'M{fx+24} {fy-70} Q{fx+58} {fy-88} {fx+92} {fy-72}', INK, 2.2))
    p.append(f'<ellipse cx="{fx-58}" cy="{fy-46}" rx="26" ry="10" fill="{INK}" opacity="0.85"/>')
    p.append(f'<ellipse cx="{fx+58}" cy="{fy-46}" rx="26" ry="10" fill="{INK}" opacity="0.85"/>')
    p.append(path(f'M{fx} {fy-40} L{fx} {fy+52}', INK, 2.0))
    p.append(path(f'M{fx-16} {fy+56} Q{fx} {fy+70} {fx+16} {fy+56}', INK, 2.0))
    p.append(path(f'M{fx-42} {fy+118} Q{fx} {fy+140} {fx+42} {fy+118}', INK, 2.2))
    zones = [
        (fx, fy - 98, '额部 · 眶上动脉'),
        (fx, fy - 78, '眉间 · 滑车上动脉'),
        (fx, fy + 52, '鼻背 · 面动脉终末支'),
        (fx - 138, fy - 10, '颞部 · 颞浅动脉额支'),
        (fx + 138, fy - 10, '颞部 · 对侧同区'),
    ]
    for zx, zy, lab in zones:
        p.append(circle(zx, zy, 34, TERRA, TERRA, 1.6, 0.16, '5 4'))
        p.append(circle(zx, zy, 4, TERRA))
    p.append(line(fx, fy - 132, fx, ly + 130, TERRA, 1.2, dash='3 4'))
    p.append(txt(fx, ly + 148, '额部', 13, TERRA, 600, 'middle'))
    p.append(txt(fx - 155, fy - 44, '眉间', 13, TERRA, 600, 'end'))
    p.append(txt(fx - 16, fy - 72, '滑车上动脉', 12, TERRA, 600, 'end'))
    p.append(txt(fx + 16, fy - 72, '眶上动脉', 12, TERRA, 600, 'start'))
    p.append(txt(fx, fy + 92, '鼻背 · 面动脉终末支', 12, TERRA, 600, 'middle'))
    p.append(txt(lx + 24, ly + lh_ - 20, '圆区为血管逆行入眼风险区，文献报道填充注射致视力丧失数十例', 12.5, SUB))
    p.append(txt(lx + 24, ly + lh_ - 42, '高危区不是禁区，是路径与压力管理必须升级的区域', 13, INK, 600))
    # 右 组织层次
    rx_, ry, rw, rh = 620, 164, 400, 560
    p.append(rect(rx_, ry, rw, rh, rx=16, fill=CARD, stroke=LINE))
    p.append(txt(rx_ + 24, ry + 38, '面部组织层次与注射带（示意）', 18, INK, 700))
    bands = [
        ('表皮', '屏障，禁常规注射', 0),
        ('真皮', '色素与胶原，水光注射带', 1),
        ('皮下脂肪', '浅层填充与衔接带', 2),
        ('SMAS 与表情肌', '血管与神经密集，慎入区', 3),
        ('骨膜上层', '深层填充主流层次', 4),
    ]
    by, bh2, bg2 = ry + 66, 76, 12
    for i, (bn, note, ci) in enumerate(bands):
        y = by + i * (bh2 + bg2)
        p.append(rect(rx_ + 24, y, 190, bh2, rx=10, fill=SCALE7[6 - ci], stroke='none'))
        p.append(txt(rx_ + 119, y + bh2 / 2 + 6, bn, 16.5, TEAL_DK if ci >= 2 else '#FFFFFF', 700, 'middle'))
        p.append(line(rx_ + 226, y + bh2 / 2, rx_ + 244, y + bh2 / 2, LINE, 1.2))
        p.append(mtext(rx_ + 252, y + bh2 / 2 - 8, [note], 12.5, SUB, anchor='start'))
    p.append(txt(rx_ + 24, ry + rh - 40, '由浅入深，层次选择即靶点选择', 13, INK, 600))
    p.append(txt(rx_ + 24, ry + rh - 20, '层次错配是效果不佳与结节的主要原因之一', 12.5, SUB))
    return ''.join(p) + '</svg>'


# ---------- 图 03 设备与材料 ----------
def fig03():
    w, h = 1080, 960
    p = page(w, h, '03', '设备层与材料层，框架与写入', '设备像框架，提供能力平台；材料像数据，层次与剂量是写入位置')
    lx, rx_, y0 = 60, 580, 166
    p.append(rect(lx, y0, 480, 610, rx=16, fill=CARD, stroke=LINE))
    p.append(rect(rx_, y0, 440, 610, rx=16, fill=CARD, stroke=LINE))
    p.append(rect(lx, y0, 480, 52, rx=16, fill=TEAL))
    p.append(rect(lx, y0 + 26, 480, 26, rx=0, fill=TEAL, stroke=None))
    p.append(txt(lx + 24, y0 + 34, '设备层 · 框架', 19, '#FFFFFF', 700))
    p.append(rect(rx_, y0, 440, 52, rx=16, fill=TEAL))
    p.append(rect(rx_, y0 + 26, 440, 26, rx=0, fill=TEAL, stroke=None))
    p.append(txt(rx_ + 24, y0 + 34, '材料层 · 写入', 19, '#FFFFFF', 700))
    dev = [
        ('光 · 激光与强光', [('剥脱点阵（二氧化碳、铥）', '按产品注册'), ('调 Q 与皮秒', '按产品注册'), ('强脉冲光', '按产品注册')]),
        ('电 · 射频', [('射频治疗仪', '三类证（2024 起）')]),
        ('声 · 聚焦超声', [('聚焦超声皮肤治疗仪', '三类证（2025 首证）')]),
    ]
    mat = [
        ('注射', [('A 型肉毒毒素 · 剂量与弥散', '毒麻类管理'), ('透明质酸 · 黏弹性与层次', '三类器械，可溶解'), ('胶原与再生材料', '三类器械，起效有周期')]),
        ('外用与口服', [('维 A 酸类、氨甲环酸、防晒', '证据分层使用')]),
    ]

    def items(x, y, groups, tagfill):
        for gname, rows in groups:
            p.append(txt(x + 24, y + 26, gname, 16, INK, 700))
            y += 40
            for nm, tg in rows:
                p.append(rect(x + 24, y, 392 if x == lx else 356, 44, rx=10, fill=BG, stroke=LINE, sw=1))
                p.append(txt(x + 40, y + 28, nm, 14.5, INK))
                pw = tw(tg, 11.5) + 18
                p.append(rect(x + 24 + (392 if x == lx else 356) - pw - 12, y + 10, pw, 24, rx=12, fill=tagfill))
                p.append(txt(x + 24 + (392 if x == lx else 356) - pw / 2 - 12, y + 27, tg, 11.5, '#FFFFFF', 600, 'middle'))
                y += 54
            y += 14
        return y
    items(lx, y0 + 52, dev, TEAL)
    items(rx_, y0 + 52, mat, GOLD)
    ys = y0 + 640
    c1, _, _ = pill_c(280, ys, '设备层的思维是参数思维', 14.5, TEAL_DK, '#FFFFFF', h=40)
    c2, _, _ = pill_c(800, ys, '材料层的思维是层次思维', 14.5, '#8A6A33', '#FFFFFF', h=40)
    p.append(c1)
    p.append(c2)
    p.append(rect(60, ys + 58, 960, 66, rx=12, fill=BG, stroke=LINE))
    p.append(txt(540, ys + 85, '价格量级（渠道行情与公开报道，2026-08，估算需复核）', 13.5, INK, 600, 'middle'))
    p.append(txt(540, ys + 108, '国产二氧化碳点阵 10 至 20 万 · 国产铥激光 40 至 50 万 · 热玛吉探头约 8000 元一次 · 皮秒蜂巢探头约 8 万', 13, SUB, 400, 'middle'))
    return ''.join(p) + '</svg>'


# ---------- 图 04 围治疗期时间轴 ----------
def fig04():
    w, h = 1080, 660
    p = page(w, h, '04', '围治疗期，医生的运维时间轴', '价值的一半在治疗之外，术前、术中、术后、随访各有节点')
    nodes = [
        ('术前', ['筛查清单', '基线影像', '知情同意']),
        ('治疗日', ['查对制度', '参数记录', '术中观察']),
        ('72 小时', ['反应高峰期', '异常识别', '首次回访']),
        ('1 至 2 周', ['结痂与修复', '屏障管理', '复诊节点']),
        ('1 至 3 月', ['效果评估', '方案迭代', '长期档案']),
    ]
    y = 250
    p.append(line(100, y, 980, y, LINE, 2.4))
    xs = [130, 345, 560, 775, 990]
    for (nm, bl), x in zip(nodes, xs):
        p.append(circle(x, y, 9, TEAL))
        p.append(circle(x, y, 4.5, '#FFFFFF'))
        p.append(txt(x, y - 40, nm, 19, INK, 700, 'middle'))
        p.append(mtext(x, y + 40, bl, 13.5, SUB, lh=25, anchor='middle'))
    for x1, x2 in zip(xs[:-1], xs[1:]):
        p.append(line(x1 + 16, y, x2 - 18, y, TEAL, 2.4, marker='ar'))
    y2 = 420
    grades = [
        ('预期内反应', '红肿、轻微胀痛，按术后须知观察与随访', '#E7F2EE', TEAL_DK),
        ('需处置', '持续红斑、色素异常征兆，预约面诊评估', GOLD_BG, '#8A6A33'),
        ('急症', '剧烈疼痛、皮肤发白或视力症状，立即启动急救与转诊', TERRA_BG, TERRA),
    ]
    for i, (g, d, bgc, fc) in enumerate(grades):
        yy = y2 + i * 58
        p.append(rect(70, yy, 940, 46, rx=10, fill=bgc, stroke=fc, sw=1))
        p.append(txt(94, yy + 29, g, 15.5, fc, 700))
        p.append(txt(250, yy + 29, d, 13.5, SUB))
    p.append(txt(70, y2 - 12, '并发症的三级分诊，处置动作随级别切换', 15, INK, 600))
    return ''.join(p) + '</svg>'


# ---------- 图 05 咨询师与 SC 对照 ----------
def fig05():
    w, h = 1080, 1030
    p = page(w, h, '05', '咨询师的技术栈，与 SC 逐层对照', '同构六层来自翻译者岗位的通例，第七层是医疗行业特有')
    c1, _, _ = pill_c(280, 158, '医美咨询师', 18, TEAL, '#FFFFFF', h=46)
    c2, _, _ = pill_c(800, 158, 'SC 售前顾问', 18, BLUE, '#FFFFFF', h=46)
    p.append(c1)
    p.append(c2)
    rows = [
        ('行业结构层', '行业知识'),
        ('医学常识层', '技术广度'),
        ('项目知识层', '产品知识'),
        ('方案层', '方案撰写'),
        ('呈现层', '演示宣讲'),
        ('流程客户层', '项目管理与客户关系'),
        ('边界层', '（无对应层）'),
    ]
    y = 224
    rh, gap = 84, 11
    for i, (a, b) in enumerate(rows):
        special = (i == 6)
        p.append(rect(70, y, 420, rh, rx=12, fill=TERRA_BG if special else SCALE7[min(6, i + 1)], stroke=TERRA if special else 'none', sw=1.4))
        p.append(txt(94, y + 35, a, 18, TERRA if special else ('#FFFFFF' if i <= 2 else TEAL_DK), 700))
        p.append(txt(94, y + 62, '不诊断 不处方 不承诺' if special else ['项目、分级、价格体系', '皮肤常识与转诊信号', '适应症 疗程 恢复期', '主诉转译与报价结构', '面诊 案例报告解读', '接待到随访全流程'][i], 13, TERRA if special else SUB))
        p.append(rect(590, y, 420, rh, rx=12, fill=BLUE_BG if not special else '#F1F3F6', stroke='none'))
        p.append(txt(614, y + 35, b, 18, BLUE if not special else SUB, 700))
        p.append(txt(614, y + 62, ['行业格局与政策', '云、网络、数据库常识', '产品功能与边界', '方案建议书与报价', 'PPT 与系统演示', '招投标与客户维护', '医疗行为法定归属医师'][i], 13, SUB))
        badge = '分野' if special else '同构'
        cb, _, _ = pill_c(540, y + rh / 2 - 14, badge, 12.5, TERRA if special else SUB, '#FFFFFF', h=28)
        p.append(cb)
        if not special:
            p.append(line(494, y + rh / 2, 586, y + rh / 2, LINE, 1.4, dash='4 4'))
        y += rh + gap
    ys = y + 8
    p.append(rect(70, ys, 940, 62, rx=12, fill=CARD, stroke=LINE))
    steps = ['无国家职业准入', '中整协标准起草', '规范化培训', '职业技能认定（进行中）']
    x = 96
    for i, s in enumerate(steps):
        p.append(txt(x, ys + 38, s, 14.5, INK if i < 3 else TEAL, 600))
        xw = tw(s, 14.5)
        if i < len(steps) - 1:
            p.append(line(x + xw + 12, ys + 33, x + xw + 58, ys + 33, SUB, 1.8, marker='arG'))
        x += xw + 82
    return ''.join(p) + '</svg>'


# ---------- 图 06 主诉到报价 ----------
def fig06():
    w, h = 1080, 720
    p = page(w, h, '06', '方案层，从主诉到报价', '咨询师交付的是转译与结构，方案的终审权在医生')
    r1 = [('想变好看', '客人的原始主诉'), ('提问与转译', '开放式问诊技术'), ('需求轴归类', '质地 色素 黏膜'), ('项目组合', '适应症与疗程结构')]
    r2 = [('优先级排序', '先色素后质地之类次序'), ('报价结构', '单次 疗程 年度三层'), ('医生面诊确认', '方案归执业医师')]
    nw, nh, ny = 205, 84, 190
    xs1 = [90, 330, 570, 810]
    for (nm, sb), x in zip(r1, xs1):
        p.append(rect(x, ny, nw, nh, rx=14, fill=CARD, stroke=LINE, sw=1.6))
        p.append(txt(x + nw / 2, ny + 36, nm, 17.5, INK, 700, 'middle'))
        p.append(txt(x + nw / 2, ny + 62, sb, 12.5, SUB, 400, 'middle'))
    for x1, x2 in zip(xs1[:-1], xs1[1:]):
        p.append(line(x1 + nw + 8, ny + nh / 2, x2 - 10, ny + nh / 2, TEAL, 2.2, marker='ar'))
    xs2 = [90, 330, 570]
    ny2 = 400
    for i, (nm, sb) in enumerate(r2):
        x = xs2[i]
        last = (i == 2)
        p.append(rect(x, ny2, nw, nh, rx=14, fill=TERRA_BG if last else CARD, stroke=TERRA if last else LINE, sw=last and 2 or 1.6))
        p.append(txt(x + nw / 2, ny2 + 36, nm, 17.5, TERRA if last else INK, 700, 'middle'))
        p.append(txt(x + nw / 2, ny2 + 62, sb, 12.5, TERRA if last else SUB, 400, 'middle'))
    for x1, x2 in zip(xs2[:-1], xs2[1:]):
        p.append(line(x1 + nw + 8, ny2 + nh / 2, x2 - 10, ny2 + nh / 2, TEAL, 2.2, marker='ar'))
    p.append(path(f'M{xs1[-1] + nw / 2} {ny + nh + 8} V{ny2 - 14} H{xs2[0] + nw / 2}', TEAL, 2.2, marker='ar'))
    p.append(rect(810, ny2 - 24, 205, 132, rx=14, fill=GOLD_BG, stroke=GOLD, sw=1.2))
    p.append(txt(912, ny2 + 4, '排序逻辑示例', 14.5, '#8A6A33', 700, 'middle'))
    p.append(mtext(912, ny2 + 30, ['色素改善在前，质地重塑在后', '恢复期进入方案与告知', '年度规划按随访节点滚动'], 12.5, SUB, lh=24, anchor='middle'))
    ys = 590
    p.append(rect(90, ys, 900, 58, rx=12, fill=CARD, stroke=LINE))
    p.append(txt(540, ys + 36, '报价三层是信息结构，不是价格战术。单次对齐预期，疗程对齐依从性，年度对齐长期关系', 14.5, INK, 600, 'middle'))
    return ''.join(p) + '</svg>'


# ---------- 图 07 边界层 ----------
def fig07():
    w, h = 1080, 830
    p = page(w, h, '07', '边界层，专业性的来源', '四项医疗行为法定归属执业医师，边界不是天花板')
    p.append(rect(70, 176, 340, 320, rx=16, fill=CARD, stroke=TEAL, sw=1.6))
    p.append(txt(240, 216, '咨询师的工作面', 19, INK, 700, 'middle'))
    for i, s in enumerate(['主诉转译与需求归类', '流程、档案与随访', '项目知识科普与答疑', '案例与报告的规范讲解']):
        p.append(circle(108, 254 + i * 56, 4.5, TEAL))
        p.append(txt(124, 260 + i * 56, s, 15, INK))
    four = ['诊断', '处方', '治疗方案', '操作实施']
    for i, s in enumerate(four):
        y = 216 + i * 66
        c, _, _ = pill_c(540, y, s, 15.5, TERRA, '#FFFFFF', h=40)
        p.append(c)
        p.append(line(416, y + 20, 478, y + 20, TERRA, 1.8, marker='arT'))
    p.append(rect(640, 176, 340, 320, rx=16, fill=TERRA_BG, stroke=TERRA, sw=1.8))
    p.append(txt(810, 220, '执业医师负责', 19, TERRA, 700, 'middle'))
    p.append(mtext(810, 254, ['《医疗美容服务管理办法》确立执业医师负责制，', '诊断、处方、治疗方案、操作实施四项', '医疗行为由具备资质的医师完成。'], 14, SUB, lh=26, anchor='middle'))
    p.append(txt(810, 372, '边界让咨询师成为医疗团队的协作岗', 14.5, INK, 600, 'middle'))
    p.append(txt(810, 398, '而不是单兵作战的销售岗', 14.5, INK, 600, 'middle'))
    ys = 532
    p.append(rect(70, ys, 940, 96, rx=14, fill=CARD, stroke=LINE))
    p.append(txt(94, ys + 32, '转诊信号，出现即进入医生面诊流程', 16, INK, 700))
    p.append(txt(94, ys + 60, '疼痛异常 · 皮肤感染迹象 · 妊娠可能或光电禁忌史 · 期望值明显偏离沟通结果 · 未成年客人（须监护人知情同意流程）', 14, SUB))
    p.append(txt(94, ys + 82, '转诊是接口质量，不是能力不足的标志', 13, TEAL, 600))
    ys2 = 648
    p.append(rect(70, ys2, 940, 118, rx=14, fill=BG, stroke=LINE))
    p.append(txt(94, ys2 + 30, '宣传合规的五条重点（《医疗美容广告执法指南》，市场监管总局 2021）', 15.5, INK, 700))
    items5 = ['不制造容貌焦虑', '不作疗效承诺', '不用患者形象作对比证明', '不用医生与专业人士代言', '不面向未成年人发布']
    x = 94
    for s in items5:
        c, cw2, _ = pill(x, ys2 + 50, s, 13, '#FFFFFF', TEAL_DK, h=34)
        p.append(c)
        x += cw2 + 14
    p.append(txt(94, ys2 + 106, '执法指南为监管与内容创作的共同边界，正面科普空间因此更清晰', 13, SUB))
    return ''.join(p) + '</svg>'


# ---------- 图 08 机构八系统 ----------
def fig08():
    w, h = 1080, 930
    p = page(w, h, '08', '医美机构的技术栈，八个系统', '个人栈讲深度与广度，机构栈讲系统完整与接口质量')
    systems = [
        ('S1 资质系统', ['执业许可与诊疗科目', '机构形态与项目分级', '人员资质档案'], '合规与证照', False),
        ('S2 人才系统', ['岗位最小配置', '培训体系与演练', '职业路径设计'], '团队与梯队', False),
        ('S3 设备供应链系统', ['设备组合策略', '药品耗材溯源', '注册证核验'], '基础设施', False),
        ('S4 诊疗流程系统', ['面诊到随访 SOP', '知情同意与病历', '序贯排程规则'], '研发流水线', False),
        ('S5 质量安全系统', ['感控体系', '急救预案与演练', '不良事件闭环'], '监控与告警', True),
        ('S6 客户系统', ['治疗史与影像档案', '随访节点体系', '长周期客户资产'], '用户运营', False),
        ('S7 获客品牌系统', ['专业科普内容', '平台合规运营', '口碑与转介绍'], '市场与增长', False),
        ('S8 经营系统', ['定价三层体系', '成本与财务合规', '经营数据看板'], '商业化与财务', False),
    ]
    cw2, ch = 232, 268
    xs = [70, 320, 570, 820]
    ys = [176, 466]
    for i, (nm, its, tag, gold) in enumerate(systems):
        x, y = xs[i % 4], ys[i // 4]
        p.append(rect(x, y, cw2, ch, rx=16, fill=CARD, stroke=GOLD if gold else LINE, sw=gold and 2 or 1.4))
        if gold:
            p.append(rect(x, y, cw2, 12, rx=6, fill=GOLD, stroke=None))
        p.append(txt(x + 20, y + 48, nm, 17.5, INK, 700))
        for j, it in enumerate(its):
            p.append(circle(x + 28, y + 86 + j * 40, 3.5, TEAL))
            p.append(mtext(x + 42, y + 92 + j * 40, [it], 13.5, SUB))
        c, _, _ = pill(x + 20, y + ch - 46, tag, 12, GOLD if gold else TEAL, '#FFFFFF', h=28)
        p.append(c)
    ys3 = 766
    p.append(rect(70, ys3, 982 - 88, 92, rx=14, fill=TEAL_DK, stroke=None))
    p.append(txt(540, ys3 + 38, '一个系统缺失，其他系统的产出都会衰减', 17, '#FFFFFF', 700, 'middle'))
    p.append(txt(540, ys3 + 66, '机构形态与人员配置依据《美容医疗机构、医疗美容科（室）基本标准（试行）》', 12.5, '#C9DED7', 400, 'middle'))
    p.append(txt(540, ys3 + 84, '经营结果是栈的输出', 12.5, '#C9DED7', 400, 'middle'))
    return ''.join(p) + '</svg>'


# ---------- 图 09 流程与安全回路 ----------
def fig09():
    w, h = 1080, 730
    p = page(w, h, '09', '诊疗流程系统与安全回路', '流程向前跑，安全回路把问题送回系统')
    names = ['面诊', '评估', '方案', '知情同意', '查对', '治疗', '术后观察', '随访']
    nw, nh, ny = 106, 66, 196
    xs = [64 + i * (nw + 18) for i in range(8)]
    for nm, x in zip(names, xs):
        p.append(rect(x, ny, nw, nh, rx=12, fill=CARD, stroke=LINE, sw=1.6))
        p.append(txt(x + nw / 2, ny + 40, nm, 16, INK, 700, 'middle'))
    for x1, x2 in zip(xs[:-1], xs[1:]):
        p.append(line(x1 + nw + 2, ny + nh / 2, x2 - 8, ny + nh / 2, TEAL, 2, marker='ar'))
    fy = 380
    p.append(path(f'M{xs[7] + nw / 2} {ny + nh + 8} V{fy} H{988}', SUB, 1.8, dash='5 5'))
    chips = ['不良事件与投诉', '上报', '复盘', '修订流程']
    cx = 880
    cw2s = [tw(c, 14.5) + 30 for c in chips]
    total = sum(cw2s) + 3 * 24
    x = 990 - total
    for i, (c, cwd) in enumerate(zip(chips, cw2s)):
        p.append(rect(x, fy - 21, cwd, 42, rx=21, fill='#F1F3F0', stroke=SUB, sw=1.2))
        p.append(txt(x + cwd / 2, fy + 5, c, 14.5, INK, 600, 'middle'))
        if i < 3:
            p.append(line(x + cwd + 4, fy, x + cwd + 20, fy, SUB, 1.6, marker='arG'))
        x += cwd + 24
    p.append(path(f'M{64 + 26} {fy} H{xs[0] + nw / 2}', SUB, 1.8, dash='5 5', marker='arG'))
    p.append(path(f'M{xs[0] + nw / 2} {fy} V{ny + nh + 10}', SUB, 1.8, dash='5 5', marker='arG'))
    p.append(txt(540, fy + 34, '回路不指向个人，指向流程版本的更新', 13.5, SUB, 400, 'middle'))
    ys = 500
    refs = ['十八项医疗质量安全核心制度（2018 年要点）', '病历书写基本规范', '医疗机构消毒技术规范']
    x = 90
    for s in refs:
        cwd = tw(s, 13.5) + 34
        p.append(rect(x, ys, cwd, 44, rx=10, fill=BG, stroke=LINE))
        p.append(txt(x + cwd / 2, ys + 28, s, 13.5, INK, 600, 'middle'))
        x += cwd + 20
    p.append(rect(90, ys + 62, 910, 56, rx=12, fill=CARD, stroke=LINE))
    p.append(txt(540, ys + 96, '知情同意是流程节点而不是签字动作，要素、风险、替代方案与恢复期都在其中', 14.5, INK, 600, 'middle'))
    return ''.join(p) + '</svg>'


# ---------- 图 10 经营与客户看板 ----------
def fig10():
    w, h = 1080, 760
    p = page(w, h, '10', '经营系统与客户系统，看板与飞轮', '指标健康的前提，是前面六个系统都真实存在')
    # 左 定价三层
    p.append(rect(60, 166, 300, 430, rx=16, fill=CARD, stroke=LINE))
    p.append(txt(210, 202, '定价三层', 18, INK, 700, 'middle'))
    bars = [('单次体验', 100, '对齐预期', 5), ('疗程套餐', 140, '对齐依从性', 3), ('年度规划', 170, '对齐长期关系', 1)]
    for i, (nm, bw2, sb, ci) in enumerate(bars):
        y = 240 + i * 106
        p.append(rect(80, y, bw2, 52, rx=10, fill=SCALE7[ci], stroke='none'))
        p.append(txt(80 + bw2 + 14, y + 24, nm, 14.5, INK, 700))
        p.append(txt(80 + bw2 + 14, y + 44, sb, 12, SUB))
    p.append(txt(210, 570, '价格是信息，分层即透明', 13.5, TEAL, 600, 'middle'))
    # 中 飞轮
    cx, cy, r = 540, 390, 148
    p.append(rect(370, 166, 340, 430, rx=16, fill=CARD, stroke=LINE))
    p.append(txt(540, 202, '信任飞轮', 18, INK, 700, 'middle'))
    import math
    nodes6 = ['获客', '到店', '交付', '信任', '复购', '转介绍']
    pts = []
    for i in range(6):
        a = math.radians(-90 + i * 60)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) - 14))
    for i in range(6):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 6]
        p.append(path(f'M{x1:.0f} {y1:.0f} Q{cx} {cy - 14} {x2:.0f} {y2:.0f}', TEAL, 1.5, marker=None, opacity=0.55))
        mx, my = (x1 + 2 * cx + x2) / 4, (y1 + 2 * (cy - 14) + y2) / 4
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        p.append(f'<path d="M-5,-4 L6,0 L-5,4 z" fill="{TEAL}" opacity="0.75" '
                 f'transform="translate({mx:.0f},{my:.0f}) rotate({ang:.0f})"/>')
    for i, (nm, (nx, ny2)) in enumerate(zip(nodes6, pts)):
        cwd = tw(nm, 14) + 26
        p.append(rect(nx - cwd / 2, ny2 - 17, cwd, 34, rx=17, fill=TEAL if nm == '信任' else CARD, stroke=TEAL, sw=1.4))
        p.append(txt(nx, ny2 + 5, nm, 14, '#FFFFFF' if nm == '信任' else TEAL_DK, 700, 'middle'))
    p.append(txt(540, cy + r + 42, '复购节奏以医疗需求为依据', 13.5, SUB, 400, 'middle'))
    # 右 指标卡
    p.append(rect(730, 166, 290, 430, rx=16, fill=CARD, stroke=LINE))
    p.append(txt(875, 202, '三个指标', 18, INK, 700, 'middle'))
    kpis = [('复购率', '年度内重复消费客人占比'), ('设备利用率', '治疗人次与设备产能之比'), ('单客年度周期', '客单价与到店频次的乘积')]
    for i, (k, d) in enumerate(kpis):
        y = 232 + i * 112
        p.append(rect(752, y, 246, 92, rx=12, fill=BG, stroke=LINE))
        p.append(txt(772, y + 36, k, 16.5, INK, 700))
        p.append(mtext(772, y + 62, [d], 13, SUB))
    ys = 620
    p.append(rect(60, ys, 960, 62, rx=12, fill=BG, stroke=LINE))
    p.append(txt(540, ys + 26, '设备回收期算例沿用行业观察 01', 13.5, INK, 600, 'middle'))
    p.append(txt(540, ys + 47, '月治疗 100 人次、单次 1500 至 4000 元（估算），回收期两个月至半年。实际取决于获客、复购与定价三个经营变量', 12.5, SUB, 400, 'middle'))
    return ''.join(p) + '</svg>'


FIGS = {
    'fig-00-三栈总览.svg': fig00,
    'fig-01-医生技术栈七层全景.svg': fig01,
    'fig-02-面部危险区与组织层次.svg': fig02,
    'fig-03-设备与材料两层地图.svg': fig03,
    'fig-04-围治疗期时间轴.svg': fig04,
    'fig-05-咨询师栈与SC栈对照.svg': fig05,
    'fig-06-从主诉到报价.svg': fig06,
    'fig-07-边界层四条红线.svg': fig07,
    'fig-08-机构八系统全景.svg': fig08,
    'fig-09-诊疗流程与安全回路.svg': fig09,
    'fig-10-经营与客户看板.svg': fig10,
}

if __name__ == '__main__':
    ok = True
    for name, fn in FIGS.items():
        svg = fn()
        try:
            minidom.parseString(svg.encode('utf-8'))
        except Exception as e:
            ok = False
            print(f'[BAD ] {name}: {e}')
            continue
        (OUT / name).write_text(svg, encoding='utf-8')
        print(f'[OK  ] {name}  {len(svg)} bytes')
    print('ALL OK' if ok else 'HAS ERRORS')
