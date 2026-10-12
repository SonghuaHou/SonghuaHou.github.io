# Portfolio

A fast, static personal portfolio built with **Astro 7** (zero client JS by default — only tiny vanilla TS enhancements). Bilingual EN-primary / ZH-secondary, with per-page accent-color theming and an Unsplash-style masonry photo gallery. Deployed to **GitHub Pages** via GitHub Actions.



* **Framework:** Astro 7 (static output, no SSR)

* **Styling:** hand-written CSS design tokens + one stylesheet; Sora font self-hosted via Fontsource, Chinese in Alibaba PuHuiTi 2.0 subset-self-hosted (`public/fonts`, regenerate with `scripts/subset-fonts.py` after adding Chinese copy)

* **Motion:** Lenis smooth scroll + scroll scrub reveals (`.sf` / `.sw`), vanilla TS, respects `prefers-reduced-motion`

* **Deploy:** GitHub Actions → GitHub Pages (`dist/`)



***

## Quick start



```
npm install
npm run dev      # http://localhost:4321
npm run build    # outputs static site to dist/
npm run preview  # serves dist/ locally
```

Node 18+ (tested on Node 22).



***

## Architecture at a glance



```
portfolio/
├─ astro.config.mjs            # site URL + (optional) base path for Pages
├─ package.json
├─ .github/workflows/deploy.yml# builds & publishes dist/ to GitHub Pages
├─ public/
│  └─ assets/                  # all images referenced as /assets/<file>
└─ src/
   ├─ content/
   │  └─ site.json             # ★ the ONLY content file — all copy & data live here
   ├─ lib/site.ts              # re-exports site.json as `site`
   ├─ layouts/Base.astro       # HTML skeleton; sets <body data-page="…">
   ├─ components/
   │  ├─ Topbar.astro          # top-right tab nav (bilingual)
   │  ├─ SiteFooter.astro
   │  ├─ WorkCard.astro        # bilingual list card; primary language follows `lang`
   │  └─ Icon.astro           # inline SVG icon set
   ├─ pages/
   │  ├─ index.astro           # About (hero + Education/Experience/Volunteering)
   │  ├─ writing.astro         # list: zine, statement, paper, report
   │  ├─ design.astro         # list: keynotes, workshop, poster
   │  ├─ visual-media.astro    # list: photo series + videos
   │  ├─ writing/*/index.astro # detail: zine pages / text blogs
   │  ├─ design/*/index.astro  # detail: keynote slides / poster
   │  ├─ visual-media/*/index.astro # detail: video players
   │  ├─ visual-media/daily/index.astro  # masonry gallery + lightbox
   │  ├─ 404.astro
   │  └─ robots.txt.ts
   ├─ styles/
   │  ├─ global.css            # base type scale, tokens (mostly untouched)
   │  └─ app.css              # ★ per-page themes + all new layout components
   └─ scripts/
      ├─ entry.ts             # bundles client JS (runs once on every page)
      ├─ topbar.ts            # mobile menu toggle
      ├─ reveal.ts            # scroll-scrubbed .sf / .sw reveals
      ├─ smooth-scroll.ts      # Lenis
      └─ lib.ts               # shared scroll helpers
```

**Data flow:** `site.json` → `lib/site.ts` → imported by every page. Pages map over arrays and render markup; there is no headless CMS. Adding/removing an item = editing JSON only.



***

## The content model (`src/content/site.json`)

Every text field exists in English (`*_en`) as primary and Chinese (`*_zh`) as secondary.



| Key                                           | Shape                                                         | Rendered on                                  |
| --------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------- |
| `name`, `role`, `email`, `year`, `socials[]`  | scalar / list                                                 | top-left logo, footer                        |
| `nav[]`                                       | `{label, zh, href}`                                           | top-right tabs                               |
| `about`                                       | `{photo, location_en/zh, role_zh, intro_en/zh}`               | About hero                                   |
| `education[]` `experience[]` `volunteering[]` | `{period, title_en/zh, org_en/zh, detail_en/zh}`              | About resume rows                            |
| `writing[]` `design[]` `visualmedia[]`   | `{year, kind, kind_zh?, lang, title_en/zh, venue_en/zh, detail_en/zh, thumb?, href?}` | list cards (`WorkCard`) — `lang: "zh"` renders Chinese primary, EN strings carry `(Mandarin)` |
| `dailyPhotos[]`                               | `{src, alt_en/zh}`                                            | masonry gallery                              |

### Conventions



* **Add a row:** copy one object in the relevant array. No component changes needed — lists auto-render.

* **Make a row clickable to a sub-page:** add `href` (e.g. the Daily Photography entry points to `/visual-media/daily/`).

* **Images:** drop files in `public/assets/`, reference as `/assets/foo.webp`. Because these are absolute paths, deploy at the repo root (`<user>.github.io`) — see *Deploying* below.



***

## Theming system

Theme is driven by **one attribute on&#x20;**`<body>`. `Base.astro` takes a `page` prop and writes `<body data-page="writing">`, and `app.css` defines the accent per value:



```
body[data-page="about"]       { --bg:#f2ead9; --text:#201a12; --accent:#ff5a1f; } /* light beige */
body[data-page="writing"]     { --accent:#ff5e9c; }  /* pink  */
body[data-page="design"]      { --accent:#ffc233; }  /* yellow*/
body[data-page="visualmedia"]  { --accent:#3ea6ff; }  /* blue  */
```

All UI reads from `--bg / --text / --soft / --line / --accent`, so recoloring a page = changing one line.

### Bilingual typography



* Tabs & headings: English primary, Chinese appended as `.nav-zh` / `.sec-title-zh` (smaller, muted).

* Body copy: English paragraph, then Chinese paragraph with class `zh` (\~0.86em, muted).



***

## Client scripts

`entry.ts` is the single bundle Astro loads from `Base.astro`. Each module queries for its own DOM hooks and no-ops when absent, so the same bundle works on every page:



* `topbar.ts` — mobile menu open/close (hooks: `[data-menu-btn]`, `[data-mobile-nav]`).

* `reveal.ts` — `.sf` blocks fade/rise on scroll; `.sw` word-by-word blur reveal.

* `smooth-scroll.ts` — Lenis.

The photo lightbox in `visual-media/daily/index.astro` is an inline page `<script>` (hooks `[data-lightbox]`, `[data-full]`).



***

## Common tasks (how to extend)

**Add a new portfolio page**



1. Create `src/pages/<name>.astro` using `Base page="<x>"`, `Topbar path="/<name>/"`, and a `work-list` block (copy `design.astro`).

2. Add a `body[data-page="<x>"] { --accent:#…; }` rule in `app.css`.

3. Add `{label, zh, href:"/<name>/"}` to `nav[]` in `site.json`.

**Add another photo gallery sub-page**

Copy `visual-media/daily/index.astro`, point `dailyPhotos` (or a new array) to it, and add a `visualmedia[]` row with `href`.

**Change fonts / type scale**

Fonts are imported in `Base.astro`; sizes live in `global.css` `.h1/.h2/.body/...`. New layout components go in `app.css`.



***

## Deploying (GitHub Pages)

`.github/workflows/deploy.yml` runs `npm ci && npm run build` and uploads `dist/`.



1. Set `site` in `astro.config.mjs` to your URL (e.g. `https://yourname.github.io`).

2. Push to `main`.

3. In the repo: **Settings → Pages → Source → GitHub Actions**.

> **Base path:**
>
>  images use absolute 
>
> `/assets/...`
>
>  paths. Deploy as a user site (
>
> `<user>.github.io`
>
> , repo root) for zero config. For a project page (
>
> `<user>.github.io/<repo>`
>
> ), you must also set 
>
> `base: "/<repo>"`
>
>  in 
>
> `astro.config.mjs`
>
>  and Astro will prefix asset URLs accordingly.



***

## Gotchas



* No content collection is configured — `getCollection` is intentionally unused; everything is plain JSON.

* `global.css` carries the original template's dark base tokens; page-level overrides in `app.css` win because it is imported second.

* The contact form from the original template was removed; there is no backend — mail links go to `site.email`.