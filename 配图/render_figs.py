# -*- coding: utf-8 -*-
"""用无头 Chrome 把本目录的 SVG 渲染成 PNG。用法 python render_figs.py [scale] [outdir]"""
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
HERE = Path(__file__).parent


def render(svg: Path, out: Path, scale: float = 1.0):
    head = svg.read_text(encoding='utf-8')[:400]
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', head)
    w, h = int(m.group(1)), int(m.group(2))
    url = 'file:///' + quote(str(svg).replace('\\', '/'), safe=':/')
    cmd = [CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
           f'--force-device-scale-factor={scale}',
           f'--window-size={w},{h}',
           f'--screenshot={out}', url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return out.exists(), (r.stderr or r.stdout)[-200:]


if __name__ == '__main__':
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    outdir = HERE / (sys.argv[2] if len(sys.argv) > 2 else '走查')
    outdir.mkdir(exist_ok=True)
    for svg in sorted(HERE.glob('fig-*.svg')):
        out = outdir / (svg.stem + '.png')
        ok, log = render(svg, out, scale)
        print(('OK  ' if ok else 'FAIL') + f' {out.name}  {log.strip()[:80] if not ok else ""}')
