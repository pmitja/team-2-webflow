---
name: webflow-components-guide
description: Zgenerira vodič po komponentah Webflow projekta za stranko — en samostojen HTML (COMPONENTS-GUIDE.html), ki ga stranka odpre, ko gradi nove sekcije. Za vsako komponento: predogled (screenshot z objavljene strani), kdaj jo uporabiti in kdaj ne, lastnosti (props), variante, strani, kjer je uporabljena, in nasveti. Bere prek Webflow MCP, ničesar ne spreminja. Triggers: "components guide", "vodič po komponentah", "component use case guide", "navodila za komponente za stranko", "handoff komponent".
---

# Webflow components guide

Cilj: stranka (urednik ali njihov developer) odpre en HTML in v minuti ve, **katero komponento vzeti za kaj** in **kako jo nastaviti**, ne da bi spraševala nas ali odklapljala komponente.

Skill ima tri dele v tej mapi:
- `shoot.mjs` — posname komponente z objavljene strani (Node 22+, Chrome, brez paketov).
- `build_guide.py` — iz `guide.json` zgradi HTML (samo standardna knjižnica). Slike vgradi, izhod je ena datoteka.
- ta navodila.

**HTML ne piši na roke.** Vedno pripravi `guide.json` in poženi `build_guide.py`, da je vodič pri vseh strankah enak.

## Pravilo #1: samo branje

V Webflowu ničesar ne spreminjaj. Ne kliči `create_*`, `update_*`, `rename_*`, `remove_*`, `delete_*`, `publish_*`, `unlink_*` ali `insert_*`.

## Vhod

- **Site** (prek Webflow MCP). Če jih je več, vprašaj, katerega.
- **Javni URL** za screenshote: produkcija ali staging **brez gesla**. Headless Chrome se ne more prijaviti. Če je stran pod geslom, vodič naredi brez predogledov in to povej.
- **Jezik vodiča:** privzeto angleščina (`en`). Slovenščina je vgrajena (`sl`). Za druge jezike dodaj `labels` v JSON (glej spodaj). Če iz pogovora ni jasno, kateri jezik govori stranka, vprašaj.

## Postopek

### 1. Podatki iz Webflowa

1. `webflow_guide_tool` enkrat na začetku. Uporabljaj isti `agent_id` / `session_id`. Točna imena akcij preveri tam.
2. `data_sites_tool` → site, domena (za URL-je strani).
3. `data_pages_tool` → strani (slug, naslov, draft). Draft in utility strani (404, password, style guide) izpusti.
4. `data_component_tool` → `get_all_components` z `options: { includeInstanceCount: true, includeProps: true, includeVariants: true }`. Zabeleži ime, group (folder), opis, instance, prope (ime, tip, privzeta vrednost) in variante.
5. **Izberi komponente za vodič:**
   - Komponente z 0 instancami izpusti in jih naštej v chatu.
   - Interne komponente (ime začne z `_`, group `Internal`, `Utility`, `Dev` ali podobno) izpusti.
   - Navbar, footer in druge globalne komponente daj v skupino "Global". Pri njih napiši, da so že na vsaki strani in jih ni treba dodajati.
   - Če je komponent več kot 40, vprašaj, ali naj vključiš vse ali samo tiste, ki jih stranka dejansko uporablja pri gradnji sekcij.
6. **Kje je uporabljena in selektor za screenshot:** za vsako komponento poišči strani z instancami (element tool na straneh, glej guide). Iz root elementa komponente vzemi **prvi class** kot CSS selektor (npr. `.cta_component`). Če je na isti strani več instanc, zapomni si zaporedno številko.
7. **Brand:** iz variabel (`data_variable_tool`) vzemi primarno barvo, barvo teksta in fonta za naslove in besedilo. Če ni jasne primarne barve, vzemi barvo glavnega gumba.
8. **Recept za sekcijo:** če v delovni mapi obstaja `WEBFLOW-PROJECT.md` (iz `webflow-onboarding`), vzemi drevo iz "Kako zgraditi novo sekcijo". Sicer ga ugotovi iz domače strani (npr. `section_[ime] › padding-global › container-large › padding-section-large`). Če projekt nima jasne strukture, polje izpusti.

### 2. Screenshoti

1. V delovni mapi ustvari `components-guide/` in v njej `shots.json`:
   ```json
   [{ "id": "cta-banner", "url": "https://site.com/pricing", "selector": ".cta_component", "index": 0, "pad": 24 }]
   ```
   Za vsako komponento vzemi stran, kjer je najbolje vidna (običajno prva vsebinska stran, ne domača, če je tam v posebni postavitvi).
2. Poženi: `node ~/.claude/skills/webflow-components-guide/shoot.mjs components-guide/shots.json components-guide/img`
3. Skripta izpiše rezultat za vsak posnetek. Pri `ok: false` poskusi drug selektor ali drugo stran. Če tudi to ne gre, pusti komponento brez slike, vodič pokaže link na stran.
4. **Z Read preglej vsaj 3 posnetke** in vse, ki so sumljivo majhni ali veliki. Preveri, da posnetek kaže pravo komponento in da ni prazen, prekrit s cookie bannerjem ali odrezan. `cut: true` pomeni, da je bila komponenta višja od 1800 px in je odrezana. Za sekcije je to v redu.

### 3. Vsebina

Za vsako komponento napiši (v jeziku vodiča):

- `description` — 1–2 stavka: kaj je in kje se pojavi. Konkretno, brez marketinga.
- `use_when` — 2–4 konkretne situacije ("Primary call to action at the end of a page").
- `avoid_when` — 1–3 situacije, kjer je boljša druga komponenta. Če obstaja, jo poimenuj ("Use **Button Secondary** next to a primary button").
- `props[].description` — kaj lastnost spremeni, v jeziku urednika ("Text on the button", ne "String prop for label").
- `variants[].description` — kdaj vzeti katero varianto.
- `tips` — 0–3 nasveti, samo če so koristni (dolžina teksta, razmerje slike, kaj se zgodi, če je polje prazno).

**Piši samo to, kar vidiš** v imenu, propih, variantah, screenshotu in na straneh, kjer je komponenta uporabljena. Ne izmišljuj funkcij. Kjer namen ni jasen, napiši nevtralen opis in komponento dodaj na seznam "Za pregled" v chatu.

### 4. guide.json in gradnja

Zapiši `components-guide/guide.json`:

```json
{
  "title": "Component guide",
  "intro": "How to build new sections on example.com with the components that already exist.",
  "site": {
    "name": "Example", "url": "https://example.com", "language": "en", "generated": "6 Nov 2026",
    "brand": { "primary": "#9966FF", "text": "#092540", "font_heading": "Inter", "font_body": "Inter" },
    "google_fonts": ["Inter:wght@400;500;600;700"]
  },
  "how_to": null,
  "section_recipe": {
    "tree": ["section_[name]", "padding-global", "container-large", "padding-section-large", "[component]"],
    "note": "Every new section uses this structure, so spacing and width stay consistent."
  },
  "groups": [
    { "name": "Buttons", "description": "", "components": [
      { "name": "Button", "description": "…", "instances": 48, "image": "img/button.png",
        "use_when": ["…"], "avoid_when": ["…"],
        "props": [{ "name": "Text", "type": "Text", "description": "…", "default": "Get started" }],
        "variants": [{ "name": "Primary", "description": "…" }],
        "used_on": [{ "page": "Home", "url": "https://example.com/" }],
        "tips": ["…"] }
    ]}
  ],
  "footer": "Prepared by Flowout · Questions: your project lead.",
  "labels": {}
}
```

- `how_to: null` uporabi privzete 4 korake (dodaj iz panela, urejaj prek lastnosti, izberi varianto, ne odklopi). Lastne korake daj kot seznam `{title, text}`.
- `google_fonts` samo za fonte z Google Fonts. Za custom fonte ga izpusti, vodič uporabi Inter kot rezervo.
- `labels` prepiše oznake vmesnika, npr. za nemščino: `{"title": "Komponenten-Leitfaden", "use": "Verwenden für", …}`. Ključe najdeš v `LABELS` v `build_guide.py`.
- V tekstih lahko uporabiš `` `code` `` in `**bold**`.
- Skupine razvrsti po tem, kako stranka gradi stran: Global → Sections / Hero → Content → Cards → Buttons and links → Forms.

Zgradi: `python3 ~/.claude/skills/webflow-components-guide/build_guide.py components-guide/guide.json components-guide/COMPONENTS-GUIDE.html`

### 5. Preveri

Odpri `COMPONENTS-GUIDE.html` v vgrajenem brskalniku. Posnemi vrh in eno komponento, preizkusi iskanje in preveri še mobilno širino (`resize_window` mobile, nato nazaj na desktop). Popravi JSON in zgradi znova, če je kaj narobe.

## Izhod v chatu

Kratko, v slovenščini:
- pot do `components-guide/COMPONENTS-GUIDE.html` in velikost datoteke,
- število komponent v vodiču in skupin,
- izpuščene komponente (0 instanc, interne) in zakaj,
- komponente brez predogleda in zakaj,
- **Za pregled:** komponente, pri katerih namen ni bil jasen, ali opisi, ki jih mora developer potrditi.

Na koncu dodaj: vodič naj pred pošiljanjem stranki pregleda developer na projektu.
