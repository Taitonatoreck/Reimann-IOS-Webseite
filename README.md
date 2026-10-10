# IOS Hannover – Website

Neue, schlichte Website für **IOS Hannover – Interdisciplinary Orthodontic Seminars**
(bisher www.ios-hannover.de). Statisches HTML, kein CMS, keine Cookies, kein Tracking.

## Seitenstruktur

Die Startseite zeigt nur das Wichtigste – was IOS anbietet. Alles Weitere ist über das Menü erreichbar.

```
Start  /             Hero (Angebot in einem Satz), Zahlen, Unser Angebot (Seminare | Symposium),
                     Über uns (kurz), Kontakt + Facebook / Instagram / IOS Prague
Menü
 ├─ Seminare & Symposium  /veranstaltungen/
 ├─ Über uns              /philosophie/
 ├─ Referenten            /referenten/   (116 Namen, Suche)
 ├─ Archiv                /archiv/       (Symposien + Seminare seit 2000, Fotogalerie)
 ├─ Presse                /presse/
 └─ Kontakt               /kontakt/
Fußzeile: Impressum · Datenschutz
```

Logo: `assets/logo.svg` (als Vektorgrafik nachgezeichnet, gestochen scharf in jeder Größe).

## Bearbeiten

| Was ändern? | Wo? |
| --- | --- |
| Referenten | `content/referenten.json` |
| Archiv Kongresse / Seminare | `content/kongresse.json`, `content/seminare.json` |
| Presseberichte | `content/presse.json` |
| Texte der Seiten | `build.py` (Funktionen `page_…`) |
| Design | `assets/style.css` |

Danach neu bauen:

```bash
python3 build.py          # erzeugt ./public
python3 -m http.server -d public 8000   # Vorschau: http://localhost:8000
```

## Veröffentlichen

Den **Inhalt** von `public/` (inklusive `.htaccess`) in das Web-Verzeichnis von
www.ios-hannover.de kopieren. Diese Ordner auf dem Server bleiben unverändert:

- `/data/pdf/` – Flyer und Presseartikel (die Website verlinkt dorthin)
- `/shop/` – der Shopware-Shop (wird von der `.htaccess` nicht angefasst)

Die alten `.php`-Seiten können danach gelöscht werden. Die `.htaccess` leitet alle alten
Adressen (z. B. `kontakt.php`) mit 301 auf die neuen weiter, so bleiben Google-Rankings und
Lesezeichen erhalten.

## SEO-Verbesserungen gegenüber der alten Seite

| Vorher | Jetzt |
| --- | --- |
| Gleicher `<title>` auf allen Seiten | Eigener Title pro Seite |
| Keine Meta-Description | Description pro Seite (120–150 Zeichen) |
| Kein Viewport, nicht mobilfähig | Responsive, Handy-Menü |
| 3 Weiterleitungen (http → https → http://www → https://www) | 1 Weiterleitung direkt auf `https://www.` |
| Kein Canonical | Canonical auf jeder Seite |
| Mehrere `<h1>` | Genau eine `<h1>` pro Seite |
| `lang` fehlt, Sprache gemischt | `lang="de"`, einheitlich Deutsch |
| Sitemap von 2011 mit http-URLs | Automatisch erzeugte Sitemap, in `robots.txt` eingetragen |
| Keine strukturierten Daten | Schema.org: Organisation, Kontaktseite, Brotkrumen |
| Keine Social-Vorschau | Open Graph + Vorschaubild |
| jQuery 1.5, IE6–8-CSS, Cookie-Banner | 1 CSS + 1 kleines JS, keine externen Dateien |
| 17 tote PDF-Links (alte Prag-Flyer) | Nur noch funktionierende Links |

## Vor dem Livegang bitte prüfen

- **Impressum & Datenschutz**: Die Texte sind an die neue Seite angepasst (§ 5 DDG statt TMG,
  keine Cookies). Bitte rechtlich prüfen lassen.
- **IOS Prague**: Termin und Inhalte für das nächste Symposium auf Start- und
  Veranstaltungsseite aktualisieren, sobald sie feststehen.

## Design

Nach den Grundsätzen aus dem Skill `emil-design-eng` (`npx skills add emilkowalski/skill`,
liegt unter `.claude/skills/`): kurze Übergänge mit Ease-out-Kurve, Drück-Feedback
(`scale(0.97)`), Menü klappt vom Button aus auf, Hover-Effekte nur bei Maus,
`prefers-reduced-motion` wird beachtet, und die Suche reagiert sofort ohne Animation.
