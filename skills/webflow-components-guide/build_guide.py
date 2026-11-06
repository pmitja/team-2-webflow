"""Zgradi samostojen HTML vodič komponent iz guide.json.

Uporaba: python3 build_guide.py guide.json COMPONENTS-GUIDE.html
Slike (polje "image") so poti relativno na guide.json in se vgradijo v HTML (base64),
zato je izhod ena datoteka, ki jo stranka odpre brez interneta (razen pisav).
Samo standardna knjižnica.
"""
import base64, html, json, mimetypes, re, sys
from pathlib import Path

LABELS = {
    "en": {
        "title": "Component guide", "search": "Search components…", "intro_kicker": "For editors and developers",
        "how": "How to use components", "recipe": "Building a new section", "components": "Components",
        "use": "Use it for", "avoid": "Avoid it for", "props": "Properties", "prop": "Property", "type": "Type",
        "does": "What it does", "variants": "Variants", "used_on": "Used on", "tips": "Tips",
        "instances": "instances", "instance": "instance", "no_preview": "Preview not available. See it live on",
        "updated": "Updated", "count": "components", "empty": "No components match your search.",
        "default": "Default", "nav_start": "Start here",
    },
    "sl": {
        "title": "Vodič po komponentah", "search": "Išči komponente…", "intro_kicker": "Za urednike in developerje",
        "how": "Kako uporabljati komponente", "recipe": "Gradnja nove sekcije", "components": "Komponente",
        "use": "Uporabi za", "avoid": "Ne uporabi za", "props": "Lastnosti", "prop": "Lastnost", "type": "Tip",
        "does": "Kaj naredi", "variants": "Variante", "used_on": "Uporabljena na", "tips": "Nasveti",
        "instances": "uporab", "instance": "uporaba", "no_preview": "Predogled ni na voljo. Poglej jo na",
        "updated": "Posodobljeno", "count": "komponent", "empty": "Nobena komponenta ne ustreza iskanju.",
        "default": "Privzeto", "nav_start": "Začni tukaj",
    },
}

DEFAULT_HOW = {
    "en": [
        {"title": "Add from the panel", "text": "Open the Add panel (A), go to Components and drag the component into your section."},
        {"title": "Edit through properties", "text": "Change text, images, links and variants in the right panel under Properties. Don't edit inside the component."},
        {"title": "Pick a variant", "text": "Need a different look? Choose a variant instead of adding new classes."},
        {"title": "Don't unlink", "text": "Unlinking breaks future updates. If something is missing, ask your developer to add a property or variant."},
    ],
    "sl": [
        {"title": "Dodaj iz panela", "text": "Odpri Add panel (A), pojdi na Components in povleci komponento v sekcijo."},
        {"title": "Urejaj prek lastnosti", "text": "Tekst, slike, linke in variante spreminjaš v desnem panelu pod Properties, ne znotraj komponente."},
        {"title": "Izberi varianto", "text": "Rabiš drugačen izgled? Izberi varianto, namesto da dodajaš nove classe."},
        {"title": "Ne odklopi", "text": "Unlink prekine prihodnje posodobitve. Če kaj manjka, prosi developerja za novo lastnost ali varianto."},
    ],
}


def inline(text):
    """Escape + `code` + **bold**."""
    t = html.escape(str(text or ""))
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "c"


def data_uri(base, rel):
    if not rel:
        return None
    p = (base / rel).resolve()
    if not p.exists():
        print(f"  ! slika ne obstaja: {rel}", file=sys.stderr)
        return None
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def ul(items, cls):
    if not items:
        return ""
    return f'<ul class="{cls}">' + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"


def component(c, L, base, group):
    cid = slug(c["name"])
    n = c.get("instances")
    badges = ""
    if n is not None:
        badges += f'<span class="badge">{n} {L["instance"] if n == 1 else L["instances"]}</span>'
    if c.get("variants"):
        badges += f'<span class="badge">{len(c["variants"])} {L["variants"].lower()}</span>'

    img = data_uri(base, c.get("image"))
    used = c.get("used_on") or []
    if img:
        preview = f'<figure class="preview"><img src="{img}" alt="{html.escape(c["name"])}" loading="lazy"></figure>'
    else:
        link = ""
        if used:
            u = used[0]
            link = f' <a href="{html.escape(u.get("url", "#"))}" target="_blank" rel="noopener">{inline(u.get("page"))}</a>'
        preview = f'<figure class="preview empty"><span>{L["no_preview"]}{link}</span></figure>'

    use_avoid = ""
    if c.get("use_when") or c.get("avoid_when"):
        use_avoid = '<div class="ua">'
        if c.get("use_when"):
            use_avoid += f'<div><h4 class="ok">{L["use"]}</h4>{ul(c["use_when"], "yes")}</div>'
        if c.get("avoid_when"):
            use_avoid += f'<div><h4 class="no">{L["avoid"]}</h4>{ul(c["avoid_when"], "nope")}</div>'
        use_avoid += "</div>"

    props = ""
    if c.get("props"):
        rows = "".join(
            f'<tr><td><span class="pname">{inline(p.get("name"))}</span></td>'
            f'<td><span class="ptype">{inline(p.get("type"))}</span></td>'
            f'<td>{inline(p.get("description"))}'
            + (f'<span class="pdef">{L["default"]}: {inline(p["default"])}</span>' if p.get("default") else "")
            + "</td></tr>"
            for p in c["props"]
        )
        props = (f'<div class="block"><h4>{L["props"]}</h4><div class="tablewrap"><table><thead><tr><th>{L["prop"]}</th>'
                 f'<th>{L["type"]}</th><th>{L["does"]}</th></tr></thead><tbody>{rows}</tbody></table></div></div>')

    variants = ""
    if c.get("variants"):
        items = "".join(
            f'<div class="variant"><span class="vname">{inline(v.get("name"))}</span><span>{inline(v.get("description"))}</span></div>'
            for v in c["variants"])
        variants = f'<div class="block"><h4>{L["variants"]}</h4><div class="variants">{items}</div></div>'

    used_html = ""
    if used:
        links = "".join(
            f'<a class="page" href="{html.escape(u.get("url", "#"))}" target="_blank" rel="noopener">{inline(u.get("page"))}<span>↗</span></a>'
            for u in used)
        used_html = f'<div class="block"><h4>{L["used_on"]}</h4><div class="pages">{links}</div></div>'

    tips = ""
    if c.get("tips"):
        tips = f'<div class="tips"><h4>{L["tips"]}</h4>{ul(c["tips"], "tiplist")}</div>'

    search = " ".join([c["name"], group, c.get("description", "")] + (c.get("use_when") or [])).lower()
    return f'''
<article class="comp" id="{cid}" data-search="{html.escape(search)}">
  <header>
    <h3>{inline(c["name"])}</h3>
    <div class="badges">{badges}</div>
  </header>
  <p class="desc">{inline(c.get("description"))}</p>
  {preview}
  {use_avoid}
  {props}
  {variants}
  {used_html}
  {tips}
</article>'''


def build(src, out):
    src = Path(src)
    d = json.loads(src.read_text())
    site = d.get("site", {})
    lang = site.get("language", "en")
    L = {**LABELS.get(lang, LABELS["en"]), **d.get("labels", {})}
    brand = site.get("brand", {})
    accent = brand.get("primary", "#4F46E5")
    ink = brand.get("text", "#0F172A")
    fh = brand.get("font_heading", "Inter")
    fb = brand.get("font_body", fh)
    gfonts = site.get("google_fonts") or ["Inter:wght@400;500;600;700"]
    font_link = ("https://fonts.googleapis.com/css2?" + "&".join("family=" + f.replace(" ", "+") for f in gfonts)
                 + "&family=JetBrains+Mono:wght@400;500&display=swap")

    groups = d.get("groups", [])
    total = sum(len(g.get("components", [])) for g in groups)
    title = d.get("title") or L["title"]

    nav = f'<a href="#start" class="navstart">{L["nav_start"]}</a>'
    for g in groups:
        nav += f'<div class="navgroup"><span>{inline(g["name"])}</span>'
        nav += "".join(f'<a href="#{slug(c["name"])}" data-target="{slug(c["name"])}">{inline(c["name"])}</a>' for c in g.get("components", []))
        nav += "</div>"

    how = d.get("how_to") or DEFAULT_HOW.get(lang, DEFAULT_HOW["en"])
    how_html = "".join(f'<div class="step"><span class="n">{i+1:02d}</span><h4>{inline(s["title"])}</h4><p>{inline(s["text"])}</p></div>'
                       for i, s in enumerate(how))

    recipe_html = ""
    r = d.get("section_recipe")
    if r and r.get("tree"):
        lines = ""
        for i, node in enumerate(r["tree"]):
            pad = "&nbsp;" * (3 * max(0, i - 1))
            pre = f'<span class="t">{pad}└─ </span>' if i else ""
            cls = ' class="x"' if i in (0, len(r["tree"]) - 1) else ""
            lines += f"<div>{pre}<span{cls}>{inline(node)}</span></div>"
        recipe_html = f'''<section class="recipe"><div><h2>{L["recipe"]}</h2><p>{inline(r.get("note"))}</p></div>
          <div class="tree">{lines}</div></section>'''

    comps = ""
    for g in groups:
        comps += f'<section class="grp"><h2 class="gh">{inline(g["name"])}<span>{len(g.get("components", []))}</span></h2>'
        if g.get("description"):
            comps += f'<p class="gdesc">{inline(g["description"])}</p>'
        comps += "".join(component(c, L, src.parent, g["name"]) for c in g.get("components", []))
        comps += "</section>"

    intro = d.get("intro", "")
    page = f'''<!doctype html>
<html lang="{html.escape(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {html.escape(site.get("name", ""))}</title>
<link rel="stylesheet" href="{font_link}">
<style>
:root {{
  --accent: {accent}; --ink: {ink};
  --accent-soft: color-mix(in srgb, var(--accent) 10%, white);
  --accent-line: color-mix(in srgb, var(--accent) 28%, white);
  --text: color-mix(in srgb, var(--ink) 72%, white);
  --muted: color-mix(in srgb, var(--ink) 50%, white);
  --line: color-mix(in srgb, var(--ink) 11%, white);
  --bg: #FFFFFF; --bg-2: color-mix(in srgb, var(--ink) 3.5%, white);
  --ok: #0E9F6E; --no: #E0475F;
  --fh: "{fh}", Inter, system-ui, sans-serif; --fb: "{fb}", Inter, system-ui, sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 24px; }}
body {{ font-family: var(--fb); color: var(--ink); background: var(--bg); -webkit-font-smoothing: antialiased; line-height: 1.55; }}
a {{ color: inherit; }}
code {{ font-family: "JetBrains Mono", monospace; font-size: .86em; background: var(--accent-soft); color: var(--accent); padding: 2px 7px; border-radius: 5px; }}
strong {{ font-weight: 600; color: var(--ink); }}

.layout {{ display: grid; grid-template-columns: 290px minmax(0, 1fr); min-height: 100vh; }}
aside {{ position: sticky; top: 0; height: 100vh; overflow-y: auto; border-right: 1px solid var(--line); background: var(--bg-2); padding: 28px 22px 40px; }}
.site {{ display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }}
.site .logo {{ width: 34px; height: 34px; border-radius: 9px; background: var(--accent); color: #fff; display: grid; place-items: center; font: 700 15px var(--fh); }}
.site b {{ display: block; font: 600 15px var(--fh); }}
.site small {{ color: var(--muted); font-size: 12.5px; }}
.search {{ width: 100%; font: inherit; font-size: 14px; padding: 10px 12px 10px 36px; border: 1px solid var(--line); border-radius: 10px; background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%2394a3b8' stroke-width='2' viewBox='0 0 24 24'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m21 21-4.3-4.3'/%3E%3C/svg%3E") 12px center no-repeat; outline: none; margin-bottom: 22px; }}
.search:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }}
.navstart {{ display: block; font-size: 14px; font-weight: 600; text-decoration: none; padding: 7px 10px; border-radius: 8px; margin-bottom: 14px; }}
.navgroup {{ margin-bottom: 18px; }}
.navgroup span {{ display: block; font-size: 11.5px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); padding: 0 10px 6px; }}
.navgroup a {{ display: block; font-size: 14px; text-decoration: none; color: var(--text); padding: 6px 10px; border-radius: 8px; }}
aside a:hover {{ background: #fff; color: var(--ink); }}
aside a.active {{ background: var(--accent-soft); color: var(--accent); font-weight: 600; }}
aside a.hide {{ display: none; }}

main {{ padding: 56px 64px 120px; max-width: 1080px; width: 100%; min-width: 0; overflow-wrap: break-word; }}
.hero {{ padding-bottom: 44px; border-bottom: 1px solid var(--line); margin-bottom: 44px; }}
.kicker {{ font-size: 12.5px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); margin-bottom: 14px; }}
h1 {{ font: 700 52px/1.05 var(--fh); letter-spacing: -.03em; }}
.hero p {{ font-size: 18px; color: var(--text); max-width: 680px; margin-top: 16px; }}
.meta {{ display: flex; gap: 22px; margin-top: 26px; font-size: 14px; color: var(--muted); }}
.meta b {{ color: var(--ink); font-weight: 600; }}
h2 {{ font: 650 26px/1.2 var(--fh); font-weight: 600; letter-spacing: -.02em; }}

.how h2 {{ margin-bottom: 22px; }}
.steps {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
.step {{ border: 1px solid var(--line); border-radius: 14px; padding: 20px; background: #fff; }}
.step .n {{ font: 500 12px "JetBrains Mono", monospace; color: var(--accent); }}

.step p {{ font-size: 14px; color: var(--text); }}

.recipe {{ display: grid; grid-template-columns: 1fr 1.1fr; gap: 36px; align-items: center; margin-top: 44px; padding: 32px; border-radius: 18px; background: var(--ink); color: #fff; }}
.recipe p {{ color: color-mix(in srgb, #fff 70%, var(--ink)); margin-top: 10px; font-size: 15px; }}
.tree {{ font: 15px/1.9 "JetBrains Mono", monospace; background: color-mix(in srgb, #000 22%, var(--ink)); border-radius: 12px; padding: 20px 24px; }}
.tree .t {{ color: color-mix(in srgb, #fff 35%, var(--ink)); }}
.tree .x {{ color: color-mix(in srgb, var(--accent) 55%, white); font-weight: 500; }}

.grp {{ margin-top: 64px; }}
.gh {{ display: flex; align-items: center; gap: 12px; padding-bottom: 14px; border-bottom: 2px solid var(--ink); }}
.gh span {{ font: 500 13px "JetBrains Mono", monospace; color: var(--muted); }}
.gdesc {{ color: var(--text); margin-top: 12px; }}

.comp {{ padding: 40px 0; border-bottom: 1px solid var(--line); }}
.comp header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }}
.group {{ font-size: 12px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }}
.comp h3 {{ font: 600 28px/1.15 var(--fh); letter-spacing: -.02em; margin-top: 4px; }}
.badges {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
.badge {{ font-size: 12.5px; font-weight: 500; padding: 5px 10px; border-radius: 100px; background: var(--bg-2); border: 1px solid var(--line); color: var(--text); white-space: nowrap; }}
.desc {{ font-size: 16.5px; color: var(--text); margin-top: 12px; max-width: 760px; }}
.preview {{ margin-top: 22px; border: 1px solid var(--line); border-radius: 14px; overflow: hidden;
  background: var(--bg-2) repeating-conic-gradient(color-mix(in srgb, var(--ink) 3%, white) 0 25%, transparent 0 50%) 0 0 / 20px 20px;
  display: flex; justify-content: center; align-items: center; padding: 18px; }}
.preview img {{ display: block; max-width: 100%; max-height: 560px; height: auto; border-radius: 6px; }}
.preview.empty {{ padding: 36px; color: var(--muted); font-size: 14px; }}
.preview.empty a {{ color: var(--accent); }}

.ua {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 22px; }}
.ua > div {{ border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px; }}
h4 {{ font: 600 12.5px var(--fb); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }}
h4.ok {{ color: var(--ok); }} h4.no {{ color: var(--no); }}
ul {{ list-style: none; }}
ul li {{ font-size: 15px; color: var(--text); padding: 5px 0 5px 24px; position: relative; }}
ul.yes li::before, ul.nope li::before {{ position: absolute; left: 0; top: 5px; font-weight: 700; font-size: 13px; }}
ul.yes li::before {{ content: "✓"; color: var(--ok); }}
ul.nope li::before {{ content: "✕"; color: var(--no); }}

.block {{ margin-top: 26px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14.5px; }}
th {{ text-align: left; font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); padding: 0 16px 10px 0; border-bottom: 1px solid var(--line); }}
td {{ padding: 12px 16px 12px 0; border-bottom: 1px solid var(--line); vertical-align: top; color: var(--text); }}
td:first-child {{ width: 26%; }} td:nth-child(2) {{ width: 14%; }}
.pname {{ font-weight: 600; color: var(--ink); }}
.ptype {{ font: 12.5px "JetBrains Mono", monospace; color: var(--muted); }}
.pdef {{ display: block; font-size: 13px; color: var(--muted); margin-top: 3px; }}
.variants {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; }}
.variant {{ border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; font-size: 14px; color: var(--text); }}
.vname {{ display: block; font-weight: 600; color: var(--ink); margin-bottom: 2px; }}
.pages {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.page {{ font-size: 14px; text-decoration: none; padding: 7px 12px; border-radius: 8px; border: 1px solid var(--line); display: inline-flex; gap: 8px; }}
.page span {{ color: var(--muted); }}
.page:hover {{ border-color: var(--accent); color: var(--accent); }}
.tips {{ margin-top: 26px; background: var(--accent-soft); border: 1px solid var(--accent-line); border-radius: 14px; padding: 18px 20px; }}
.tips h4 {{ color: var(--accent); }}
.step h4 {{ font: 600 16px/1.3 var(--fh); letter-spacing: -.01em; text-transform: none; color: var(--ink); margin: 12px 0 6px; }}
.tablewrap {{ overflow-x: auto; }}
.tiplist li {{ padding-left: 16px; }}
.tiplist li::before {{ content: ""; position: absolute; left: 0; top: 14px; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }}
.noresult {{ display: none; padding: 60px 0; color: var(--muted); text-align: center; }}
footer {{ margin-top: 64px; font-size: 13px; color: var(--muted); }}

@media (max-width: 1000px) {{
  .layout {{ grid-template-columns: 1fr; }}
  aside {{ position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }}
  .navgroup, .navstart {{ display: none; }}
  main {{ padding: 36px 20px 80px; }}
  .steps {{ grid-template-columns: minmax(0, 1fr); }}
  .comp header {{ flex-direction: column; align-items: flex-start; }}
  .badges {{ justify-content: flex-start; }}
  thead {{ display: none; }}
  table, tbody, tr, td {{ display: block; width: auto !important; }}
  tr {{ padding: 12px 0; border-bottom: 1px solid var(--line); }}
  td {{ border: 0; padding: 0; }}
  td:first-child, td:nth-child(2) {{ display: inline; margin-right: 10px; }}
  td:last-child {{ margin-top: 4px; }}
  .meta {{ flex-wrap: wrap; gap: 8px 18px; }}
  .recipe, .ua {{ grid-template-columns: 1fr; }}
  h1 {{ font-size: 38px; }}
}}
@media print {{ aside {{ display: none; }} .layout {{ display: block; }} .comp {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<div class="layout">
  <aside>
    <div class="site"><span class="logo">{html.escape((site.get("name") or "?")[:1].upper())}</span>
      <div><b>{inline(site.get("name"))}</b><small>{L["title"]}</small></div></div>
    <input class="search" type="search" placeholder="{L["search"]}" aria-label="{L["search"]}">
    <nav>{nav}</nav>
  </aside>
  <main>
    <section class="hero" id="start">
      <div class="kicker">{L["intro_kicker"]}</div>
      <h1>{inline(title)}</h1>
      <p>{inline(intro)}</p>
      <div class="meta"><span><b>{total}</b> {L["count"]}</span><span>{L["updated"]} <b>{inline(site.get("generated"))}</b></span>
        {f'<span><a href="{html.escape(site["url"])}" target="_blank" rel="noopener">{inline(site["url"])}</a></span>' if site.get("url") else ""}</div>
    </section>
    <section class="how"><h2>{L["how"]}</h2><div class="steps">{how_html}</div></section>
    {recipe_html}
    {comps}
    <p class="noresult">{L["empty"]}</p>
    <footer>{inline(d.get("footer", ""))}</footer>
  </main>
</div>
<script>
const q = document.querySelector('.search'), comps = [...document.querySelectorAll('.comp')], grps = [...document.querySelectorAll('.grp')];
const links = [...document.querySelectorAll('nav a[data-target]')];
q.addEventListener('input', () => {{
  const v = q.value.trim().toLowerCase(); let any = false;
  comps.forEach(c => {{ const m = !v || c.dataset.search.includes(v); c.style.display = m ? '' : 'none'; any ||= m; }});
  grps.forEach(g => g.style.display = [...g.querySelectorAll('.comp')].some(c => c.style.display !== 'none') ? '' : 'none');
  links.forEach(a => a.classList.toggle('hide', document.getElementById(a.dataset.target).style.display === 'none'));
  document.querySelector('.noresult').style.display = any ? 'none' : 'block';
}});
const io = new IntersectionObserver(es => es.forEach(e => {{ if (e.isIntersecting) links.forEach(a => a.classList.toggle('active', a.dataset.target === e.target.id)); }}), {{ rootMargin: '-20% 0px -70% 0px' }});
comps.forEach(c => io.observe(c));
</script>
</body>
</html>'''
    Path(out).write_text(page)
    print(f"{out}: {total} komponent, {len(groups)} skupin")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uporaba: python3 build_guide.py guide.json COMPONENTS-GUIDE.html")
    build(sys.argv[1], sys.argv[2])
