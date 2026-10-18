"""Assemble the 11 portfolio detail pages from converted assets + extracted texts."""
import fitz
import html
import re
from pathlib import Path

ROOT = Path('/Users/songhua/Downloads/portfolio')
SRC = ROOT / 'src/pages'
T = Path('/private/var/folders/1b/wf3tlmpd4cj9skrmw1kmpdph0000gn/T/opencode/portfolio-text')
R = Path('/Users/songhua/Downloads/portfolio resources/portfolio contents')

ABBR = ['et al.', 'e.g.', 'i.e.', 'St.', 'pp.', 'Vol.', 'No.', 'vs.', 'Fig.']

def split_en(t):
    for i, k in enumerate(ABBR):
        t = t.replace(k, f'§AB{i}§')
    parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', t) if p.strip()]
    sents, buf = [], ''
    for idx, p in enumerate(parts):
        buf = (buf + ' ' + p).strip() if buf else p
        rest = parts[idx + 1] if idx + 1 < len(parts) else ''
        if rest and re.match(r'^[a-z§\d,;:\-–—%)]', rest):
            continue
        sents.append(buf)
        buf = ''
    if buf:
        sents.append(buf)
    out = []
    for s in sents:
        for i, k in enumerate(ABBR):
            s = s.replace(f'§AB{i}§', k)
        out.append(s)
    return out

def norm(t):
    return re.sub(r' {2,}', ' ', t).strip()

def paras_of(name):
    return [norm(p) for p in open(T / name).read().split('\n\n') if norm(p)]

def refs_of(name):
    return [norm(p) for p in open(T / name).read().split('\n') if norm(p)]

def check(t):
    assert '{' not in t and '}' not in t, t[:80]

def p_tags(plist):
    out = []
    for p in plist:
        check(p)
        out.append(f'          <p>{html.escape(p)}</p>')
    return '\n'.join(out)

def ref_list(rlist):
    items = '\n'.join(f'            <li>{html.escape(r)}</li>' for r in rlist)
    return ('          <div class="article-refs">\n            <h2>References</h2>\n'
            f'            <ol>\n{items}\n            </ol>\n          </div>')

# ---------- AIGC body rebuilt from blocks (keeps H2s + opening) ----------
def aigc_fragments():
    d = fitz.open(R / 'writing/AIGC与知识产权文化的重塑.pdf')
    heads = {'Recurrent Cycle of Piracy', 'The Myth of Democratisation', 'Fragmented Authorship'}
    frags, seg = [], []
    started = False
    for pno in range(4):
        for b in d[pno].get_text('blocks'):
            t = re.sub(r'\s+', ' ', b[4]).strip()
            if not t or t.lower() == 'references' or t.startswith('I declare'):
                continue
            if not started:
                if t.startswith('The Recurrent Cycle of Piracy:') or t.startswith('Reshaping of Intellectual'):
                    started = True
                continue
            if t in heads:
                if seg:
                    frags.append(('p', seg))
                    seg = []
                frags.append(('h', t))
            elif re.match(r'^(Allen|Chan|Disney|Johns|Philip),', t):
                break  # refs reached
            else:
                seg.append(t)
    if seg:
        frags.append(('p', seg))
    out = []
    for kind, val in frags:
        if kind == 'h':
            out.append(f'          <h2>{html.escape(val)}</h2>')
        else:
            sents = split_en(norm(' '.join(val)))
            for i in range(0, len(sents), 3):
                p = norm(' '.join(sents[i:i + 3]))
                check(p)
                out.append(f'          <p>{html.escape(p)}</p>')
    return '\n'.join(out)

HAVE_TEXTS = all((T / n).exists() for n in [
    'zine-statement.txt', 'zine-refs.txt', 'aigc-refs.txt', 'stmt-body.txt',
    'stmt-refs.txt', 'liangshan-full.txt'])
if not HAVE_TEXTS:
    print('WARN: extracted text fragments missing in', T, '— skipping text pages')

AIGC_BODY = aigc_fragments() if HAVE_TEXTS else ''
print('aigc paras+h:', AIGC_BODY.count('<p>'), AIGC_BODY.count('<h2>'))

ZINE_STMT = p_tags(paras_of('zine-statement.txt')) if HAVE_TEXTS else ''
ZINE_REFS = ref_list(refs_of('zine-refs.txt')) if HAVE_TEXTS else ''
AIGC_REFS = ref_list(refs_of('aigc-refs.txt')) if HAVE_TEXTS else ''
STMT_BODY = p_tags(paras_of('stmt-body.txt')) if HAVE_TEXTS else ''
STMT_REFS = ref_list(refs_of('stmt-refs.txt')) if HAVE_TEXTS else ''

def figure(src, alt, caption):
    return (f'          <figure class="article-figure">\n'
            f'            <img src="{src}" alt="{alt}" loading="lazy" />\n'
            f'            <figcaption>{caption}</figcaption>\n'
            f'          </figure>')

def paras_with_figures(name, insertions):
    """insertions: list of (anchor_start, figure_html) — figure goes after the
    paragraph starting with anchor_start."""
    plist = paras_of(name)
    out = []
    for p in plist:
        check(p)
        out.append(f'          <p>{html.escape(p)}</p>')
        for anchor, fig in insertions:
            if p.startswith(anchor):
                out.append(fig)
    return '\n'.join(out)

LIANGSHAN = paras_with_figures('liangshan-full.txt', [
    ('教室后黑板提示栏里写着',
     figure('/assets/liangshan-01.webp', '学生在小学教学楼前打篮球', '学生在小学教学楼前打篮球')),
    ('这种观感不分对错',
     figure('/assets/liangshan-02.webp', '课间聚在操场上的学生们', '课间聚在操场上的学生们')),
    ('送给课堂提问得分最高的学生一本书',
     figure('/assets/liangshan-03.webp', '走在村道上的支教队员们', '走在村道上的支教队员们')),
]) if HAVE_TEXTS else ''
# 结尾段改为三行落款
LIANGSHAN = re.sub(
    r'<p>2023[^<]*</p>',
    '<div class="article-colophon">2023年8月14-16日于四川省凉山州冕宁县宏模镇<br />8月19-20日改定<br />杨金娜 丁贝蓓等 供图</div>',
    LIANGSHAN)

ZH_REFS_HEAD = '<h2>参考文献</h2>'

# ---------- page templates ----------
def design_page(slug, images, alts):
    (SRC / 'design' / slug).mkdir(parents=True, exist_ok=True)
    href = f'/design/{slug}/'
    figs = '\n'.join(
        f'          <figure>\n            <img src="/assets/{img}" alt="{alt}" loading="lazy" />\n          </figure>'
        for img, alt in zip(images, alts))
    return f"""---
import Base from "../../../layouts/Base.astro";
import Topbar from "../../../components/Topbar.astro";
import SiteFooter from "../../../components/SiteFooter.astro";
import {{ site }} from "../../../lib/site";
const w = site.design.find((x) => x.href === "{href}")!;
---
<Base page="design" title={{`${{site.name}} — ${{w.title_zh}}`}}>
  <Topbar path="/design/" />
  <main>
    <section class="pad page">
      <div class="sec-head sf">
        <a href="/design/" class="caption" style="color:var(--soft)">← Design</a>
        <span class="kicker" style="margin-top:18px; display:inline-flex">{{w.kind}}<span class="kicker-zh">{{w.kind_zh}}</span></span>
        <h1 class="sec-title" style="margin-top:14px">{{w.title_zh}}<span class="sec-title-zh">{{w.title_en}}</span></h1>
        <div class="article-meta"><span>{{w.year}}</span><span>{{w.venue_zh}}</span></div>
        <p class="article-lede" style="margin-top:18px">{{w.intro_zh}}</p>
        <p class="article-lede zh">{{w.intro_en}}</p>
      </div>
      <div class="doc-pages sf">
{figs}
      </div>
    </section>
  </main>
  <SiteFooter />
</Base>
"""

def blog_page(section, page, slug, en_primary, body_html, refs_html='', extra_head=''):
    (SRC / section / slug).mkdir(parents=True, exist_ok=True)
    href = f'/{section}/{slug}/'
    title_p, title_s = (f'w.title_en', f'w.title_zh') if en_primary else (f'w.title_zh', f'w.title_en')
    venue_p = 'w.venue_en' if en_primary else 'w.venue_zh'
    det_p, det_s = ('w.detail_en', 'w.detail_zh') if en_primary else ('w.detail_zh', 'w.detail_en')
    return f"""---
import Base from "../../../layouts/Base.astro";
import Topbar from "../../../components/Topbar.astro";
import SiteFooter from "../../../components/SiteFooter.astro";
import {{ site }} from "../../../lib/site";
const w = site.{section}.find((x) => x.href === "{href}")!;
---
<Base page="{page}" title={{`${{site.name}} — ${{{title_p}}}`}}>
  <Topbar path="/{section}/" />
  <main>
    <section class="pad page">
      <div class="sec-head sf">
        <a href="/{section}/" class="caption" style="color:var(--soft)">← {'Writing' if section == 'writing' else 'Visual Media'}</a>
        <span class="kicker" style="margin-top:18px; display:inline-flex">{{w.kind}}<span class="kicker-zh">{{w.kind_zh || w.kind}}</span></span>
        <h1 class="sec-title" style="margin-top:14px">{{{title_p}}}<span class="sec-title-zh">{{{title_s}}}</span></h1>
        <div class="article-meta"><span>{{w.year}}</span><span>{{{venue_p}}}</span></div>
{extra_head}      </div>
      <div class="article sf">
        <p class="article-lede">{{{det_p}}}</p>
        <p class="article-lede zh">{{{det_s}}}</p>
        <div class="article-body">
{body_html}
        </div>
{refs_html}      </div>
    </section>
  </main>
  <SiteFooter />
</Base>
"""

pages = {}

# --- 4 keynote detail pages ---
pages['design/introducing-journalism/index.astro'] = design_page(
    'introducing-journalism',
    ['jy-xinwen-1.webp', 'jy-xinwen-2.webp', 'jy-xinwen-3.webp'],
    ['新闻传播学讲演配图 1', '新闻传播学讲演配图 2', '新闻传播学讲演配图 3'])
pages['design/housing-reform-40-years/index.astro'] = design_page(
    'housing-reform-40-years',
    ['jy-fangdichan-1.webp', 'jy-fangdichan-2.webp', 'jy-fangdichan-3.webp', 'jy-fangdichan-4.webp'],
    ['房地产改革讲演配图 1', '房地产改革讲演配图 2', '房地产改革讲演配图 3', '房地产改革讲演配图 4'])
pages['design/resurrection/index.astro'] = design_page(
    'resurrection',
    ['jy-fuhuo-1.webp', 'jy-fuhuo-2.webp', 'jy-fuhuo-3.webp', 'jy-fuhuo-4.webp'],
    ['复活讲演配图 1', '复活讲演配图 2', '复活讲演配图 3', '复活讲演配图 4'])
pages['design/yi-yi/index.astro'] = design_page(
    'yi-yi',
    ['jy-yiyi-1.webp', 'jy-yiyi-2.webp', 'jy-yiyi-3.webp'],
    ['一一培训配图 1', '一一培训配图 2', '一一培训配图 3'])
pages['design/drama-festival-poster/index.astro'] = design_page(
    'drama-festival-poster',
    ['poster-drama-festival.webp', 'poster-drama-ten.webp'],
    ['青岛二中第十届戏剧节海报', '戏剧十年海报'])

# --- zine page: 14 page images + statement + refs ---
zfigs = '\n'.join(
    f'          <figure>\n            <img src="/assets/zine-{i:02d}.webp" alt="Quantifying a Better Self, page {i}" loading="lazy" />\n'
    f'            <figcaption>Page {i} / 第 {i} 页</figcaption>\n          </figure>'
    for i in range(1, 9))
zine_body = ('        <div class="doc-pages doc-pages--zine sf">\n' + zfigs +
             '\n        </div>\n        <div class="article sf">\n          <div class="article-body">\n'
             '          <h2>Statement<span class="sec-title-zh">创作陈述</span></h2>\n' +
             ZINE_STMT + '\n          </div>\n' + ZINE_REFS + '        </div>')
(SRC / 'writing' / 'quantifying-better-self').mkdir(parents=True, exist_ok=True)
pages['writing/quantifying-better-self/index.astro'] = f"""---
import Base from "../../../layouts/Base.astro";
import Topbar from "../../../components/Topbar.astro";
import SiteFooter from "../../../components/SiteFooter.astro";
import {{ site }} from "../../../lib/site";
const w = site.writing.find((x) => x.href === "/writing/quantifying-better-self/")!;
---
<Base page="writing" title={{`${{site.name}} — ${{w.title_en}}`}}>
  <Topbar path="/writing/" />
  <main>
    <section class="pad page">
      <div class="sec-head sf">
        <a href="/writing/" class="caption" style="color:var(--soft)">← Writing</a>
        <span class="kicker" style="margin-top:18px; display:inline-flex">{{w.kind}}<span class="kicker-zh">杂志</span></span>
        <h1 class="sec-title" style="margin-top:14px">{{w.title_en}}<span class="sec-title-zh">{{w.title_zh}}</span></h1>
        <div class="article-meta"><span>{{w.year}}</span><span>{{w.venue_en}}</span><span>8 plates + statement</span></div>
        <p class="article-lede" style="margin-top:18px">{{w.detail_en}}</p>
        <p class="article-lede zh">{{w.detail_zh}}</p>
      </div>
{zine_body}
    </section>
  </main>
  <SiteFooter />
</Base>
"""

# --- 3 text blog pages ---
pages['writing/re-rendering-cinema/index.astro'] = blog_page(
    'writing', 'writing', 're-rendering-cinema', True, STMT_BODY, STMT_REFS)
pages['writing/recurrent-cycle-of-piracy/index.astro'] = blog_page(
    'writing', 'writing', 'recurrent-cycle-of-piracy', True, AIGC_BODY, AIGC_REFS)
epigraph = ('        <p class="article-lede">“农村教育并没有提供观念，而只是观念的对象。”</p>\n'
            '        <p class="article-lede zh">—— 林小英《县中的孩子》</p>\n')
pages['writing/objects-of-concepts/index.astro'] = blog_page(
    'writing', 'writing', 'objects-of-concepts', False, LIANGSHAN, '', epigraph)

# --- full-text-as-images writing page (zine style) ---
def imgdoc_page(section, slug, en_primary, imgs, credit):
    (SRC / section / slug).mkdir(parents=True, exist_ok=True)
    href = f'/{section}/{slug}/'
    title_p, title_s = ('w.title_en', 'w.title_zh') if en_primary else ('w.title_zh', 'w.title_en')
    venue_p = 'w.venue_en' if en_primary else 'w.venue_zh'
    det_p, det_s = ('w.detail_en', 'w.detail_zh') if en_primary else ('w.detail_zh', 'w.detail_en')
    figs = '\n'.join(
        f'          <figure>\n'
        f'            <img src="/assets/{img}" alt={{{title_p} + ", page {i}"}} loading="lazy" />\n'
        f'            <figcaption>Page {i} / 第 {i} 页</figcaption>\n          </figure>'
        for i, img in enumerate(imgs, 1))
    return f"""---
import Base from "../../../layouts/Base.astro";
import Topbar from "../../../components/Topbar.astro";
import SiteFooter from "../../../components/SiteFooter.astro";
import {{ site }} from "../../../lib/site";
const w = site.{section}.find((x) => x.href === "{href}")!;
---
<Base page="{section}" title={{`${{site.name}} — ${{{title_p}}}`}}>
  <Topbar path="/{section}/" />
  <main>
    <section class="pad page">
      <div class="sec-head sf">
        <a href="/{section}/" class="caption" style="color:var(--soft)">← {'Writing' if section == 'writing' else 'Visual Media'}</a>
        <span class="kicker" style="margin-top:18px; display:inline-flex">{{w.kind}}<span class="kicker-zh">{{w.kind_zh || w.kind}}</span></span>
        <h1 class="sec-title" style="margin-top:14px">{{{title_p}}}<span class="sec-title-zh">{{{title_s}}}</span></h1>
        <div class="article-meta"><span>{{w.year}}</span><span>{{{venue_p}}}</span><span>{credit}</span></div>
        <p class="article-lede" style="margin-top:18px">{{{det_p}}}</p>
        <p class="article-lede zh">{{{det_s}}}</p>
      </div>
      <div class="doc-pages sf">
{figs}
      </div>
    </section>
  </main>
  <SiteFooter />
</Base>
"""

# --- designing intimacy: 23 full-text page images ---
pages['writing/designing-intimacy/index.astro'] = imgdoc_page(
    'writing', 'designing-intimacy', True,
    [f'replika-{i:02d}.webp' for i in range(1, 24)],
    'With Alice Jing &amp; Zhewen Xu')

# --- 2 video pages ---
def video_page(slug, href, en_primary, mp4, poster):
    (SRC / 'visual-media' / slug).mkdir(parents=True, exist_ok=True)
    title_p, title_s = ('w.title_en', 'w.title_zh') if en_primary else ('w.title_zh', 'w.title_en')
    venue_p = 'w.venue_en' if en_primary else 'w.venue_zh'
    det_p, det_s = ('w.detail_en', 'w.detail_zh') if en_primary else ('w.detail_zh', 'w.detail_en')
    return f"""---
import Base from "../../../layouts/Base.astro";
import Topbar from "../../../components/Topbar.astro";
import SiteFooter from "../../../components/SiteFooter.astro";
import {{ site }} from "../../../lib/site";
const w = site.visualmedia.find((x) => x.href === "{href}")!;
---
<Base page="visualmedia" title={{`${{site.name}} — ${{{title_p}}}`}}>
  <Topbar path="/visual-media/" />
  <main>
    <section class="pad page">
      <div class="sec-head sf">
        <a href="/visual-media/" class="caption" style="color:var(--soft)">← Visual Media</a>
        <span class="kicker" style="margin-top:18px; display:inline-flex">{{w.kind}}<span class="kicker-zh">{{w.kind_zh}}</span></span>
        <h1 class="sec-title" style="margin-top:14px">{{{title_p}}}<span class="sec-title-zh">{{{title_s}}}</span></h1>
        <div class="article-meta"><span>{{w.year}}</span><span>{{{venue_p}}}</span></div>
        <p class="article-lede" style="margin-top:18px">{{{det_p}}}</p>
        <p class="article-lede zh">{{{det_s}}}</p>
      </div>
      <figure class="video-wrap sf">
        <video controls preload="metadata" poster="/assets/{poster}" src="/assets/{mp4}"></video>
        <figcaption>{{{title_p}}}</figcaption>
      </figure>
    </section>
  </main>
  <SiteFooter />
</Base>
"""

pages['visual-media/climate-crisis/index.astro'] = video_page(
    'climate-crisis', '/visual-media/climate-crisis/', True, 'climate-crisis.mp4', 'video-climate.webp')
pages['visual-media/hkbu-interview/index.astro'] = video_page(
    'hkbu-interview', '/visual-media/hkbu-interview/', False, 'hkbu-interview.mp4', 'video-hkbu.webp')

TEXT_PAGES = {
    'writing/quantifying-better-self/index.astro',
    'writing/re-rendering-cinema/index.astro',
    'writing/recurrent-cycle-of-piracy/index.astro',
    'writing/objects-of-concepts/index.astro',
}
for rel, content in pages.items():
    if not HAVE_TEXTS and rel in TEXT_PAGES:
        print('kept existing (texts missing):', rel)
        continue
    (SRC / rel).write_text(content)
    print('wrote', rel)
print('total:', len(pages))
