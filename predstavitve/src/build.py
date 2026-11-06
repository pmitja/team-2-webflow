"""Zgradi predstavitve: python3 src/build.py  (rabi Google Chrome in internet za pisave)."""
import re, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DECKS = {
    "pre-qa-check": "Pre-QA Check – Flowout Team 2.pdf",
    "webflow-onboarding": "Webflow Onboarding – Flowout Team 2.pdf",
    "webflow-launch-audit": "Webflow Launch Audit – Flowout Team 2.pdf",
    "webflow-components-guide": "Webflow Components Guide – Flowout Team 2.pdf",
}

I = {
 "frame": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/>',
 "browser": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18M6.5 6.5h.01M9 6.5h.01"/>',
 "compare": '<rect x="3" y="4" width="7" height="16" rx="1.5"/><rect x="14" y="4" width="7" height="16" rx="1.5"/><path d="M12 2v20"/>',
 "type": '<path d="M4 7V5h16v2M12 5v14M9 19h6"/>',
 "doc": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
 "mobile": '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>',
 "copy": '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
 "missing": '<rect x="4" y="4" width="16" height="16" rx="2" stroke-dasharray="3 3"/><path d="M9 12h6"/>',
 "loop": '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
 "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>',
 "bp": '<rect x="2" y="5" width="13" height="10" rx="1.5"/><rect x="17" y="8" width="5" height="11" rx="1.2"/><path d="M6 19h5"/>',
 "repo": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="7" r="2"/><path d="M6 7v10M18 9c0 5-7 4-11 8.5"/>',
 "vars": '<path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1M16 3h1a2 2 0 0 1 2 2v5a2 2 0 0 0 2 2 2 2 0 0 0-2 2v5a2 2 0 0 1-2 2h-1"/>',
 "comp": '<path d="M12 2.5l3.5 3.5L12 9.5 8.5 6zM6 8.5 9.5 12 6 15.5 2.5 12zM18 8.5l3.5 3.5-3.5 3.5-3.5-3.5zM12 14.5l3.5 3.5-3.5 3.5L8.5 18z"/>',
 "tag": '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
 "layout": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 9v12"/>',
 "tree": '<path d="M5 3v13a2 2 0 0 0 2 2h5M5 9h7"/><rect x="13" y="6" width="8" height="6" rx="1.5"/><rect x="13" y="15" width="8" height="6" rx="1.5"/>',
 "alert": '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
 "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 "link": '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
 "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/>',
 "a11y": '<circle cx="12" cy="4.5" r="1.6"/><path d="M5 8.5 12 10l7-1.5M12 10v4.5l-3 6.5M12 14.5l3 6.5"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
 "msg": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 9h8M8 13h5"/>',
 "rocket": '<path d="M4.5 16.5c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.2 2.2 0 0 0-2.9-.1z"/><path d="M12 15l-3-3a22 22 0 0 1 2-4A13 13 0 0 1 22 2c0 2.7-.8 7.5-6 11a22 22 0 0 1-4 2z"/><path d="M9 12H4s.6-3 2-4c1.6-1 5 0 5 0M12 15v5s3-.6 4-2c1-1.6 0-5 0-5"/>',
 "plug": '<path d="M12 22v-5M9 8V2M15 8V2M18 8v5a6 6 0 0 1-12 0V8z"/>',
 "stack": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
 "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
}

def icon(m):
    return f'<svg viewBox="0 0 24 24">{I[m.group(1)]}</svg>'

def build(name):
    html = (SRC / f"{name}.html").read_text()
    total = len(re.findall(r'<section class="slide', html))
    n = iter(range(1, total + 1))
    def hd(_):
        i = next(n)
        return ('<div class="hd"><span class="brand"><span class="mark"><i></i><i></i></span>'
                f'Flowout <span class="sep">/ Team 2</span></span>'
                f'<span class="pg"><b>{i:02d}</b> / {total:02d}</span></div>')
    html = re.sub(r"\{\{hd\}\}", hd, html)
    html = re.sub(r"\{\{i:(\w+)\}\}", icon, html)
    out = SRC / "build" / f"{name}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html.replace('href="deck.css"', 'href="../deck.css"').replace('src="img/', 'src="../img/'))
    pdf = ROOT / DECKS[name]
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=10000", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    print(f"{pdf.name}: {total} strani")

if __name__ == "__main__":
    import sys
    for d in (sys.argv[1:] or DECKS):
        build(d)
