# -*- coding: utf-8 -*-
"""Statischer Site-Generator fuer madutours.com. Aufruf: python3 build.py  → ../dist"""
import os, re, json, shutil, html, hashlib
from pathlib import Path
from PIL import Image, ImageOps
import content as C

SRC = Path(__file__).resolve().parent
UP = SRC / "uploads"
DIST = SRC.parent / "dist"
IMG = DIST / "img"
S = C.SITE
LANGS = ["es", "en"]
BASE = {"es": "/", "en": "/en/"}

def esc(s): return html.escape(str(s), quote=True)

# ------------------------------------------------------------------ Bilder
def web_img(rel, width, kind, quality=80):
    """Erzeugt ein skaliertes JPEG unter dist/img/<kind>/<name>-<w>.jpg, gibt URL zurueck."""
    src = UP / rel
    stem = re.sub(r"[^a-z0-9]+", "-", Path(rel).stem.lower()).strip("-")
    out = IMG / kind / f"{stem}-{width}.jpg"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src); im = ImageOps.exif_transpose(im).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return "/img/%s/%s" % (kind, out.name)

def img_size(url):
    with Image.open(DIST / url.lstrip("/")) as im: return im.size

def picture(rel, kind, widths, sizes, alt="", cls="", loading="lazy", fetchpriority=None):
    srcs = [(web_img(rel, w, kind), w) for w in widths]
    srcset = ", ".join(f"{u} {w}w" for u, w in srcs)
    w, h = img_size(srcs[-1][0])
    fp = f' fetchpriority="{fetchpriority}"' if fetchpriority else ""
    return (f'<img src="{srcs[-1][0]}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{esc(alt)}" class="{cls}" loading="{loading}" decoding="async"{fp}>')

def make_logos():
    (IMG / "brand").mkdir(parents=True, exist_ok=True)
    shutil.copy(UP / "2016/04/logo_madotours.png", IMG / "brand/logo-white.png")
    shutil.copy(UP / "2016/04/logo_madotours_black.png", IMG / "brand/logo-dark.png")
    # Favicons: Hamsa weiss auf Nachtblau
    logo = Image.open(UP / "2016/04/logo_madotours.png").convert("RGBA")
    hamsa = logo.crop((0, 0, logo.width, int(logo.height * 0.78)))  # ohne Schriftzug
    for size, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (32, "favicon-32.png")):
        bg = Image.new("RGBA", (size, size), (27, 36, 64, 255))
        h = ImageOps.contain(hamsa, (int(size * 0.72), int(size * 0.72)))
        bg.alpha_composite(h, ((size - h.width) // 2, (size - h.height) // 2))
        bg.convert("RGB").save(DIST / name if name.startswith(("apple", "favicon")) else IMG / "brand" / name, "PNG")
    # OG-Bild
    og = Image.open(UP / "2016/04/BU.jpg").convert("RGB")
    og = ImageOps.fit(og, (1200, 630), Image.LANCZOS)
    og.save(IMG / "brand/og.jpg", "JPEG", quality=82)

# ------------------------------------------------------------------ Helfer
def url(key, lang): return BASE[lang] + C.SLUGS.get(key, "")
def t(lang): return C.UI[lang]

ICON = {
    "wa": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 12 12 0 0 0 4.6 4.1c1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3Z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M4 6h16v12H4zM4 7l8 6 8-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M12 21s-6-5.3-6-11a6 6 0 0 1 12 0c0 5.7-6 11-6 11Z"/><circle cx="12" cy="10" r="2.2" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M6 6l12 12M18 6 6 18"/></svg>',
    "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14m-6-6 6 6-6 6"/></svg>',
    "chev": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m9 6 6 6-6 6"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path fill="none" stroke="currentColor" stroke-width="1.8" d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "bed": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M3 18V8m0 6h18v4M3 14V7m18 7v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="10" r="2" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "camel": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M3 20l2-7a4 4 0 0 1 4-3h1l2-4 2 2v2h2l3 3v7m-9-4v4m4-4v4"/></svg>',
    "tag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.5" fill="currentColor"/></svg>',
    "guide": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M4 21a8 8 0 0 1 16 0"/></svg>',
    "flag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M5 21V4h12l-2 4 2 4H5"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M3 10h18M8 3v4m8-4v4"/></svg>',
}
FEATURE_ICONS = ["bed", "camel", "sun"]
USP_ICONS = ["tag", "guide", "sun"]

def wa_link(lang, text=None):
    msg = text or {"es": "Hola Madutours, quiero información sobre ", "en": "Hello Madutours, I would like information about "}[lang]
    from urllib.parse import quote
    return f"https://wa.me/{S['whatsapp']}?text={quote(msg)}"

def btn(href, label, kind="primary", icon=None, attrs=""):
    ic = ICON.get(icon, "") if icon else ""
    return f'<a class="btn btn-{kind}" href="{href}" {attrs}>{ic}<span>{esc(label)}</span></a>'

# ------------------------------------------------------------------ Layout
def head(lang, key, p):
    L = p[lang]; ui = t(lang)
    canon = S["domain"] + url(key, lang)
    alt_es, alt_en = S["domain"] + url(key, "es"), S["domain"] + url(key, "en")
    og_img = S["domain"] + (web_img(p["hero_img"], 1200, "hero") if p.get("hero_img") else "/img/brand/og.jpg")
    ld = {"@context": "https://schema.org", "@type": "TravelAgency", "name": "Madutours", "url": S["domain"],
          "telephone": S["phone_e164"], "email": S["email"], "image": S["domain"] + "/img/brand/og.jpg",
          "address": {"@type": "PostalAddress", "streetAddress": "Hassi Labied", "addressLocality": "Merzouga", "postalCode": "52202", "addressCountry": "MA"},
          "areaServed": "Morocco", "availableLanguage": ["es", "en", "fr", "de"]}
    if p.get("kind") == "route":
        ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": L["name"], "description": L["desc"], "url": canon,
              "touristType": ["Adventure", "Culture"], "itinerary": {"@type": "ItemList", "numberOfItems": p["days"],
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": d[0]} for i, d in enumerate(L["itinerary"])]},
              "provider": {"@type": "TravelAgency", "name": "Madutours", "url": S["domain"], "telephone": S["phone_e164"]}}
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(L["title"])}</title>
<meta name="description" content="{esc(L["desc"])}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="es" href="{alt_es}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="x-default" href="{alt_es}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Madutours">
<meta property="og:title" content="{esc(L["title"])}"><meta property="og:description" content="{esc(L["desc"])}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{og_img}"><meta property="og:locale" content="{'es_ES' if lang=='es' else 'en_GB'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1b2440">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus&family=Nunito+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap">
<link rel="stylesheet" href="/css/style.css?v={ASSET_V}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body class="page-{key}">
'''

def header(lang, key):
    ui = t(lang)
    items = "".join(f'<li><a href="{url(k, lang)}"{" aria-current=\"page\"" if k == key or (key in ("excursiones_fes",) and k == "excursiones") or (C.PAGES.get(key,{}).get("kind")=="route" and k=="rutas") else ""}>{esc(lbl)}</a></li>' for k, lbl in C.NAV[lang])
    other = ui["other_lang_code"]
    return f'''<a class="skip" href="#main">{ "Saltar al contenido" if lang=="es" else "Skip to content"}</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{BASE[lang]}" aria-label="Madutours"><img src="/img/brand/logo-white.png" width="134" height="175" alt="Madutours"></a>
    <nav class="nav" id="nav" aria-label="{'Principal' if lang=='es' else 'Main'}">
      <ul>{items}</ul>
      <div class="nav-extra">
        <a class="lang" href="{url(key, other)}" hreflang="{other}" lang="{other}">{ICON["globe"]}<span>{esc(ui["other_lang"])}</span></a>
        {btn(url("reservas", lang), ui["book"], "gold")}
      </div>
    </nav>
    <a class="lang lang-top" href="{url(key, other)}" hreflang="{other}" lang="{other}" title="{esc(ui["other_lang"])}">{other.upper()}</a>
    <button class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="nav" aria-label="{esc(ui["menu"])}"><span class="ic-open">{ICON["menu"]}</span><span class="ic-close">{ICON["close"]}</span></button>
  </div>
</header>
<main id="main">
'''

def footer(lang):
    ui = t(lang)
    addr = S["address"] if lang == "es" else S["address_en"]
    links = "".join(f'<li><a href="{url(k, lang)}">{esc(lbl)}</a></li>' for k, lbl in C.NAV[lang])
    routes = "".join(f'<li><a href="{url(k, lang)}">{esc(C.PAGES[k][lang]["name"])}</a></li>' for k in C.ROUTE_KEYS)
    return f'''</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="f-brand">
      <img src="/img/brand/logo-white.png" width="134" height="175" alt="" loading="lazy">
      <p>{esc(ui["footer_tag"])}</p>
    </div>
    <div>
      <h2 class="f-h">{esc(ui["contact_title"])}</h2>
      <ul class="f-contact">
        <li>{ICON["pin"]}<span>{esc(addr)}</span></li>
        <li>{ICON["phone"]}<a href="tel:{S["phone_e164"]}">{esc(S["phone_display"])}</a></li>
        <li>{ICON["wa"]}<a href="{wa_link(lang)}" rel="noopener" target="_blank">WhatsApp</a></li>
        <li>{ICON["mail"]}<a href="mailto:{S["email"]}">{S["email"]}</a></li>
      </ul>
    </div>
    <div><h2 class="f-h">Madutours</h2><ul class="f-links">{links}</ul></div>
    <div><h2 class="f-h">{esc(ui["our_routes"])}</h2><ul class="f-links">{routes}<li><a href="{url("excursiones", lang)}">{esc(ui["from_marrakech"])}</a></li><li><a href="{url("excursiones_fes", lang)}">{esc(ui["from_fes"])}</a></li></ul></div>
  </div>
  <div class="wrap footer-bottom"><p>© {S["year"]} Madutours · Hassi Labied, Merzouga · {esc(ui["footer_rights"])}</p><a class="lang" href="{url("home", ui["other_lang_code"])}">{esc(ui["other_lang"])}</a></div>
</footer>
<a class="wa-float" href="{wa_link(lang)}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICON["wa"]}</a>
<div class="lightbox" id="lightbox" hidden><button class="lb-close" aria-label="{esc(ui["close"])}">{ICON["close"]}</button><button class="lb-prev" aria-label="‹">{ICON["chev"]}</button><img alt=""><button class="lb-next" aria-label="›">{ICON["chev"]}</button></div>
<script src="/js/main.js?v={ASSET_V}" defer></script>
</body>
</html>
'''

def hero(lang, p, title, sub=None, kicker=None, ctas="", size="md", alt=""):
    pic = picture(p["hero_img"], "hero", [960, 1600, 2000], "100vw", alt=alt, cls="hero-img", loading="eager", fetchpriority="high")
    return f'''<section class="hero hero-{size}">
  {pic}
  <div class="hero-shade"></div>
  <div class="wrap hero-content">
    {f'<p class="kicker">{esc(kicker)}</p>' if kicker else ''}
    <h1>{esc(title)}</h1>
    {f'<p class="lead">{esc(sub)}</p>' if sub else ''}
    {f'<div class="cta-row">{ctas}</div>' if ctas else ''}
  </div>
</section>
'''

def gallery(lang, imgs, h2=None, kind="gal"):
    ui = t(lang)
    items = []
    for rel in imgs:
        full = web_img(rel, 1600, "full", 82)
        items.append(f'<a href="{full}" class="gal-item" data-lightbox>{picture(rel, kind, [480, 800], "(min-width: 900px) 30vw, 50vw", alt="", cls="")}</a>')
    return f'''<section class="section gallery-section"><div class="wrap">
  {f'<h2 class="h2">{esc(h2)}</h2>' if h2 else ''}
  <div class="gallery">{"".join(items)}</div>
</div></section>
'''

def video_block(lang, video, h2=None):
    ui = t(lang); kind, vid, poster = video
    src = f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0" if kind == "youtube" else f"https://player.vimeo.com/video/{vid}?autoplay=1"
    return f'''<section class="section video-section"><div class="wrap narrow">
  {f'<h2 class="h2">{esc(h2)}</h2>' if h2 else ''}
  <button class="video" type="button" data-video="{src}" aria-label="{esc(ui["play"])}">
    {picture(poster, "poster", [800, 1200], "(min-width: 900px) 800px, 100vw", alt="")}
    <span class="play">{ICON["play"]}</span>
  </button>
</div></section>
'''

def cta_band(lang, h2, p=None):
    ui = t(lang)
    return f'''<section class="cta-band"><div class="wrap">
  <h2>{esc(h2)}</h2>{f'<p>{esc(p)}</p>' if p else ''}
  <div class="cta-row">{btn(url("reservas", lang), ui["book_now"], "gold", "arrow")}{btn(wa_link(lang), ui["whatsapp"], "ghost", "wa", 'target="_blank" rel="noopener"')}</div>
</div></section>
'''

def route_cards(lang, exclude=None):
    ui = t(lang); cards = []
    for k in C.ROUTE_KEYS:
        if k == exclude: continue
        p = C.PAGES[k]; L = p[lang]
        cards.append(f'''<a class="card route-card" href="{url(k, lang)}">
  {picture(p["card_img"], "card", [600, 900], "(min-width: 900px) 30vw, 100vw", alt=L["name"])}
  <div class="card-body"><span class="pill">{p["days"]} {esc(ui["days"])}</span><h3>{esc(L["name"])}</h3><p>{esc(L["teaser"])}</p><span class="more">{esc(ui["see_route"])} {ICON["arrow"]}</span></div>
</a>''')
    cards.append(f'''<a class="card route-card custom" href="{url("reservas", lang)}">
  <div class="card-body"><span class="pill">{esc(ui["custom_route_t"])}</span><h3>{esc(ui["custom_route_t"])}</h3><p>{esc(ui["custom_route_p"])}</p><span class="more">{esc(ui["write_us"])} {ICON["arrow"]}</span></div>
</a>''')
    return f'<div class="cards cards-routes">{"".join(cards)}</div>'

# ------------------------------------------------------------------ Seiten
def page_home(lang):
    p = C.PAGES["home"]; L = p[lang]; ui = t(lang)
    ctas = btn(url("rutas", lang), ui["our_routes"], "gold", "arrow") + btn(wa_link(lang), ui["whatsapp"], "ghost", "wa", 'target="_blank" rel="noopener"')
    pillars = "".join(f'''<a class="card pillar" href="{url(k, lang)}">
      {picture(C.PAGES[k]["hero_img"], "card", [600, 900], "(min-width: 900px) 30vw, 100vw", alt=title)}
      <div class="card-body"><h3>{esc(title)}</h3><p>{esc(txt)}</p><span class="more">{ICON["arrow"]}</span></div></a>''' for k, title, txt in L["pillars"])
    return (hero(lang, p, L["hero_h1"], L["hero_p"], L["hero_kicker"], ctas, "lg", alt="Erg Chebbi, Merzouga")
        + f'''<section class="section"><div class="wrap">
  <h2 class="h2">{esc(L["pillars_h2"])}</h2>
  <div class="cards cards-pillars">{pillars}</div>
</div></section>
<section class="section section-tint"><div class="wrap">
  <div class="split">
    <div><h2 class="h2">{esc(L["intro_h2"])}</h2><p class="big">{esc(L["intro_p1"])}</p></div>
    <div><p>{esc(L["intro_p2"])}</p></div>
  </div>
</div></section>
'''
        + video_block(lang, ("vimeo", S["vimeo_home"], "2016/04/vimeo_video.jpg"), L["video_h2"])
        + f'''<section class="section"><div class="wrap narrow center">
  <h2 class="h2">{esc(L["price_h2"])}</h2><p class="big">{esc(L["price_p"])}</p>
  <div class="cta-row center">{btn(url("rutas", lang), ui["our_routes"], "primary", "arrow")}{btn(url("reservas", lang), ui["book_now"], "gold")}</div>
</div></section>
'''
        + gallery(lang, p["gallery"], L["gallery_h2"])
        + f'''<section class="quote-band"><div class="wrap narrow"><blockquote><p>“{esc(L["quote"])}”</p><cite>{esc(ui["quote_author"])}</cite></blockquote></div></section>
''' + cta_band(lang, ui["custom_route_t"], ui["custom_route_p"]))

def page_about(lang):
    p = C.PAGES["about"]; L = p[lang]; ui = t(lang)
    facts = "".join(f'<div class="fact"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in L["facts"])
    return (hero(lang, p, L["h1"], alt="Riad Madu")
        + f'''<section class="section"><div class="wrap">
  <div class="split"><div><p class="big">{esc(L["p1"])}</p></div><div><p>{esc(L["p2"])}</p></div></div>
  <div class="facts">{facts}</div>
</div></section>
<section class="quote-band"><div class="wrap narrow"><blockquote><p>“{esc(L["quote"])}”</p><cite>{esc(L["quote_by"])}</cite></blockquote></div></section>
'''
        + gallery(lang, p["gallery"], ui["gallery"])
        + cta_band(lang, L["cta_h2"]))

def page_rutas(lang):
    p = C.PAGES["rutas"]; L = p[lang]; ui = t(lang)
    usps = "".join(f'<div class="usp"><span class="usp-ic">{ICON[USP_ICONS[i]]}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(L["usps"]))
    return (hero(lang, p, L["h1"], L["lead"], alt="")
        + f'''<section class="section"><div class="wrap"><div class="usps">{usps}</div></div></section>
<section class="section section-tint"><div class="wrap"><h2 class="h2">{esc(L["routes_h2"])}</h2>{route_cards(lang)}</div></section>
<section class="section"><div class="wrap">
  <div class="excursion-links">
    <a class="card wide" href="{url("excursiones", lang)}">{picture(C.PAGES["excursiones"]["hero_img"], "card", [600, 900], "(min-width: 900px) 45vw, 100vw", alt="")}<div class="card-body"><span class="pill">1 {ui["day"].lower()}</span><h3>{esc(C.PAGES["excursiones"][lang]["h1"])}</h3><span class="more">{ICON["arrow"]}</span></div></a>
    <a class="card wide" href="{url("excursiones_fes", lang)}">{picture(C.PAGES["excursiones_fes"]["hero_img"], "card", [600, 900], "(min-width: 900px) 45vw, 100vw", alt="")}<div class="card-body"><span class="pill">1 {ui["day"].lower()}</span><h3>{esc(C.PAGES["excursiones_fes"][lang]["h1"])}</h3><span class="more">{ICON["arrow"]}</span></div></a>
  </div>
  <p class="note">{esc(ui["price_note"])}</p>
</div></section>
''' + cta_band(lang, L["banner_h2"], L["banner_p"]))

def page_route(lang, key):
    p = C.PAGES[key]; L = p[lang]; ui = t(lang)
    days = []
    for i, (title, text, img) in enumerate(L["itinerary"], 1):
        im = picture(img, "day", [600, 900], "(min-width: 900px) 360px, 100vw", alt=title) if img else ""
        days.append(f'<li class="day{" has-img" if img else ""}"><div class="day-n"><span>{esc(ui["day"])}</span><strong>{i}</strong></div><div class="day-body"><h3>{esc(title)}</h3><p>{esc(text)}</p></div>{f"<div class=\"day-img\">{im}</div>" if im else ""}</li>')
    return (hero(lang, p, L["name"], L["teaser"], f'{p["days"]} {ui["days"]} · {L["start"]} → {L["end"]}', btn(url("reservas", lang), ui["book_now"], "gold", "arrow"), alt=L["name"])
        + f'''<section class="section"><div class="wrap">
  <div class="route-meta"><div>{ICON["cal"]}<span>{p["days"]} {esc(ui["days"])}</span></div><div>{ICON["flag"]}<span>{esc(L["start"])} → {esc(L["end"])}</span></div><div>{ICON["bed"]}<span>{"Riads + jaimas" if lang=="es" else "Riads + desert camp"}</span></div><div>{ICON["guide"]}<span>{"4x4 con guía" if lang=="es" else "4x4 with guide"}</span></div></div>
  <ol class="itinerary">{"".join(days)}</ol>
  <p class="note">{esc(ui["price_note"])}</p>
</div></section>
''' + cta_band(lang, L["name"], ui["form"]["hint"] if False else None)
        + f'<section class="section section-tint"><div class="wrap"><h2 class="h2">{esc(ui["our_routes"])}</h2>{route_cards(lang, exclude=key)}</div></section>')

def page_excursions(lang, key):
    p = C.PAGES[key]; L = p[lang]; ui = t(lang)
    items = "".join(f'''<article class="exc"><div class="exc-img">{picture(img, "card", [600, 900, 1200], "(min-width: 900px) 45vw, 100vw", alt=title)}</div><div class="exc-body"><h2>{esc(title)}</h2><p>{esc(text)}</p>{btn(url("reservas", lang), ui["book"], "primary", "arrow")}</div></article>''' for title, text, img in L["items"])
    ok, olabel = L["other"]
    return (hero(lang, p, L["h1"], L["lead"], alt=L["h1"])
        + f'''<section class="section"><div class="wrap"><div class="exc-list">{items}</div>
  <a class="link-band" href="{url(ok, lang)}">{esc(olabel)} {ICON["arrow"]}</a>
  <p class="note">{esc(ui["price_note"])}</p></div></section>
''' + cta_band(lang, L["h1"]))

def page_place(lang, key):
    p = C.PAGES[key]; L = p[lang]; ui = t(lang)
    feats = "".join(f'<div class="usp"><span class="usp-ic">{ICON[FEATURE_ICONS[i]]}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(L["features"]))
    specs = "".join(f'<div class="fact"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in L["specs"])
    body = "".join(f"<p>{esc(x)}</p>" for x in L["body"])
    return (hero(lang, p, L["h1"], L["lead"], ctas=btn(url("reservas", lang), ui["book_now"], "gold", "arrow"), alt=L["h1"])
        + f'''<section class="section"><div class="wrap"><div class="usps">{feats}</div></div></section>
<section class="section section-tint"><div class="wrap"><div class="split"><div class="prose">{body}</div><div class="facts facts-col">{specs}</div></div></div></section>
''' + video_block(lang, p["video"]) + gallery(lang, p["gallery"], ui["gallery"]) + cta_band(lang, L["h1"]))

def form_html(lang, page_key):
    ui = t(lang); f = ui["form"]
    opts = "".join(f'<option>{esc(o)}</option>' for o in f["types"])
    return f'''<form class="booking" id="bookingForm" name="anfrage" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field"
  data-wa="{S["whatsapp"]}" data-subject="{esc(f["subject"])}" data-required="{esc(f["required"])}" data-ok="{esc(f["ok"])}" data-fail="{esc(f["fail"])}" data-sending="{esc(f["sending"])}" novalidate>
  <input type="hidden" name="form-name" value="anfrage">
  <input type="hidden" name="language" value="{lang}">
  <input type="hidden" name="page" value="{page_key}">
  <p class="hp" hidden><label>Do not fill this out: <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
  <div class="grid2">
    <label><span>{esc(f["name"])} *</span><input name="name" id="f-name" required autocomplete="name"></label>
    <label><span>{esc(f["email"])}</span><input name="email" id="f-email" type="email" autocomplete="email"></label>
    <label><span>{esc(f["phone"])}</span><input name="phone" id="f-phone" type="tel" autocomplete="tel"></label>
    <label><span>{esc(f["people"])}</span><input name="people" id="f-people" type="number" min="1" max="40" inputmode="numeric"></label>
    <label><span>{esc(f["arrival"])}</span><input name="arrival" id="f-arrival" type="date"></label>
    <label><span>{esc(f["departure"])}</span><input name="departure" id="f-departure" type="date"></label>
    <label class="full"><span>{esc(f["type"])}</span><select name="type" id="f-type">{opts}</select></label>
    <label class="full"><span>{esc(f["message"])} *</span><textarea name="message" id="f-message" rows="5" required></textarea></label>
  </div>
  <p class="form-error" id="formError" role="alert" hidden></p>
  <p class="form-ok" id="formOk" role="status" hidden></p>
  <div class="cta-row"><button class="btn btn-gold" type="submit" data-via="form"><span>{esc(f["send_form"])}</span></button><button class="btn btn-ghost-dark" type="submit" data-via="wa">{ICON["wa"]}<span>{esc(f["send_wa"])}</span></button></div>
  <p class="note">{esc(f["hint"])}</p>
</form>'''

def contact_cards(lang):
    ui = t(lang); addr = S["address"] if lang == "es" else S["address_en"]
    return f'''<div class="contact-cards">
  <a class="ccard" href="{wa_link(lang)}" target="_blank" rel="noopener">{ICON["wa"]}<strong>WhatsApp</strong><span>{esc(S["phone_display"])}</span></a>
  <a class="ccard" href="tel:{S["phone_e164"]}">{ICON["phone"]}<strong>{"Teléfono" if lang=="es" else "Phone"}</strong><span>{esc(S["phone_display"])}</span></a>
  <a class="ccard" href="mailto:{S["email"]}">{ICON["mail"]}<strong>E-mail</strong><span>{S["email"]}</span></a>
  <div class="ccard">{ICON["pin"]}<strong>{esc(ui["where"])}</strong><span>{esc(addr)}</span></div>
</div>'''

def page_booking(lang):
    p = C.PAGES["reservas"]; L = p[lang]
    return hero(lang, p, L["h1"], L["lead"], size="sm", alt="") + f'<section class="section"><div class="wrap narrow">{form_html(lang, "reservas")}</div></section><section class="section section-tint"><div class="wrap">{contact_cards(lang)}</div></section>'

def page_contact(lang):
    p = C.PAGES["contacto"]; L = p[lang]; ui = t(lang)
    from urllib.parse import quote
    q = quote(S["maps_query"])
    return (hero(lang, p, L["h1"], L["lead"], size="sm", alt="")
        + f'''<section class="section"><div class="wrap">{contact_cards(lang)}</div></section>
<section class="map-section"><iframe title="{"Mapa" if lang=="es" else "Map"}" src="https://www.google.com/maps?q={q}&z=12&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></section>
<section class="section"><div class="wrap narrow"><h2 class="h2">{esc(ui["write_us"])}</h2>{form_html(lang, "contacto")}</div></section>''')

BUILDERS = {"home": page_home, "about": page_about, "rutas": page_rutas, "reservas": page_booking, "contacto": page_contact}

def render(lang, key):
    p = C.PAGES[key]
    if key in BUILDERS: body = BUILDERS[key](lang)
    elif p.get("kind") == "route": body = page_route(lang, key)
    elif p.get("kind") == "excursions": body = page_excursions(lang, key)
    elif p.get("kind") == "place": body = page_place(lang, key)
    else: raise KeyError(key)
    return head(lang, key, p) + header(lang, key) + body + footer(lang)

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def not_found(lang):
    ui = t(lang)
    body = f'''<section class="section section-tint" style="min-height:60vh"><div class="wrap narrow center"><p class="kicker">404</p><h1 class="h2">{"Página no encontrada" if lang=="es" else "Page not found"}</h1><p class="big">{"La página que buscas no existe o se ha movido." if lang=="es" else "The page you are looking for does not exist or has moved."}</p><div class="cta-row center">{btn(BASE[lang], "Inicio" if lang=="es" else "Home", "primary", "arrow")}{btn(url("rutas", lang), ui["our_routes"], "gold")}</div></div></section>'''
    p = {"es": {"title": "Página no encontrada · Madutours", "desc": ""}, "en": {"title": "Page not found · Madutours", "desc": ""}, "hero_img": None}
    return head(lang, "home", p).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"') + header(lang, "404") + body + footer(lang)

def main():
    global ASSET_V
    if DIST.exists():
        for child in DIST.iterdir():
            if child.name != "img": shutil.rmtree(child) if child.is_dir() else child.unlink()
    DIST.mkdir(exist_ok=True); (DIST / "css").mkdir(exist_ok=True); (DIST / "js").mkdir(exist_ok=True)
    css = (SRC / "style.css").read_text(); js = (SRC / "main.js").read_text()
    ASSET_V = hashlib.md5((css + js).encode()).hexdigest()[:8]
    (DIST / "css/style.css").write_text(css); (DIST / "js/main.js").write_text(js)
    shutil.copy(SRC / "_redirects", DIST / "_redirects")
    make_logos()
    urls = []
    for lang in LANGS:
        for key in C.PAGES:
            out = DIST / url(key, lang).lstrip("/") / "index.html"
            write(out, render(lang, key)); urls.append((key, lang))
        write(DIST / ("404.html" if lang == "es" else "en/404.html"), not_found(lang))
    # robots + sitemap
    write(DIST / "robots.txt", f"User-agent: *\nAllow: /\nDisallow: /wp-admin/\n\nSitemap: {S['domain']}/sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for key in C.PAGES:
        for lang in LANGS:
            sm.append(f'<url><loc>{S["domain"]}{url(key, lang)}</loc>'
                      + "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{S["domain"]}{url(key, l)}"/>' for l in LANGS)
                      + f'<xhtml:link rel="alternate" hreflang="x-default" href="{S["domain"]}{url(key, "es")}"/>'
                      + f'<priority>{"1.0" if key=="home" else "0.8" if key in ("rutas","riad","jaimas","quad") else "0.6"}</priority></url>')
    sm.append("</urlset>")
    write(DIST / "sitemap.xml", "\n".join(sm))
    # Security + misc
    write(DIST / ".well-known/security.txt", f"Contact: mailto:{S['email']}\nExpires: 2027-12-31T00:00:00.000Z\nPreferred-Languages: es, en\n")
    print("built", len(urls), "pages →", DIST)

if __name__ == "__main__":
    main()
