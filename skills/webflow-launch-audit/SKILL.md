---
name: webflow-launch-audit
description: Pregled Webflow strani pred objavo ali predajo — dostopnost, linki, SEO in slike. Združi Webflow MCP (API) in pregled objavljene strani v brskalniku, zato najde tudi to, kar uradni Webflow audit skilli spregledajo (navbar, footer, CMS liste, custom koda, kontrast, prave velikosti slik). Samo bere, ničesar ne spreminja. Triggers: "launch audit", "pregled pred objavo", "pre-launch", "audit strani", "preveri stran pred launchom".
---

# Webflow launch audit

Pregled pred objavo ali predajo stranki. Cilj je seznam stvari, ki jih je treba popraviti, razvrščen po pomembnosti. Ni ocena 0–100 in ni splošno poročilo.

## Pravilo #1: samo branje

Skill **ničesar ne spreminja** — ne v Webflowu ne na strani. Ne kliči `create_*`, `update_*`, `rename_*`, `remove_*`, `delete_*`, `publish_*`, `compress_*`, `transform_*` ali `insert_*`. Če nekaj zna popraviti MCP (npr. pretvorba slik v WebP), to samo predlagaj v poročilu.

## Vhod

- **URL** objavljene strani: staging (`*.webflow.io`) ali produkcija. Obvezno.
- **Obseg:** katere strani pregledati. Če uporabnik ne pove, vzemi domačo stran in največ 5 glavnih strani iz navigacije, in to povej.
- Če je stran zaščitena z geslom, ga uporabnik vpiše sam v Browser panelu. Gesla ne vpisuj sam.

## Predpogoji

- Webflow MCP 2.0 povezan. Na začetku enkrat pokliči `webflow_guide_tool` in uporabljaj isti `agent_id` / `session_id`. Točna imena akcij preveri v guide-u; spodaj so našteta orodja, ki jih pričakuješ.
- Vgrajeni brskalnik (`mcp__Claude_Browser__*`).
- Če Webflow MCP ni povezan, naredi samo brskalniški del in to jasno označi v poročilu.

## Postopek

### 0. Priprava

1. `data_sites_tool` → poišči site, ki ustreza URL-ju. Če ga ni ali jih je več, vprašaj.
2. `data_pages_tool` → seznam strani z SEO nastavitvami (title, description, OG, slug, draft/arhiv, noindex). Zapomni si `pageId` domače strani.
3. Odpri URL v brskalniku na 1440 px. Če je stran pod geslom, počakaj, da ga uporabnik vpiše.

### 1. Dostopnost

**Brskalnik, na vsaki pregledani strani:**
1. Naloži axe-core in ga poženi:
   ```js
   await new Promise((ok, err) => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js'; s.onload = ok; s.onerror = err; document.head.appendChild(s); });
   const r = await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa'] });
   r.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length, primer: v.nodes[0]?.target.join(' ') }))
   ```
   Če CSP blokira skripto, to zapiši in nadaljuj z ostalimi checki.
2. **Tipkovnica:** s Tab pojdi skozi navbar in prvo sekcijo. Preveri, ali je focus viden in ali se dropdown / mobilni meni / modal odpre in zapre s tipkovnico (Enter, Esc).
3. **Reduced motion:** preveri, ali custom koda ali IX3 upošteva `prefers-reduced-motion` (poišči v `<style>` / skriptah). Samo opomba, ne kritično.

**Webflow MCP:**
4. Barvne variable (`data_variable_tool`): za pare tekst/ozadje, ki jih uporabljajo glavni classi, izračunaj kontrast. Če par ne dosega 4.5:1 (oz. 3:1 za velik tekst), predlagaj popravek **variable**, ker to popravi celo stran.
5. Ko axe najde napako na elementu, ki je del komponente (navbar, footer, kartica), napiši popravek na **komponenti ali classu**, ne na vsaki instanci posebej.

### 2. Linki

**Brskalnik** — na vsaki strani poberi vse linke, tudi tiste iz komponent in CMS list:
```js
[...document.querySelectorAll('a[href]')].map(a => ({ href: a.getAttribute('href'), abs: a.href, text: a.innerText.trim().slice(0, 60), blank: a.target === '_blank', rel: a.rel }))
```

Preveri:
- **Status:** unikatne absolutne URL-je preveri z Bash: `curl -s -o /dev/null -w "%{http_code} %{url_effective}" -L --max-time 10 "<url>"`. Prijavi 4xx/5xx in verige redirectov.
- **`http://`** linki namesto `https://`.
- **`*.webflow.io`** linki, ki bi na produkciji ostali absolutni na staging domeno.
- **Anchorji:** za vsak `#id` preveri, ali element s tem ID-jem obstaja na ciljni strani.
- Linki na **draft ali arhivirane strani** in **stare slugje** (primerjaj z `data_pages_tool`).
- `target="_blank"` brez `rel="noopener"`.
- Pokvarjeni `mailto:` in `tel:` (prazni, presledki, napačen format).
- Prazni `href`, `#` ali `javascript:void(0)` na elementih, ki izgledajo kot linki.

Če ima workspace analitiko (`data_analyze_tool`), razvrsti pokvarjene linke po prometu strani. Če je ni, to preskoči brez omembe.

### 3. SEO in site

**Webflow MCP:**
- Title (do ~60 znakov) in description (~150–160) za vsako stran; prazni ali podvojeni titli in descriptioni.
- OG slika, OG title.
- Strani z `noindex` proti **sitemapu** (`data_sitemap_tool`): kaj je v sitemapu, pa ne bi smelo biti (noindex, draft, utility strani), in obratno.
- Prilagojena **404** stran, **favicon** in **webclip**.
- **Custom koda** (`data_scripts_tool`): podvojen GA/GTM, ostanki starih skript, skripte v headu, ki bi lahko bile pred `</body>`.
- **Fonti** (`data_fonts_tool`): neuporabljene teže, manjkajoč `font-display`.

**Brskalnik:**
- `<link rel="canonical">` obstaja in kaže na pravo domeno.
- Natanko en `<h1>` na stran; ni preskočenih nivojev naslovov.
- `lang` na `<html>`.
- Ostanki: "Lorem ipsum", "Heading", "Button Text", "This is some text inside of a div block".

**Performance (samo produkcija, javna stran):** PageSpeed Insights za domačo stran in eno podstran:
`curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url>&strategy=mobile&category=performance"` → LCP, CLS, TBT in performance score. Na staging strani pod geslom tega ne delaj in to povej.

### 4. Slike

**Brskalnik** — na vsaki strani po scrollu do dna (da se naložijo lazy slike):
```js
const res = Object.fromEntries(performance.getEntriesByType('resource').map(e => [e.name, e.transferSize]));
[...document.images].map(i => ({ src: i.currentSrc, kb: Math.round((res[i.currentSrc] || 0) / 1024), natural: i.naturalWidth, shown: Math.round(i.getBoundingClientRect().width), loading: i.loading, alt: i.getAttribute('alt') }))
```

Prijavi:
- Slike nad **~300 KB** in slike v PNG/JPG, ki bi lahko bile WebP/AVIF. Predlagaj `compress_assets`, ne poganjaj ga.
- **Prevelike dimenzije:** `natural` več kot 2× `shown` (npr. 4000 px slika v 600 px boxu).
- **LCP / hero slika** z `loading="lazy"`.
- **Alt:** manjkajoč alt na vsebinskih slikah; izmišljen alt na dekorativnih (te naj imajo `alt=""`).

**Webflow MCP:** alt teksti v CMS image poljih in v sekundarnih lokalih (`localeId`), če jih site ima.

## Česa NE prijavljati

- Vsake axe opombe z `impact: minor`, razen če se ponavlja na vseh straneh.
- Zunanjih linkov, ki vrnejo 403/429 botom (LinkedIn, Twitter/X, Instagram) — označi jih kot "ni bilo mogoče preveriti", ne kot pokvarjene.
- Vrednosti PageSpeed na staging strani.
- Stilskih predlogov in mnenj o dizajnu.

## Izhod

Odgovori v slovenščini, točno v tej obliki. Vsaka točka pove **kje** (stran / komponenta), **kaj je narobe** in **kako popraviti**. Oznake: `[kritično]` (pokvari uporabo, SEO ali dostopnost), `[pomembno]`, brez oznake za manjše.

```
Pregledano: <URL> · <N> strani · <datum> · Webflow MCP: da/ne

## Najprej popravi
1. **Forma (Kontakt)** — gumb "Submit" nima labele za bralnike zaslona. → Dodaj aria-label v komponenti Button.
2. ...

## Dostopnost
- [kritično] **Navbar (komponenta)** — dropdown se ne odpre s tipkovnico. → ...
- **Footer** — kontrast sivega teksta 3.1:1. → Variabla `Text / Muted` naj bo temnejša (npr. #5A6B7B).

## Linki
- [kritično] **/pricing** — "Book a demo" vodi na /demo-old (404). → Nov slug je /demo.

## SEO in site
- [pomembno] **/blog** — description manjka.

## Slike
- [pomembno] **Domača stran, hero** — hero.png 2.4 MB, 3800 px v 1200 px boxu, `loading="lazy"`. → WebP, max 2400 px, odstrani lazy.

## Ni bilo mogoče preveriti
- PageSpeed (staging pod geslom), 3 linki na LinkedIn (403 za bote).
```

"Najprej popravi" ima največ 5 točk, samo `[kritično]` in najpomembnejše `[pomembno]`. Če v sekciji ni napak, napiši `Brez popravkov.` Ne dodajaj ocen 0–100 ali splošnih nasvetov.

Na koncu vrni viewport brskalnika na `desktop`.
