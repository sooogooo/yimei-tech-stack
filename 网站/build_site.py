# -*- coding: utf-8 -*-
"""医美技术栈静态网站构建脚本。读取系列 md 源文件，生成 index.html 与全部文章页。
用法 python build_site.py。输出在本目录，配图 SVG 从 ../配图 拷入 ./配图。"""
import re
import shutil
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent

DOCS = [
    (None, ROOT / '00-系列总览.md'),
    (1, ROOT / '医生篇/01-美容医生的技术栈全景.md'),
    (2, ROOT / '医生篇/02-医生的底层语言是解剖.md'),
    (3, ROOT / '医生篇/03-设备与材料，医生栈的两层核心.md'),
    (4, ROOT / '医生篇/04-医生的运维，围治疗期管理.md'),
    (5, ROOT / '咨询师篇/05-医美咨询师的技术栈全景.md'),
    (6, ROOT / '咨询师篇/06-咨询师的方案层，从主诉到报价.md'),
    (7, ROOT / '咨询师篇/07-咨询师的边界层，专业性的来源.md'),
    (8, ROOT / '机构篇/08-医美机构的技术栈全景.md'),
    (9, ROOT / '机构篇/09-机构的流程与安全系统.md'),
    (10, ROOT / '机构篇/10-机构的经营与客户系统.md'),
]

TOC = [
    (None, '系列总览', '总览', '三张栈图的体例、立场与目录，系列的入口'),
    (1, '美容医生的技术栈全景', '医生篇', '七层地图。专业能力是可核对的清单，医生的价值有结构可依'),
    (2, '医生的底层语言是解剖', '医生篇', '血管地图与组织层次，决定注射与光电的全部边界'),
    (3, '设备与材料，医生栈的两层核心', '医生篇', '能量源像框架，注射物像写入。参数思维与层次思维'),
    (4, '医生的运维，围治疗期管理', '医生篇', '评估、修复、并发症处置与随访。价值的一半在治疗之外'),
    (5, '医美咨询师的技术栈全景', '咨询师篇', '对标售前顾问。医疗语境的翻译者，广度优先的七层栈'),
    (6, '咨询师的方案层，从主诉到报价', '咨询师篇', '主诉转译、组合排序与报价结构。专业服务的核心交付'),
    (7, '咨询师的边界层，专业性的来源', '咨询师篇', '不诊断、不处方、不承诺。与医生的接口和转诊路径'),
    (8, '医美机构的技术栈全景', '机构篇', '八个系统。机构是组织能力，经营结果是栈的输出'),
    (9, '机构的流程与安全系统', '机构篇', '标准流程与质量体系，稳定交付与信任的制度来源'),
    (10, '机构的经营与客户系统', '机构篇', '获客、定价与客户资产。长期信任的结构基础'),
]

PILLARS = [
    ('医生篇 · 01 至 04', '美容医生的七层栈', '准入、底层语言、设备、材料、评估、规范安全、审美沟通。纵深型技术栈，对标 IT 工程师。', '01-美容医生的技术栈全景.html'),
    ('咨询师篇 · 05 至 07', '医美咨询师的七层栈', '行业结构、医学常识、项目知识、方案、呈现、流程客户，加医疗特有的边界层。对标售前顾问 SC。', '05-医美咨询师的技术栈全景.html'),
    ('机构篇 · 08 至 10', '医美机构的八个系统', '资质、人才、供应链、流程、质量安全、客户、获客、经营。组织能力栈，对标工程组织。', '08-医美机构的技术栈全景.html'),
]

FAVICON = ('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22>'
           '<rect width=%2224%22 height=%2224%22 rx=%225%22 fill=%22%230E6E5F%22/>'
           '<rect x=%228%22 y=%228%22 width=%228%22 height=%228%22 rx=%222%22 fill=%22%23C9A063%22/></svg>')


def inline(s):
    s = escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return s


def render_table(rows):
    parsed = []
    for r in rows:
        cells = [c.strip() for c in r.strip().strip('|').split('|')]
        parsed.append(cells)
    if len(parsed) >= 2 and all(re.fullmatch(r':?-{3,}:?', c) for c in parsed[1]):
        parsed.pop(1)
    body = []
    for ri, cells in enumerate(parsed):
        tag = 'th' if ri == 0 else 'td'
        body.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
    return '<table>' + ''.join(body) + '</table>'


def md_to_html(lines):
    out, i, appendix = [], 0, False
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s == '---':
            out.append('<hr>')
            i += 1
            continue
        m = re.match(r'^(#{1,3})\s+(.*)', s)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if lvl == 2 and txt.startswith('附'):
                if out and out[-1] == '<hr>':
                    out.pop()
                out.append('<div class="appendix">')
                appendix = True
            out.append(f'<h{lvl}>{inline(txt)}</h{lvl}>')
            i += 1
            continue
        if s.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue
        if s.startswith('!['):
            m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', s)
            alt, src = m.group(1), m.group(2).replace('../配图/', '配图/')
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            cap = ''
            if j < len(lines) and re.fullmatch(r'\*[^*].*\*', lines[j].strip()):
                cap = lines[j].strip()[1:-1]
                i = j
            i += 1
            fig = f'<figure><img src="{src}" alt="{escape(alt, quote=False)}" loading="lazy">'
            if cap:
                fig += f'<figcaption>{inline(cap)}</figcaption>'
            out.append(fig + '</figure>')
            continue
        if re.match(r'^[-*]\s+', s):
            items = []
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                items.append(inline(re.sub(r'^[-*]\s+', '', lines[i].strip())))
                i += 1
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
            continue
        if re.match(r'^\d+\.\s+', s):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                items.append(inline(re.sub(r'^\d+\.\s+', '', lines[i].strip())))
                i += 1
            out.append('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>')
            continue
        para = [s]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt == '---' or nxt.startswith(('|', '#', '![', '> '))
                    or re.match(r'^[-*]\s+', nxt) or re.match(r'^\d+\.\s+', nxt)):
                break
            para.append(nxt)
            i += 1
        out.append('<p>' + inline(' '.join(para)) + '</p>')
    if appendix:
        out.append('</div>')
    return out


def parse_doc(path):
    lines = path.read_text(encoding='utf-8').splitlines()
    title = cover = meta = None
    rest = []
    for ln in lines:
        st = ln.strip()
        if title is None and st.startswith('# '):
            title = st[2:].strip()
            continue
        if cover is None and st.startswith('> '):
            cover = st[2:].strip()
            continue
        if meta is None and re.fullmatch(r'\*[^*].*\*', st):
            meta = st[1:-1]
            continue
        rest.append(ln)
    while rest and not rest[0].strip():
        rest.pop(0)
    if rest and rest[0].strip() == '---':
        rest.pop(0)
    plain = re.sub(r'[#*>|!\[\]()`*-]', '', '\n'.join(rest))
    minutes = max(1, round(len(re.sub(r'\s', '', plain)) / 480))
    return title, cover, meta, rest, minutes


def head_html(title):
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)} · 医美技术栈</title>'
            f'<link rel="icon" href="{FAVICON}">'
            '<link rel="stylesheet" href="assets/style.css"></head><body>')


def site_head():
    return ('<header class="site-head"><div class="wrap">'
            '<a class="brand" href="index.html"><span class="brand-dot"></span>医美技术栈</a>'
            '<nav class="site-nav"><a href="index.html#zhuti">三主体</a>'
            '<a href="index.html#mulu">目录</a><a href="index.html#guanyu">关于</a></nav></div></header>')


def site_foot():
    return ('<footer class="site-foot"><div class="wrap">'
            '<span>医美技术栈 · B 端系列 · 对标 IT 工程师与 SC 售前顾问的栈图体例</span>'
            '<span>事实核验 2026-08-18</span></div></footer></body></html>')


def pn_card(lab, title, href, cls=''):
    if href is None:
        return f'<div class="pn {cls}"><div class="lab">{lab}</div></div>'
    return (f'<a class="pn {cls}" href="{href}"><div class="lab">{lab}</div>'
            f'<div class="t">{escape(title)}</div></a>')


def slug(num):
    for n, _, _, _ in TOC:
        if n == num:
            pass
    return None


def main():
    figs_src = ROOT / '配图'
    figs_dst = HERE / '配图'
    figs_dst.mkdir(exist_ok=True)
    for f in figs_src.glob('fig-*.svg'):
        shutil.copy2(f, figs_dst / f.name)

    parsed = {}
    files = {}
    for num, path in DOCS:
        title, cover, meta, rest, minutes = parse_doc(path)
        body = md_to_html(rest)
        slugname = path.stem + '.html'
        parsed[num] = dict(title=title, cover=cover, meta=meta, body=body,
                           minutes=minutes, slug=slugname)
        files[num] = slugname

    order = [n for n, _ in DOCS]
    for idx, num in enumerate(order):
        d = parsed[num]
        cat = next(c for n, _, c, _ in TOC if n == num)
        chip = '系列总览' if num is None else f'第 {num:02d} 篇 · {cat}'
        chip_cls = ' gold' if num is None else ''
        prev_n, next_n = (order[idx - 1] if idx > 0 else None,
                          order[idx + 1] if idx < len(order) - 1 else None)
        pn = '<div class="pn-nav">'
        pn += pn_card('上一篇', parsed[prev_n]['title'], files[prev_n]) if prev_n else pn_card('系列起点', '', None)
        pn += pn_card('下一篇', parsed[next_n]['title'], files[next_n], 'next') if next_n else pn_card('系列完 · 感谢阅读', '', None, 'next')
        pn += '</div>'
        html = [
            head_html(d['title']),
            site_head(),
            '<main class="article">',
            '<div class="crumbs"><a href="index.html">首页</a> / ' + escape(cat) + '</div>',
            f'<span class="chip{chip_cls}">{chip}</span>',
            f'<h1>{escape(d["title"])}</h1>',
            f'<blockquote class="cover">{inline(d["cover"])}</blockquote>',
            f'<p class="meta">{inline(d["meta"])} · 约 {d["minutes"]} 分钟读完</p>',
            '\n'.join(d['body']),
            pn,
            '</main>',
            site_foot(),
        ]
        (HERE / files[num]).write_text('\n'.join(html), encoding='utf-8')
        print(f'[PAGE] {files[num]}')

    toc_rows = []
    for num, title, cat, desc in TOC:
        badge = '总览' if num is None else f'{num:02d}'
        cls = ' overview' if num is None else ''
        href = files[num]
        toc_rows.append(
            f'<a class="toc-row" href="{href}"><span class="toc-num{cls}">{badge}</span>'
            f'<span class="toc-main"><span class="t">{escape(title)}</span>'
            f'<span class="d">{escape(desc)}</span></span>'
            f'<span class="toc-cat">{cat}</span></a>')

    pillars = ''.join(
        f'<div class="pillar"><span class="tag">{escape(t)}</span><h3>{escape(h)}</h3>'
        f'<p>{escape(d)}</p><a class="more" href="{href}">进入全景篇 →</a></div>'
        for t, h, d, href in PILLARS)

    index = [
        head_html('医美的技术栈 · 三张栈图读懂医美的专业结构'),
        '<div class="hero"><div class="wrap">',
        '<span class="hero-kicker">B 端系列 · 电子刊专题</span>',
        '<h1>医美的技术栈</h1>',
        '<p class="hero-sub">把美容医生、医美咨询师、医美机构的专业能力画成三张技术栈地图，'
        '对标 IT 行业最成熟的栈图体例。专业一旦成为可核对、可学习、可升级的清单，就不再依赖形容词。</p>',
        '<div class="hero-actions"><a class="btn btn-primary" href="00-系列总览.html">从系列总览读起</a>'
        '<a class="btn btn-ghost" href="#mulu">查看全部篇目</a></div>',
        '<div class="hero-fig"><img src="配图/fig-00-三栈总览.svg" alt="三张技术栈总览"></div>',
        '</div></div>',
        '<div class="wrap">',
        '<div class="pillars" id="zhuti">' + pillars + '</div>',
        '<section class="section" id="mulu"><div class="section-title">全部篇目</div>'
        '<div class="toc">' + ''.join(toc_rows) + '</div></section>',
        '<section class="section" id="guanyu"><div class="about">'
        '<h3>关于这个系列</h3>'
        '<p>医生对标 IT 工程师，咨询师对标售前顾问 SC，机构对标工程组织。同构带来体例，分野来自医疗属性，'
        '多出来的规范安全层、边界层与质量安全系统，正是这个行业专业性的制度表达。'
        '论证只用五类可核验信息，即法规与资质、临床证据与共识、并发症数据、价格量级与监管类别。</p>'
        '<p class="fine">三张全景图（图 1、图 5、图 8）可独立用于招聘核对与培训材料。'
        '文中法规与价格信息核验至 <b>2026 年 8 月 18 日</b>，发布前逐条复核。本文刊内容不构成医疗与投资建议。</p>'
        '</div></section>',
        '</div>',
        site_foot(),
    ]
    (HERE / 'index.html').write_text('\n'.join(index), encoding='utf-8')
    print('[PAGE] index.html')

    # 自检：本地链接与图片引用是否都存在
    bad = []
    for htmlf in HERE.glob('*.html'):
        text = htmlf.read_text(encoding='utf-8')
        for m in re.finditer(r'(?:href|src)="([^"#]+)"', text):
            u = m.group(1)
            if u.startswith(('http', 'data:')):
                continue
            if not (htmlf.parent / u).exists():
                bad.append(f'{htmlf.name} -> {u}')
    if bad:
        print('[CHECK] 缺失引用：')
        for b in bad:
            print('       ', b)
        raise SystemExit(1)
    print(f'[CHECK] {len(list(HERE.glob("*.html")))} 个页面的本地引用全部存在')


if __name__ == '__main__':
    main()
