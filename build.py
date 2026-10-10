#!/usr/bin/env python3
"""Baut die statische Website von IOS Hannover nach ./public.

Aufruf:  python3 build.py

Inhalte, die sich oft ändern (Referenten, Archiv, Presse), liegen als JSON
in ./content. Texte der einzelnen Seiten stehen weiter unten in PAGES.
Benötigt nur die Python-Standardbibliothek.
"""

import datetime
import html
import json
import shutil
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public"
CONTENT = ROOT / "content"

SITE = "https://www.ios-hannover.de"
PDF = SITE + "/data/pdf/"
SHOP_SEMINARE = "https://ios-hannover.de/shop/public/de"
SHOP_SYMPOSIUM = "https://ios-hannover.de/shop/public/cz/de"
PRAGUE = "https://ios-prague.com/"
FACEBOOK = "https://www.facebook.com/InterdisciplinaryOrthodonticSeminarsHannover"
INSTAGRAM = "https://www.instagram.com/ios.hannover/"

ICONS = {
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M13.4 21v-7.6h2.6l.4-3h-3V8.5c0-.9.3-1.5 1.5-1.5h1.6V4.3c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.3H7.8v3h2.6V21z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>',
    "prague": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M12 2.5 15.5 9v12h-7V9z"/><path d="M8.5 9h7M4 21h16M5.5 21v-6l3-2M18.5 21v-6l-3-2"/><path d="M10.5 21v-3.5a1.5 1.5 0 0 1 3 0V21"/></svg>',
}
SOCIAL = [
    ("facebook", "Facebook", FACEBOOK),
    ("instagram", "Instagram", INSTAGRAM),
    ("prague", "IOS Prague", PRAGUE),
]


def social_links(cls="social", labels=False):
    items = "".join(
        f'<li><a class="social-link social-link--{key}" href="{url}" rel="noopener" target="_blank" '
        f'aria-label="{name} (öffnet in neuem Tab)" title="{name}">{ICONS[key]}'
        + (f'<span>{name}</span>' if labels else "")
        + "</a></li>"
        for key, name, url in SOCIAL
    )
    return f'<ul class="{cls}">{items}</ul>'


ORG = {
    "name": "IOS Hannover",
    "long": "Interdisciplinary Orthodontic Seminars",
    "street": "Sutelstraße 2",
    "zip": "30659",
    "city": "Hannover",
    "phone": "+49 511 5331693",
    "phone_display": "+49 511 / 5 33 16 93",
    "fax_display": "+49 511 / 5 33 16 95",
    "email": "info@ios-hannover.de",
}

TODAY = datetime.date.today().isoformat()


def e(text):
    return html.escape(str(text), quote=True)


def load(name):
    return json.loads((CONTENT / f"{name}.json").read_text(encoding="utf-8"))


# Hauptnavigation = Seitenverlauf (Reihenfolge der „Weiter“-Links)
NAV = [
    ("/", "Start"),
    ("/philosophie/", "Philosophie"),
    ("/veranstaltungen/", "Veranstaltungen"),
    ("/archiv/", "Archiv"),
    ("/referenten/", "Referenten"),
    ("/presse/", "Presse"),
    ("/kontakt/", "Kontakt"),
]

# Stationen der langen Startseite (Burger-Menü springt per Smooth Scroll dorthin)
STATIONS = [
    ("start", "Willkommen"),
    ("philosophie", "Philosophie"),
    ("geschichte", "Geschichte"),
    ("veranstaltungen", "Veranstaltungen"),
    ("referenten", "Referenten"),
    ("presse", "Presse"),
    ("kontakt", "Kontakt"),
]


def org_jsonld():
    return {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "@id": SITE + "/#organisation",
        "name": ORG["name"],
        "alternateName": ORG["long"],
        "url": SITE + "/",
        "logo": SITE + "/assets/apple-touch-icon.png",
        "email": ORG["email"],
        "telephone": ORG["phone"],
        "faxNumber": "+49 511 5331695",
        "founder": {"@type": "Person", "name": "Dr. Jan V. Raiman"},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ORG["street"],
            "postalCode": ORG["zip"],
            "addressLocality": ORG["city"],
            "addressCountry": "DE",
        },
        "sameAs": [FACEBOOK, INSTAGRAM, PRAGUE],
    }


def breadcrumb_jsonld(path, title):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Start", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": SITE + path},
        ],
    }


def arch_svg(cls):
    """Zahnbogen mit Brackets und Bogendraht (Aufsicht) als Linienzeichnung."""
    import math

    def bez(t, p):
        u = 1 - t
        return (
            u**3 * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t**3 * p[3][0],
            u**3 * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t**3 * p[3][1],
        )

    teeth = [(30, 312), (18, -40), (382, -40), (370, 312)]
    wire = teeth  # Draht läuft durch die Brackets auf den Zähnen
    # gleichmäßig nach Bogenlänge verteilen
    samples = [bez(i / 400, teeth) for i in range(401)]
    acc = [0.0]
    for a, b in zip(samples, samples[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    n = 14
    shapes = []
    for k in range(n):
        target = acc[-1] * (k + 0.5) / n
        j = next(i for i, v in enumerate(acc) if v >= target)
        (x, y), (x2, y2) = samples[j], samples[min(j + 1, 400)]
        ang = math.degrees(math.atan2(y2 - y, x2 - x))
        pos = abs(k - (n - 1) / 2) / ((n - 1) / 2)  # 0 = Schneidezahn, 1 = Molar
        rx = 11 + 13 * pos ** 1.4
        ry = 15 + 8 * pos
        d = round(pos * (n - 1) / 2)  # Abstand zur Mitte → Reihenfolge der Animation
        shapes.append(
            f'<g transform="rotate({ang:.1f} {x:.1f} {y:.1f})"><ellipse class="tooth" style="--d:{d}" '
            f'cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/></g>'
        )
        bx, by = x, y
        shapes.append(
            f'<rect class="bracket" style="--d:{d}" x="{bx - 5:.1f}" y="{by - 5:.1f}" width="10" height="10" rx="2" '
            f'transform="rotate({ang:.1f} {bx:.1f} {by:.1f})"/>'
        )
    path = f'M{wire[0][0]},{wire[0][1]} C{wire[1][0]},{wire[1][1]} {wire[2][0]},{wire[2][1]} {wire[3][0]},{wire[3][1]}'
    return (
        f'<svg class="arch {cls}" viewBox="-10 -20 420 350" aria-hidden="true" focusable="false">'
        + "".join(shapes)
        + f'<path class="wire" d="{path}" pathLength="1"/></svg>'
    )


def layout(page, body):
    path = page["path"]
    canonical = SITE + path
    jsonld = list(page.get("jsonld", []))
    if path != "/" and not page.get("noindex"):
        jsonld.append(breadcrumb_jsonld(path, page["crumb"]))
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
        for x in jsonld
    )
    robots = "noindex, follow" if page.get("noindex") else "index, follow"

    stations = "\n".join(
        f'<li style="--i:{i}"><a href="/#{sid}" data-station="{sid}">'
        f'<span class="menu-no">{i + 1:02d}</span><span class="menu-label">{label}</span></a></li>'
        for i, (sid, label) in enumerate(STATIONS)
    )
    details = "\n".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == page.get("nav", path) else ""}>{label}</a></li>'
        for href, label in NAV[1:] + [("/fotogalerie/", "Fotogalerie")]
    )

    # Farbiges Kopf-Band mit Brotkrumen, H1 und Einleitung (alle Seiten außer Start)
    crumbs = ""
    if path != "/":
        lead = f'<p class="lead">{page["lead"]}</p>' if page.get("lead") else ""
        crumbs = (
            '<section class="page-band"><div class="wrap">'
            '<nav class="breadcrumbs" aria-label="Brotkrumen"><ol>'
            '<li><a href="/">Start</a></li>'
            f'<li aria-current="page">{e(page["crumb"])}</li></ol></nav>'
            f'<h1>{page["h1"]}</h1>{lead}</div>'
            f'{arch_svg("page-band-art")}</section>'
        )

    # „Weiter“-Link: nächste Seite im Seitenverlauf
    nxt = ""
    order = [h for h, _ in NAV]
    if path in order and path not in ("/", order[-1]):
        i = order.index(path) + 1
        h, label = NAV[i]
        nxt = (
            '<div class="wrap"><div class="next card--link">'
            f'<span class="next-step">Weiter · Schritt {i} von {len(NAV) - 1}</span>'
            f'<a href="{h}">{label}<span aria-hidden="true"> →</span></a></div></div>'
        )

    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page["title"])}</title>
<meta name="description" content="{e(page["description"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="IOS Hannover">
<meta property="og:title" content="{e(page["title"])}">
<meta property="og:description" content="{e(page["description"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#503b8a">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<script>document.documentElement.classList.add("js")</script>
<script src="/assets/main.js" defer></script>
{ld}
</head>
<body class="{page.get("body_class", "")}">
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="IOS Hannover – Startseite">
      <span class="brand-mark" aria-hidden="true">IOS</span>
      <span class="brand-text"><strong>IOS Hannover</strong><small>Interdisciplinary Orthodontic Seminars</small></span>
    </a>
    <div class="header-actions">
      {social_links("social social--header")}
    <button class="burger" type="button" aria-expanded="false" aria-controls="menu">
      <span class="burger-label">Menü</span>
      <span class="burger-icon" aria-hidden="true"><span></span><span></span><span></span></span>
    </button>
    </div>
  </div>
  <div class="scroll-progress" aria-hidden="true"><span></span></div>
</header>
<div class="menu" id="menu" aria-label="Menü">
  <div class="menu-inner wrap">
    <nav class="menu-stations" aria-label="Hauptnavigation">
      <p class="menu-kicker">Rundgang</p>
      <ol>
{stations}
      </ol>
    </nav>
    <div class="menu-side">
      <nav aria-label="Ausführliche Seiten">
        <p class="menu-kicker">Ausführlich</p>
        <ul class="menu-details">
{details}
        </ul>
      </nav>
      <div class="menu-contact">
        <p class="menu-kicker">Kontakt</p>
        <p><a href="tel:{ORG["phone"].replace(" ", "")}">{ORG["phone_display"]}</a><br>
        <a href="mailto:{ORG["email"]}">{ORG["email"]}</a><br>
        {ORG["street"]}, {ORG["zip"]} {ORG["city"]}</p>
      </div>
      <div>
        <p class="menu-kicker">Folgen Sie uns</p>
        {social_links("social social--menu", labels=True)}
      </div>
    </div>
  </div>
</div>
<main id="inhalt">
{crumbs}
{body}
{nxt}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>IOS Hannover</h2>
        <address>
          Dr. Jan V. Raiman<br>
          {ORG["street"]}<br>
          {ORG["zip"]} {ORG["city"]}
        </address>
      </div>
      <div>
        <h2>Kontakt</h2>
        <ul>
          <li>Tel. <a href="tel:{ORG["phone"].replace(" ", "")}">{ORG["phone_display"]}</a></li>
          <li>Fax {ORG["fax_display"]}</li>
          <li><a href="mailto:{ORG["email"]}">{ORG["email"]}</a></li>
        </ul>
      </div>
      <div>
        <h2>Seiten</h2>
        <ul>
          <li><a href="/veranstaltungen/">Veranstaltungen</a></li>
          <li><a href="/archiv/">Archiv</a></li>
          <li><a href="/referenten/">Referenten</a></li>
          <li><a href="/fotogalerie/">Fotogalerie</a></li>
          <li><a href="/presse/">Presse</a></li>
        </ul>
      </div>
      <div>
        <h2>Weitere Angebote</h2>
        <ul>
          <li><a href="{SHOP_SEMINARE}" rel="noopener">Anmeldung &amp; Shop</a></li>
        </ul>
        {social_links("social social--footer", labels=True)}
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {datetime.date.today().year} IOS Hannover</span>
      <span><a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a></span>
    </div>
  </div>
</footer>
</body>
</html>
"""


def pdf_link(file, label="Flyer"):
    url = file if file.startswith("http") else PDF + file
    return f'<a class="pdf-link" href="{e(url)}">{e(label)}</a>'


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------

def split_words(text):
    """Überschrift in Wörter zerlegen, damit sie Wort für Wort einblenden kann."""
    return " ".join(
        f'<span class="w"><span style="--i:{i}">{w}</span></span>' for i, w in enumerate(text.split())
    )


def connector(direction):
    """Geschwungener Bogendraht, der beim Scrollen nach rechts oder links führt."""
    if direction == "right":
        d = "M 60 10 C 60 120, 1140 60, 1140 190"
    else:
        d = "M 1140 10 C 1140 120, 60 60, 60 190"
    return (
        f'<div class="connector connector--{direction}" aria-hidden="true">'
        f'<svg viewBox="0 0 1200 200" preserveAspectRatio="none"><path d="{d}" pathLength="1"/></svg>'
        f'<span class="connector-hint">{"weiter nach rechts →" if direction == "right" else "← weiter nach links"}</span></div>'
    )


def page_start():
    kongresse = load("kongresse")
    seminare = load("seminare")
    people = load("referenten")
    presse = load("presse")

    # Geschichte: chronologisch, plus das 30. Symposium 2026
    hist = "\n".join(
        f'<li class="h-card" style="--i:{i}"><span class="h-year">{k["jahr"]}</span>'
        f'<span class="h-dot" aria-hidden="true"></span>'
        f'<strong>{k["nr"]}. Symposium</strong><span>{e(k["datum"])}</span><span>{e(k["ort"])}</span></li>'
        for i, k in enumerate(sorted(kongresse, key=lambda k: (k["jahr"], k["nr"])))
    )
    hist += (
        '<li class="h-card h-card--now"><span class="h-year">2026</span><span class="h-dot" aria-hidden="true"></span>'
        '<strong>30. Symposium</strong><span>29.–30.05.2026</span><span>Prag, Hotel Josef</span></li>'
    )

    # Referenten: die mit den meisten Auftritten zuerst
    top = sorted(people, key=lambda p: -len(p["events"]))[:12]
    ref_cards = "\n".join(
        f'<li class="r-card"><span class="avatar" aria-hidden="true">{initials(p["name"])}</span>'
        f'<strong>{e(p["name"])}</strong>'
        f'<span class="r-count">{len(p["events"])} {"Auftritt" if len(p["events"]) == 1 else "Auftritte"}</span>'
        f'<span class="r-events">{e(", ".join(ev["label"] for ev in p["events"]))}</span></li>'
        for p in top
    )

    press_cards = "\n".join(
        f'<li class="p-card reveal" style="--i:{i}"><span class="p-source">{e(p["quelle"])}</span>'
        f'<a class="pdf-link" href="{e(PDF + p["pdf"])}">{e(p["titel"])}</a></li>'
        for i, p in enumerate([p for p in presse if p.get("pdf")][:6])
    )

    body = f"""
<section class="hero" id="start">
  <div class="hero-media" aria-hidden="true">
    <img src="/assets/img/ios-prague-banner.jpg" alt="" width="830" height="600" fetchpriority="high">
  </div>
  <div class="hero-arch" aria-hidden="true">{arch_svg("hero-art")}</div>
  <div class="wrap hero-inner">
    <p class="eyebrow">Interdisciplinary Orthodontic Seminars · seit 2000</p>
    <h1 aria-label="Kieferorthopädie, die über den Tellerrand blickt.">{split_words("Kieferorthopädie, die über den Tellerrand blickt.")}</h1>
    <p class="lead">Führende Köpfe aus Kieferorthopädie, Zahnmedizin und Medizin an einem Tisch – in Seminaren
    in Hannover und beim International Orthodontic Symposium in Prag.</p>
    <div class="actions">
      <a class="btn btn--light btn--lg" href="#veranstaltungen">Veranstaltungen ansehen</a>
      <a class="btn btn--outline btn--lg" href="#kontakt">Kontakt aufnehmen</a>
    </div>
    <div class="hero-social">
      <span>Folgen Sie uns</span>
      {social_links("social social--hero")}
    </div>
  </div>
  <div class="hero-stats">
    <dl class="wrap">
      <div><dd>2000</dd><dt>gegründet in Hannover</dt></div>
      <div><dd>30</dd><dt>Symposien in Prag</dt></div>
      <div><dd>{len(people)}</dd><dt>Referentinnen &amp; Referenten</dt></div>
      <div><dd>35+</dd><dt>Nationen zu Gast</dt></div>
    </dl>
  </div>
  <a class="scroll-cue" href="#philosophie" aria-label="Weiter nach unten"><i aria-hidden="true"></i></a>
</section>

<section class="station station--light" id="philosophie">
  <div class="wrap split">
    <div class="reveal">
      <p class="kicker">01 · Philosophie</p>
      <h2 class="statement">Gesunde Kaufunktion entsteht im Team.</h2>
    </div>
    <div class="reveal" style="--i:1">
      <p>Der Gründer des Arbeitskreises für Biosystemische Zahnheilkunde, <strong>Dr. Jan V. Raiman</strong>, steht für
      eine moderne, ganzheitliche Kieferorthopädie, die über Fachgrenzen hinweg arbeitet – von der Frühbehandlung
      bei Kindern bis zur Therapie Erwachsener im „besten Alter“.</p>
      <p>Wir laden die besten interdisziplinär arbeitenden Kolleginnen und Kollegen nach Hannover ein, um Wissen
      zu teilen und neue Erkenntnisse zum Wohl der Patientinnen und Patienten einzusetzen.</p>
      <a class="more" href="/philosophie/">Mehr zur Philosophie <span aria-hidden="true">→</span></a>
    </div>
  </div>
  {connector("right")}
</section>

<section class="hscroll hscroll--right" id="geschichte" aria-label="Geschichte">
  <div class="hscroll-sticky">
    <div class="hscroll-track">
      <div class="h-intro">
        <p class="kicker">02 · Geschichte</p>
        <h2>Von der Prager Stadtbibliothek zum 30. Symposium.</h2>
        <p><span class="pinned-only">Scrollen Sie weiter – die Zeitleiste fährt mit Ihnen nach rechts.</span><span class="swipe-only">Wischen Sie nach links, um durch die Jahre zu blättern.</span></p>
      </div>
      <ol class="h-list">
{hist}
      </ol>
      <div class="h-outro">
        <p>Alle Symposien und {len(seminare)} Seminare mit Flyern:</p>
        <a class="btn" href="/archiv/">Zum Archiv</a>
      </div>
    </div>
    <div class="hscroll-bar" aria-hidden="true"><span></span></div>
  </div>
</section>

<section class="station" id="veranstaltungen">
  <div class="wrap">
    <div class="station-head reveal">
      <p class="kicker">03 · Veranstaltungen</p>
      <h2>Lernen in Hannover. Austauschen in Prag.</h2>
    </div>
    <div class="offer-grid">
      <article class="offer reveal">
        <p class="offer-tag">Seminare</p>
        <h3>Fortbildung in Hannover</h3>
        <p>Workshops und Seminare zu CMD, Frühbehandlung, Parodontologie, Implantologie und mehr – mit
        Referentinnen und Referenten aus ganz Europa.</p>
        <a class="btn" href="{SHOP_SEMINARE}" rel="noopener">Seminare &amp; Anmeldung</a>
      </article>
      <article class="offer offer--dark reveal" style="--i:1">
        <img class="offer-img" src="/assets/img/prag-abend.jpg" alt="Abendstimmung an der Moldau in Prag" width="458" height="288" loading="lazy">
        <p class="offer-tag">International Orthodontic Symposium</p>
        <h3>Zwei Tage Prag</h3>
        <dl class="facts">
          <div><dt>Zuletzt</dt><dd>30. Symposium · 29.–30. Mai 2026</dd></div>
          <div><dt>Ort</dt><dd>Hotel Josef, Prager Altstadt</dd></div>
          <div><dt>Themen</dt><dd>Aligner, digitale Workflows, Kiefergelenk</dd></div>
          <div><dt>Punkte</dt><dd>9 internationale / 12 deutsche CE-Punkte</dd></div>
        </dl>
        <a class="btn btn--light" href="{PRAGUE}" rel="noopener">IOS Prague</a>
      </article>
    </div>
    <div class="callout reveal">
      <p><strong>Referent werden?</strong> Wir suchen qualifizierte Referentinnen und Referenten aus ganz Europa.</p>
      <a class="more" href="mailto:{ORG["email"]}?subject=Referent%20werden">Schreiben Sie uns <span aria-hidden="true">→</span></a>
    </div>
  </div>
  {connector("left")}
</section>

<section class="hscroll hscroll--left" id="referenten" aria-label="Referenten">
  <div class="hscroll-sticky">
    <div class="hscroll-track">
      <div class="h-intro">
        <p class="kicker">04 · Referenten</p>
        <h2>{len(people)} Köpfe, die uns Wissen geschenkt haben.</h2>
        <p><span class="pinned-only">Diesmal geht es nach links – hier die Referenten mit den meisten Auftritten.</span><span class="swipe-only">Die Referenten mit den meisten Auftritten – zum Blättern wischen.</span></p>
      </div>
      <ul class="r-list">
{ref_cards}
      </ul>
      <div class="h-outro">
        <p>Alle {len(people)} Namen, durchsuchbar:</p>
        <a class="btn" href="/referenten/">Alle Referenten</a>
      </div>
    </div>
    <div class="hscroll-bar" aria-hidden="true"><span></span></div>
  </div>
</section>

<section class="station station--light" id="presse">
  <div class="wrap">
    <div class="station-head reveal">
      <p class="kicker">05 · Presse</p>
      <h2>Was Fachmedien über uns schreiben.</h2>
    </div>
    <ul class="press-grid">
{press_cards}
    </ul>
    <div class="row-links reveal">
      <a class="more" href="/presse/">Alle {len(presse)} Presseberichte <span aria-hidden="true">→</span></a>
      <a class="more" href="/fotogalerie/">Fotogalerie <span aria-hidden="true">→</span></a>
    </div>
  </div>
</section>

<section class="station station--dark" id="kontakt">
  <div class="wrap split">
    <div class="reveal">
      <p class="kicker">06 · Kontakt</p>
      <h2 class="statement">Fragen? Wir sind gern für Sie da.</h2>
      <div class="actions">
        <a class="btn btn--light" href="mailto:{ORG["email"]}">E-Mail schreiben</a>
        <a class="btn btn--outline" href="tel:{ORG["phone"].replace(" ", "")}">Anrufen</a>
      </div>
    </div>
    <dl class="facts reveal" style="--i:1">
      <div><dt>Office</dt><dd>{ORG["street"]}, {ORG["zip"]} {ORG["city"]}</dd></div>
      <div><dt>Telefon</dt><dd><a href="tel:{ORG["phone"].replace(" ", "")}">{ORG["phone_display"]}</a></dd></div>
      <div><dt>E-Mail</dt><dd><a href="mailto:{ORG["email"]}">{ORG["email"]}</a></dd></div>
      <div><dt>Ansprechpartner</dt><dd><a href="/kontakt/">Team &amp; Zuständigkeiten</a></dd></div>
      <div><dt>Social Media</dt><dd>{social_links("social social--contact", labels=True)}</dd></div>
    </dl>
  </div>
  <div class="wrap partners reveal">
    <p class="kicker">Partner</p>
    <ul class="toc">
      <li><a href="https://www.kfobb.de/" rel="noopener">KFO Berlin-Brandenburg</a></li>
      <li><a href="https://www.isp-gmbh.de/" rel="noopener">ISP GmbH</a></li>
      <li><a href="https://www.meinepraxis.de/" rel="noopener">meinepraxis.de</a></li>
    </ul>
  </div>
</section>
"""
    return {
        "path": "/", "body_class": "is-home",
        "title": "IOS Hannover – Interdisziplinäre kieferorthopädische Seminare",
        "description": "IOS Hannover organisiert seit 2000 Seminare zur interdisziplinären Kieferorthopädie in Hannover und das International Orthodontic Symposium in Prag.",
        "jsonld": [org_jsonld(), {
            "@context": "https://schema.org", "@type": "WebSite",
            "name": "IOS Hannover", "url": SITE + "/", "inLanguage": "de",
        }],
        "body": body,
    }


def page_philosophie():
    body = """
<div class="wrap">
  <div class="prose">
    <p>Der Gründer des Arbeitskreises für Biosystemische Zahnheilkunde, <strong>Dr. Jan V. Raiman</strong>,
    ist bekannt als Verfechter einer modernen, ganzheitlich ausgerichteten Kieferorthopädie, die
    interdisziplinär arbeitet und das Zusammenspiel von Wissenschaft und Praxis in den Mittelpunkt stellt.</p>

    <h2>Zusammenarbeit in jedem Alter</h2>
    <p>Nicht nur die gezielte Frühbehandlung bei kleinen Patientinnen und Patienten zeigt, wie wichtig die
    enge Zusammenarbeit von Kieferorthopädie, Zahnmedizin und Medizin aller Fachrichtungen ist. Auch die
    Behandlung Erwachsener – gerade im „besten Alter“ – erfordert eine gut abgestimmte Zusammenarbeit der
    zahnärztlichen Disziplinen.</p>
    <p>Die jahrelange Beanspruchung des Gebisses hinterlässt vielfältige Abnutzungserscheinungen. Beschwerden,
    die eine gesunde Kaufunktion stören, lassen sich nur durch eine planvoll abgestimmte Behandlung mehrerer
    Expertinnen und Experten erfolgreich behandeln. Ziel dieses interdisziplinären, biosystemischen Ansatzes
    ist es, die gesunde Kaufähigkeit wiederherzustellen.</p>

    <h2>Lernen von den Besten</h2>
    <p>Im Arbeitskreis möchten wir die Philosophie und das Können der besten biosystemisch und interdisziplinär
    behandelnden Kolleginnen und Kollegen vorstellen – etwa Prof. Dr. Vincent G. Kokich. Wir laden diese
    Expertinnen und Experten nach Hannover ein, um Wissen zu teilen und neue Erkenntnisse zum Wohl unserer
    Patientinnen und Patienten einzusetzen.</p>
    <div class="note"><p>Eine Übersicht aller bisherigen Referentinnen und Referenten finden Sie unter
    <a href="/referenten/">Referenten</a>.</p></div>
  </div>
</div>
"""
    return {
        "h1": f"""Unsere Philosophie""", "lead": f"""Moderne Kieferorthopädie gelingt am besten im Team – über Fachgrenzen hinweg.""",
        "path": "/philosophie/", "crumb": "Philosophie",
        "title": "Philosophie – interdisziplinäre Kieferorthopädie | IOS Hannover",
        "description": "Ganzheitliche, interdisziplinäre Kieferorthopädie: Wie IOS Hannover Wissenschaft und Praxis verbindet und führende Experten nach Hannover holt.",
        "body": body,
    }


def page_veranstaltungen():
    body = f"""
<div class="wrap">
  <ul class="toc" aria-label="Auf dieser Seite">
    <li><a href="#seminare">Seminare in Hannover</a></li>
    <li><a href="#symposium">Symposium in Prag</a></li>
    <li><a href="#referent-werden">Referent werden</a></li>
  </ul>

  <section class="section" id="seminare">
    <h2>Seminare in Hannover</h2>
    <p class="prose">Unser aktuelles Seminarangebot mit Terminen, Preisen und Anmeldung finden Sie
    in unserem Online-Shop.</p>
    <div class="actions"><a class="btn" href="{SHOP_SEMINARE}" rel="noopener">Seminare ansehen &amp; anmelden</a></div>
  </section>

  <section class="section" id="symposium">
    <h2>International Orthodontic Symposium (IOS Prague)</h2>
    <div class="prose">
      <p>Seit 2000 organisiert IOS Hannover das International Orthodontic Symposium in Prag – zwei Tage
      Vorträge internationaler Referentinnen und Referenten in familiärer Atmosphäre, dazu ein
      Get-Together in einem traditionellen Prager Gasthaus.</p>
      <p>2026 fand das <strong>30. Symposium am 29. und 30. Mai</strong> im Hotel Josef in der Prager Altstadt
      statt. Schwerpunkte waren Aligner-Therapie, digitale Workflows und das Kiefergelenk.</p>
      <div class="note"><p>Programm, Termine und Anmeldung zum nächsten Symposium:
      <a href="{PRAGUE}" rel="noopener">ios-prague.com</a></p></div>
    </div>
    <div class="actions">
      <a class="btn" href="{SHOP_SYMPOSIUM}" rel="noopener">Zur Anmeldung</a>
      <a class="btn btn--ghost" href="/archiv/#kongresse">Frühere Symposien</a>
    </div>
  </section>

  <section class="section" id="referent-werden">
    <h2>Referent werden</h2>
    <p class="prose">Für unsere Seminare und Kongresse suchen wir qualifizierte Referentinnen und Referenten
    aus ganz Europa. Sie möchten selbst ein Seminar halten oder eine Kollegin bzw. einen Kollegen empfehlen?
    Wir freuen uns auf Ihre Nachricht.</p>
    <div class="actions"><a class="btn btn--ghost" href="mailto:{ORG["email"]}?subject=Referent%20werden">E-Mail schreiben</a></div>
  </section>
</div>
"""
    return {
        "h1": f"""Seminare &amp; Symposium""", "lead": f"""Fortbildungen in Hannover und das International Orthodontic Symposium in Prag – Anmeldung bequem online.""",
        "path": "/veranstaltungen/", "crumb": "Veranstaltungen",
        "title": "Seminare & Symposium – Fortbildung Kieferorthopädie | IOS Hannover",
        "description": "Kieferorthopädische Seminare in Hannover und das International Orthodontic Symposium in Prag: Termine, Anmeldung und Infos für Referenten.",
        "body": body,
    }


def page_archiv():
    kongresse = load("kongresse")
    seminare = load("seminare")

    k_items = "\n".join(
        f'<li><span class="when">{e(k["datum"])}</span>'
        f'<span><span class="what">{k["nr"]}. International Orthodontic Symposium</span><br>'
        f'<span class="where">{e(k["ort"])}</span></span></li>'
        for k in kongresse
    )

    by_year = OrderedDict()
    for s in seminare:
        by_year.setdefault(s["jahr"], []).append(s)
    s_html = ""
    for year, items in by_year.items():
        rows = "\n".join(
            f'<li><span class="when">{e(s["datum"])}</span><span>'
            f'<span class="what">{e(s["titel"])}</span><br>'
            f'<span class="who">{e(s["referent"])}</span> · <span class="where">{e(s["ort"])}</span>'
            + (f'<br><span class="pdf">{pdf_link(s["pdf"])}</span>' if s.get("pdf") else "")
            + "</span></li>"
            for s in items
        )
        s_html += f'<h3 class="year-head">{year}</h3>\n<ul class="list list--timeline">{rows}</ul>\n'

    body = f"""
<div class="wrap">
  <ul class="toc" aria-label="Auf dieser Seite">
    <li><a href="#kongresse">Kongresse ({len(kongresse)})</a></li>
    <li><a href="#seminare">Seminare ({len(seminare)})</a></li>
    <li><a href="/fotogalerie/">Fotogalerie</a></li>
  </ul>

  <section class="section" id="kongresse">
    <h2>International Orthodontic Symposium</h2>
    <ul class="list list--timeline">
{k_items}
    </ul>
  </section>

  <section class="section" id="seminare">
    <h2>Seminare</h2>
    {s_html}
  </section>
</div>
"""
    return {
        "h1": f"""Archiv: Kongresse &amp; Seminare""", "lead": f"""Alle bisherigen Veranstaltungen von IOS Hannover seit dem Jahr 2000.""",
        "path": "/archiv/", "crumb": "Archiv",
        "title": "Archiv: Kongresse & Seminare seit 2000 | IOS Hannover",
        "description": "Alle International Orthodontic Symposien in Prag und Seminare von IOS Hannover seit 2000 – mit Referenten, Orten und Flyern als PDF.",
        "body": body,
    }


def sort_key(name):
    # Nach Nachnamen sortieren (Titel und Namenszusätze überspringen)
    skip = {"dr.", "prof.", "pd", "ass.", "priv.doz.", "dr.med.", "med."}
    parts = [p for p in name.replace(",", " ").split() if p.lower() not in skip]
    suffix = {"dds", "dmsc", "msc", "mds", "msd", "jr.", "phd"}
    parts = [p for p in parts if p.lower() not in suffix]
    last = parts[-1] if parts else name
    if "van der" in name.lower():
        last = "Linden"
    if "Kokich" in name:
        last = "Kokich"
    if "Keles" in name:
        last = "Keles"
    return last.lower().translate(str.maketrans("äöüčďš", "aoucds"))


def initials(name):
    skip = {"dr.", "prof.", "pd", "ass.", "h.c.", "med."}
    words = [w for w in name.replace(",", " ").split() if w.lower() not in skip and w[0].isupper()]
    last = sort_key(name)
    first = words[0][0] if words else ""
    return e(first + last[0].upper())


def page_referenten():
    people = load("referenten")
    people.sort(key=lambda p: (sort_key(p["name"]), p["name"]))
    groups = OrderedDict()
    for p in people:
        groups.setdefault(sort_key(p["name"])[0].upper(), []).append(p)

    def events(p):
        parts = []
        for ev in p["events"]:
            if ev.get("pdf"):
                parts.append(f'<a href="{e(ev["pdf"])}">{e(ev["label"])}</a>')
            else:
                parts.append(e(ev["label"]))
        return ", ".join(parts) if parts else "–"

    letters = "".join(f'<li><a href="#buchstabe-{k}">{k}</a></li>' for k in groups)
    blocks = ""
    for k, items in groups.items():
        lis = "\n".join(
            f'<li data-person><span class="avatar" aria-hidden="true">{initials(p["name"])}</span>'
            f'<span><span class="name">{e(p["name"])}</span>'
            f'<span class="events">{events(p)}</span></span></li>'
            for p in items
        )
        blocks += f'<section class="letter-group" id="buchstabe-{k}"><h2>{k}</h2><ul class="people">{lis}</ul></section>\n'

    body = f"""
<div class="wrap">
  <div class="filter" role="search">
    <label for="speaker-filter">Suchen</label>
    <input id="speaker-filter" type="search" placeholder="Name, Ort oder Jahr – z. B. „Prag 2012“" autocomplete="off">
    <span class="filter-count" id="speaker-count" aria-live="polite"></span>
  </div>
  <ul class="letters" aria-label="Nach Anfangsbuchstabe">{letters}</ul>
  {blocks}
  <p class="filter-count" style="margin-top:2rem">Verlinkte Veranstaltungen öffnen den Flyer als PDF.</p>
</div>
"""
    return {
        "h1": f"""Unsere Referentinnen und Referenten""", "lead": f"""Wir danken den {len(people)} Referentinnen und Referenten, die uns seit 2000 mit fachkundigen und lebendigen Vorträgen wertvolles Wissen vermittelt haben.""",
        "path": "/referenten/", "crumb": "Referenten",
        "title": "Referenten seit 2000 – Kieferorthopädie-Experten | IOS Hannover",
        "description": f"Alle {len(people)} Referentinnen und Referenten der IOS-Seminare und -Symposien seit 2000 – durchsuchbar nach Name, Ort und Jahr.",
        "body": body,
    }


def page_presse():
    items = load("presse")
    rows = "\n".join(
        f'<li><span class="when">{e(p["quelle"])}</span><span>'
        + (f'<a class="pdf-link what" href="{e(PDF + p["pdf"])}">{e(p["titel"])}</a>' if p.get("pdf")
           else f'<span class="what">{e(p["titel"])}</span>')
        + "</span></li>"
        for p in items
    )
    body = f"""
<div class="wrap">
  <ul class="list">
{rows}
  </ul>
  <p class="filter-count" style="margin-top:1rem">Abkürzungen: DZW – Die ZahnarztWoche, KN – Kieferorthopädie Nachrichten,
  ZKN – Zahnärztekammer Niedersachsen, GZM – Ganzheitliche ZahnMedizin.</p>
</div>
"""
    return {
        "h1": f"""Presseberichte""", "lead": f"""Was Fachmedien über die Seminare und Symposien von IOS Hannover geschrieben haben.""",
        "path": "/presse/", "crumb": "Presse",
        "title": "Presseberichte über IOS Hannover & IOS Prague",
        "description": "Presseberichte aus Fachmedien (DZW, KN, ZKN, KFO Zeitung) über die Seminare von IOS Hannover und das International Orthodontic Symposium in Prag.",
        "body": body,
    }


def page_fotogalerie():
    mail = (
        f"mailto:{ORG['email']}?subject=Zugang%20Fotogalerie&body="
        "Guten%20Tag%2C%0A%0Abitte%20senden%20Sie%20mir%20den%20Link%20zu%20den%20Fotogalerien.%0A%0A"
        "Name%3A%20%0AVeranstaltung(en)%3A%20%0A%0AVielen%20Dank!"
    )
    body = f"""
<div class="wrap">
  <div class="prose">
    <p>Zum Schutz der Persönlichkeitsrechte unserer Teilnehmenden versenden wir den Zugang zu den
    Fotogalerien nur an uns bekannte Personen.</p>
    <p>Schreiben Sie uns einfach eine kurze E-Mail mit Ihrem Namen und der Veranstaltung, an der Sie
    teilgenommen haben – wir schicken Ihnen den Link zu.</p>
    <div class="actions"><a class="btn" href="{mail}">Zugang per E-Mail anfordern</a></div>
  </div>
</div>
"""
    return {
        "h1": f"""Fotogalerie""", "lead": f"""Bilder unserer Seminare und Symposien.""",
        "path": "/fotogalerie/", "crumb": "Fotogalerie", "nav": "/archiv/",
        "title": "Fotogalerie – Zugang anfordern | IOS Hannover",
        "description": "Fotos der Seminare und Symposien von IOS Hannover: Teilnehmende können den Zugang zur Fotogalerie per E-Mail anfordern.",
        "body": body,
    }


def page_kontakt():
    team = [
        ("Dr. Dr. h.c. Jan V. Raiman", "Mediatoring &amp; Organisation", None, "jan@raiman.de",
         ("https://www.raiman.de/", "www.raiman.de")),
        ("Dr. Doreen Jaeschke", "Scientific Public Relation Service", ("+491792022587", "+49 179 / 20 22 58 7"),
         "doreen_jaeschke@web.de", None),
        ("Viktor Hense", "Repräsentant Asien", ("+491747740569", "+49 174 / 77 40 56 9"), "viktor-hense@mail.ru", None),
    ]
    cards = ""
    for name, role, tel, mail, web in team:
        lines = ""
        if tel:
            lines += f'<li><span>Telefon</span><a href="tel:{tel[0]}">{tel[1]}</a></li>'
        lines += f'<li><span>E-Mail</span><a href="mailto:{mail}">{mail}</a></li>'
        if web:
            lines += f'<li><span>Web</span><a href="{web[0]}" rel="noopener">{web[1]}</a></li>'
        cards += f'<div class="card"><div class="meta">{role}</div><h3>{name}</h3><ul class="contact-lines">{lines}</ul></div>\n'

    body = f"""
<div class="wrap">

  <div class="contact-main">
    <div class="card">
      <div class="meta">Büro</div>
      <h2>Office IOS Hannover</h2>
      <address>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}</address>
      <ul class="contact-lines">
        <li><span>Telefon</span><a href="tel:{ORG["phone"].replace(" ", "")}">{ORG["phone_display"]}</a></li>
        <li><span>Fax</span><span>{ORG["fax_display"]}</span></li>
        <li><span>E-Mail</span><a href="mailto:{ORG["email"]}">{ORG["email"]}</a></li>
      </ul>
      <div class="actions">
        <a class="btn" href="mailto:{ORG["email"]}">E-Mail schreiben</a>
        <a class="btn btn--ghost" href="tel:{ORG["phone"].replace(" ", "")}">Anrufen</a>
      </div>
    </div>
    <div class="card">
      <div class="meta">Ihr Anliegen</div>
      <h2>Wobei können wir helfen?</h2>
      <ul class="contact-lines">
        <li><span>Anmeldung</span><a href="{SHOP_SEMINARE}" rel="noopener">Seminare im Shop</a></li>
        <li><span>Symposium</span><a href="{PRAGUE}" rel="noopener">IOS Prague</a></li>
        <li><span>Referent</span><a href="mailto:{ORG["email"]}?subject=Referent%20werden">Seminar anbieten</a></li>
        <li><span>Feedback</span><a href="mailto:{ORG["email"]}?subject=Feedback">Ideen &amp; Anregungen</a></li>
      </ul>
    </div>
  </div>

  <section class="section">
    <h2>Ansprechpartner</h2>
    <div class="grid">
{cards}
    </div>
    <p class="filter-count" style="margin-top:1rem">Im Team außerdem: Heiko Sommer, Marko Krentz und Olina Raiman –
    erreichbar über das Office.</p>
  </section>

  <section class="section">
    <h2>Referent werden</h2>
    <p class="prose">Für unsere Seminare und Kongresse suchen wir qualifizierte Referentinnen und Referenten aus
    ganz Europa. Sie möchten ein Seminar halten oder jemanden empfehlen? Schreiben Sie uns.</p>
  </section>

  <section class="section">
    <h2>Feedback</h2>
    <p class="prose">Anmerkungen zur Website, Wünsche für das Symposium oder Ideen für künftige Themen?
    Wir freuen uns auf Ihre Rückmeldung.</p>
  </section>
</div>
"""
    jsonld = org_jsonld()
    jsonld["contactPoint"] = [{
        "@type": "ContactPoint", "contactType": "customer service",
        "telephone": ORG["phone"], "email": ORG["email"], "availableLanguage": ["de", "en"],
    }]
    return {
        "h1": f"""Kontakt""", "lead": f"""Fragen zu Seminaren, zur Anmeldung oder zum Symposium? Wir sind gern für Sie da.""",
        "path": "/kontakt/", "crumb": "Kontakt",
        "title": "Kontakt – IOS Hannover | Interdisciplinary Orthodontic Seminars",
        "description": "Kontakt zu IOS Hannover: Sutelstraße 2, 30659 Hannover, Tel. +49 511 5331693, info@ios-hannover.de – Anmeldung, Referentenanfragen und Feedback.",
        "jsonld": [jsonld,
                   {"@context": "https://schema.org", "@type": "ContactPage", "url": SITE + "/kontakt/",
                    "about": {"@id": SITE + "/#organisation"}}],
        "body": body,
    }


def page_impressum():
    body = f"""
<div class="wrap">
  <div class="prose">
    <h2>Angaben gemäß § 5 DDG</h2>
    <p>Dr. Jan V. Raiman<br>IOS Hannover<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}</p>

    <h2>Kontakt</h2>
    <p>Telefon: {ORG["phone_display"]}<br>Fax: {ORG["fax_display"]}<br>
    E-Mail: <a href="mailto:{ORG["email"]}">{ORG["email"]}</a></p>

    <h2>Zuständige Aufsichtsbehörde</h2>
    <p>Bezirksregierung Hannover</p>

    <h2>Umsatzsteuer-Identifikationsnummer</h2>
    <p>gemäß § 27a Umsatzsteuergesetz: DE 249690381</p>

    <p>Dieses Impressum gilt auch für die Facebook-Seite von IOS Hannover.</p>

    <h2>Haftung für Inhalte</h2>
    <p>Die Inhalte dieser Website wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit
    und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen.</p>

    <h2>Haftung für Links</h2>
    <p>Diese Website enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben.
    Für diese fremden Inhalte ist stets der jeweilige Anbieter oder Betreiber verantwortlich. Zum Zeitpunkt der
    Verlinkung waren keine Rechtsverstöße erkennbar. Werden uns Rechtsverletzungen bekannt, entfernen wir
    derartige Links umgehend.</p>

    <h2>Urheberrecht</h2>
    <p>Die auf dieser Website veröffentlichten Inhalte und Werke unterliegen dem deutschen Urheberrecht.
    Vervielfältigung, Bearbeitung und Verbreitung außerhalb der Grenzen des Urheberrechts bedürfen der
    schriftlichen Zustimmung des jeweiligen Autors bzw. Urhebers. Kopien für den privaten, nicht kommerziellen
    Gebrauch sind gestattet. Links auf diese Website sind jederzeit willkommen.</p>
  </div>
</div>
"""
    return {
        "h1": f"""Impressum""", "lead": f"""""",
        "path": "/impressum/", "crumb": "Impressum", "noindex": True, "nav": None,
        "title": "Impressum | IOS Hannover",
        "description": "Impressum von IOS Hannover – Dr. Jan V. Raiman, Sutelstraße 2, 30659 Hannover.",
        "body": body,
    }


def page_datenschutz():
    body = f"""
<div class="wrap">
  <div class="prose">
    <h2>1. Verantwortliche Stelle</h2>
    <p>IOS Hannover<br>Dr. Jan V. Raiman<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}<br>
    Telefon: {ORG["phone_display"]}<br>
    E-Mail: <a href="mailto:datenschutz@ios-hannover.de">datenschutz@ios-hannover.de</a></p>

    <h2>2. Aufruf der Website (Server-Logfiles)</h2>
    <p>Beim Aufruf dieser Website speichert unser Hosting-Anbieter automatisch technische Informationen, die Ihr
    Browser übermittelt: Browsertyp und -version, Betriebssystem, Referrer-URL, IP-Adresse sowie Datum und
    Uhrzeit des Zugriffs. Diese Daten sind für den sicheren und stabilen Betrieb der Website erforderlich
    (Art. 6 Abs. 1 lit. f DSGVO) und werden nicht mit anderen Datenquellen zusammengeführt.</p>

    <h2>3. Keine Cookies, kein Tracking</h2>
    <p>Diese Website verwendet keine Cookies, keine Analyse- oder Tracking-Werkzeuge und bindet keine externen
    Schriftarten, Karten oder Videos ein. Alle Dateien werden direkt von unserem Server geladen.</p>

    <h2>4. Kontakt per E-Mail oder Telefon</h2>
    <p>Wenn Sie uns per E-Mail oder Telefon kontaktieren, verarbeiten wir Ihre Angaben ausschließlich zur
    Bearbeitung Ihrer Anfrage (Art. 6 Abs. 1 lit. b bzw. f DSGVO). Die Daten werden gelöscht, sobald sie
    dafür nicht mehr erforderlich sind und keine gesetzlichen Aufbewahrungspflichten bestehen.</p>

    <h2>5. Externe Links</h2>
    <p>Unsere Seiten verlinken auf externe Angebote, z. B. unseren Online-Shop zur Anmeldung, die Website von
    IOS Prague und unsere Facebook-Seite. Erst wenn Sie einen solchen Link anklicken, werden Daten an den
    jeweiligen Anbieter übertragen. Dort gelten dessen eigene Datenschutzhinweise.</p>

    <h2>6. Ihre Rechte</h2>
    <p>Sie haben jederzeit das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17),
    Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21).
    Wenden Sie sich dazu einfach an die oben genannte Adresse.</p>
    <p>Außerdem können Sie sich bei einer Datenschutz-Aufsichtsbehörde beschweren, für uns zuständig ist
    die Landesbeauftragte für den Datenschutz Niedersachsen.</p>

    <h2>7. Verschlüsselung</h2>
    <p>Diese Website nutzt aus Sicherheitsgründen eine TLS-Verschlüsselung. Sie erkennen sie an „https://“ in
    der Adresszeile Ihres Browsers.</p>
  </div>
</div>
"""
    return {
        "h1": f"""Datenschutzerklärung""", "lead": f"""Kurz gesagt: Diese Website setzt keine Cookies, verwendet kein Tracking und lädt keine Inhalte von Drittanbietern.""",
        "path": "/datenschutz/", "crumb": "Datenschutz", "noindex": True, "nav": None,
        "title": "Datenschutz | IOS Hannover",
        "description": "Datenschutzerklärung von IOS Hannover: keine Cookies, kein Tracking.",
        "body": body,
    }


def page_404():
    body = """
<div class="wrap">
  <ul class="toc">
    <li><a href="/">Startseite</a></li>
    <li><a href="/veranstaltungen/">Veranstaltungen</a></li>
    <li><a href="/archiv/">Archiv</a></li>
    <li><a href="/kontakt/">Kontakt</a></li>
  </ul>
</div>
"""
    return {
        "h1": f"""Seite nicht gefunden""", "lead": f"""Die gesuchte Seite gibt es nicht (mehr). Vielleicht hilft Ihnen einer dieser Links weiter:""",
        "path": "/404.html", "crumb": "Nicht gefunden", "noindex": True, "nav": None, "file": "404.html",
        "title": "Seite nicht gefunden | IOS Hannover",
        "description": "Diese Seite wurde nicht gefunden.",
        "body": body,
    }


PAGES = [
    page_start, page_philosophie, page_veranstaltungen, page_archiv, page_referenten,
    page_presse, page_fotogalerie, page_kontakt, page_impressum, page_datenschutz, page_404,
]

# Alte URLs → neue URLs (301), damit Google-Rankings und Lesezeichen erhalten bleiben
REDIRECTS = {
    "index.php": "/",
    "philosophie.php": "/philosophie/",
    "seminare.php": "/veranstaltungen/",
    "kongresse.php": "/veranstaltungen/#symposium",
    "seminar-stefan-verra-2013.php": "/archiv/#seminare",
    "registration_form.php": "/veranstaltungen/",
    "kongress_archiv.php": "/archiv/#kongresse",
    "seminar_archiv.php": "/archiv/#seminare",
    "referenten.php": "/referenten/",
    "presseberichte.php": "/presse/",
    "fotogalerie.php": "/fotogalerie/",
    "photo_form.php": "/fotogalerie/",
    "kontakt.php": "/kontakt/",
    "impressum.php": "/impressum/",
    "datenschutz.php": "/datenschutz/",
}


def htaccess():
    rules = "\n".join(
        f"RewriteRule ^{name.replace('.', '[.]')}$ {target} [R=301,L,NE]"
        for name, target in REDIRECTS.items()
    )
    return f"""# IOS Hannover – Apache-Konfiguration
# Ersetzt die alten Weiterleitungsregeln: jede Variante landet mit EINEM 301 auf https://www…

Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
RewriteEngine On

# Shop (Shopware) läuft auf ios-hannover.de ohne www – nicht anfassen
RewriteRule ^shop/ - [L]

# 1) http → https und ohne www → www in einem Schritt
RewriteCond %{{HTTPS}} off [OR]
RewriteCond %{{HTTP_HOST}} !^www\\. [NC]
RewriteRule ^(.*)$ https://www.ios-hannover.de/$1 [R=301,L]

# 2) Alte PHP-Seiten → neue Adressen
{rules}
</IfModule>

<IfModule mod_headers.c>
Header always set Strict-Transport-Security "max-age=31536000"
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set X-Frame-Options "SAMEORIGIN"
</IfModule>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml text/plain
</IfModule>

<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 0 seconds"
ExpiresByType text/css "access plus 1 week"
ExpiresByType application/javascript "access plus 1 week"
ExpiresByType image/png "access plus 1 month"
ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")

    sitemap = []
    for fn in PAGES:
        page = fn()
        target = OUT / (page.get("file") or (page["path"].strip("/") + "/index.html").lstrip("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(layout(page, page["body"]), encoding="utf-8")
        if not page.get("noindex"):
            sitemap.append(SITE + page["path"])
        print("✓", page["path"])

    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in sitemap)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
    )
    (OUT / ".htaccess").write_text(htaccess(), encoding="utf-8")
    print(f"Fertig: {len(PAGES)} Seiten in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
