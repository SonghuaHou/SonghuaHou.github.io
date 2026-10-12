"""Convert portfolio resource files to web assets (public/assets/).
Photos/poster -> webp. Single-page Keynote PDFs + zine pages -> webp.
Video posters extracted from original mp4s.
"""
import fitz
from PIL import Image, ImageOps
import subprocess
from pathlib import Path

R = Path('/Users/songhua/Downloads/portfolio resources/portfolio contents')
OUT = Path('/Users/songhua/Downloads/portfolio/public/assets')
OUT.mkdir(parents=True, exist_ok=True)

def save_webp(im: Image.Image, name: str, width: int, quality: int):
    im = ImageOps.exif_transpose(im).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    p = OUT / name
    im.save(p, 'WEBP', quality=quality, method=6)
    print(f'{name}: {im.size} {p.stat().st_size//1024}KB', flush=True)

def pdf_to_webp(pdf: Path, prefix: str, width: int, quality: int, zoom: float = 2.0):
    d = fitz.open(pdf)
    names = []
    for i, pg in enumerate(d):
        pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        name = f'{prefix}.webp' if len(d) == 1 else f'{prefix}-{i+1}.webp'
        save_webp(im, name, width, quality)
        names.append(name)
    return names

# 1. Daily photos (sorted, full ratio kept)
photos = sorted((R / 'visual media/日常摄影').glob('IMG_*.jpeg'))
for i, ph in enumerate(photos, 1):
    save_webp(Image.open(ph), f'daily-{i:02d}.webp', 1400, 80)

# 2. Drama festival poster (Pixelmator PNG, A3-ish)
save_webp(Image.open(R / 'design/青岛二中第十届戏剧节海报.png'),
          'poster-drama-festival.webp', 1200, 82)

# 3. Keynote single-page PDFs, order: base, then numbered
jobs = [
    ('design/讲演配图/班会专业简介：新闻传播学', 'jy-xinwen',
     ['新闻传播（拖移项目）.pdf', '新闻传播（拖移项目） 2.pdf', '新闻传播（拖移项目） 3.pdf']),
    ('design/讲演配图/政治课堂讲演：中国房地产改革40年', 'jy-fangdichan',
     ['政治课堂讲演_中国房地产改革40年（拖移项目）.pdf',
      '政治课堂讲演_中国房地产改革40年（拖移项目） 4.pdf',
      '政治课堂讲演_中国房地产改革40年（拖移项目） 5.pdf',
      '政治课堂讲演_中国房地产改革40年（拖移项目） 6.pdf']),
    ('design/讲演配图/语文课堂讲演：复活', 'jy-fuhuo',
     ['语文课堂讲演_复活（拖移项目）.pdf', '语文课堂讲演_复活（拖移项目） 2.pdf',
      '语文课堂讲演_复活（拖移项目） 3.pdf', '语文课堂讲演_复活（拖移项目） 5.pdf']),
    ('design/讲演配图/戏剧社培训设计：一一', 'jy-yiyi',
     ['戏剧社培训设计：一一（拖移项目）.pdf', '戏剧社培训设计：一一（拖移项目） 2.pdf',
      '戏剧社培训设计：一一（拖移项目） 3.pdf']),
]
for folder, prefix, files in jobs:
    for j, f in enumerate(files, 1):
        pdf_to_webp(R / folder / f, f'{prefix}-{j}', 1600, 82)

# 4. Zine pages (A4, keep readable)
d = fitz.open(R / 'writing/量化更好的自我.pdf')
for i, pg in enumerate(d):
    pix = pg.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    save_webp(im, f'zine-{i+1:02d}.webp', 1190, 85)

# 5. Video posters from originals
def poster(src: Path, name: str, ss: int):
    tmp = OUT / '_tmp_poster.jpg'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ss), '-i', str(src),
                    '-frames:v', '1', '-q:v', '3', str(tmp)], check=True)
    save_webp(Image.open(tmp), name, 960, 80)
    tmp.unlink()

poster(R / 'visual media/我们如何看见并了解气候危机.mp4', 'video-climate.webp', 30)
poster(R / 'visual media/香港浸会大学项目视频采访.mp4', 'video-hkbu.webp', 20)

print('DONE images')
