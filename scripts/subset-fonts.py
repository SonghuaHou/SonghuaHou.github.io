"""Subset Alibaba PuHuiTi 2.0 to the CJK chars actually used on the site.
Downloads full TTFs from jsDelivr to a temp dir (not committed), emits small
woff2 files to public/fonts. Re-run after adding new Chinese copy.

Unicodes: used chars minus ASCII (Latin/digits stay on Sora).
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path('/Users/songhua/Downloads/portfolio')
TMP = Path('/private/var/folders/1b/wf3tlmpd4cj9skrmw1kmpdph0000gn/T/opencode/puhuiti')
FONTS = ROOT / 'public/fonts'
TMP.mkdir(parents=True, exist_ok=True)
FONTS.mkdir(parents=True, exist_ok=True)

WEIGHTS = {
    '55-Regular': 400,
    '65-Medium': 500,
    '75-SemiBold': 600,
    '85-Bold': 700,
}
HAVE_FILES = all((TMP / f'AlibabaPuHuiTi-2-{n}.ttf').exists() for n in WEIGHTS)

# 1. collect used chars from rendered sources
text = ''
for p in list((ROOT / 'src').rglob('*.astro')) + [ROOT / 'src/content/site.json']:
    text += p.read_text(encoding='utf-8')
chars = {c for c in text if ord(c) > 0x7F}
print(f'non-ascii chars used: {len(chars)}')

import subprocess
for name, weight in WEIGHTS.items():
    src = TMP / f'AlibabaPuHuiTi-2-{name}.ttf'
    if not src.exists():
        if HAVE_FILES:
            raise SystemExit(f'missing {src}, download via curl (see script header)')
        url = f'https://cdn.jsdelivr.net/npm/@fontpkg/alibaba-pu-hui-ti-2-0@2.0.2/AlibabaPuHuiTi-2-{name}.ttf'
        print('downloading', name)
        urllib.request.urlretrieve(url, src)
    dst = FONTS / f'AlibabaPuHuiTi-2-{name}.woff2'
    unicodes = ','.join(f'U+{ord(c):04X}' for c in sorted(chars))
    subprocess.run(['pyftsubset', str(src), f'--output-file={dst}',
                    '--flavor=woff2', '--with-zopfli',
                    f'--unicodes={unicodes}',
                    '--layout-features=*'], check=True)
    print(dst.name, f'{dst.stat().st_size // 1024}KB')
print('DONE')
