---
name: webflow-onboarding
description: Read-only pregled obstoječega Webflow projekta prek Webflow MCP — komponente, globalne variable, utility classi in glavni layout classi (section, container, padding, max-width, tipografija). Ustvari cheat sheet, da developer, ki je nov na projektu, ne podvaja že obstoječih zadev. Uporabi, ko uporabnik pride na nov/tuj Webflow projekt ali vpraša, kaj že obstaja. Triggers: "onboarding", "kaj že obstaja v webflowu", "preglej webflow projekt", "katere classe uporablja projekt", "design system audit".
---

# Webflow onboarding

Cilj: v nekaj minutah dobiti sliko, **kaj projekt že ima**, da novih classov, variabel in komponent ne dodajamo na pamet. Rezultat je cheat sheet + kratek povzetek v chatu.

## Pravilo #1: samo branje

Ta skill **ničesar ne spreminja**. Ne kliči `create_*`, `update_*`, `rename_*`, `remove_*`, `delete_*`, `unregister_*`, `publish_*`, `transform_*`, `unlink_*` ali `insert_*`. Če med pregledom opaziš kaj za popravit (podvojen class, nepovezana barva), to samo zapiši v poročilo.

## Predpogoji

- Webflow MCP (2.0) mora biti povezan. Bridge app ni potreben. Če klic vrne napako dostopa ali avtorizacije, to povej uporabniku in počakaj.
- Na začetku enkrat pokliči `webflow_guide_tool` (zahteva MCP serverja). Uporabljaj isti `agent_id` in `session_id` skozi celoten pregled.

## Postopek

### 1. Site in stran

1. `data_sites_tool` → `list_sites`. Če je več sitov in uporabnik ni povedal katerega, ga vprašaj.
2. `data_pages_tool` → `list_pages`. Zapomni si `pageId` domače strani (slug prazen ali `index`) — ta tooli ga zahtevajo kot kontekst.

### 2. Globalne variable

1. `data_variable_tool` → `get_variable_collections` (`query: "all"`), da dobiš kolekcije in njihove mode (npr. Light/Dark, breakpoint mode).
2. Za vsako kolekcijo `get_variables` z `include_all_modes: true`.
3. Razvrsti po tipu (Color, Size, Number, Percentage, FontFamily) in po namenu, ki ga razbereš iz imen (barve, spacing, radius, font size, container width ...). Zabeleži, katere variable se referencirajo med sabo (alias na drugo variablo), ker to pokaže "primitive → semantic" strukturo.

### 3. Komponente

1. `data_component_tool` → `get_all_components` z `options: { includeInstanceCount: true, includeProps: true, includeVariants: true }`.
2. Za vsako zabeleži: ime, group (folder), opis, število instanc, prope (ime + tip), variante.
3. Označi komponente z 0 instancami (verjetno neuporabljene ali library komponente, ki še niso postavljene — MCP tega ne loči zanesljivo, zato jih označi kot "0 instanc", ne kot "neuporabljene").

### 4. Classi — celoten seznam

`data_style_tool` → `get_styles` z `query: "all"` in **brez** propertyjev (`include_properties: false`). To da imena vseh classov in combo classov brez ogromnega izpisa.

Iz imen ugotovi **naming sistem**:

| Znaki v imenih | Sistem |
|---|---|
| `padding-global`, `container-large`, `padding-section-medium`, `section_`, `_component`, `heading-style-h1`, `text-size-`, `max-width-`, `spacer-` | Client-First (Finsweet) |
| `u-` prefiks, `u-container`, `u-section`, `g_` / `c_` | Lumos / sorodni utility sistemi |
| `is-`, `has-` kot combo classi | modifier combo classi (pogosto skupaj z zgornjima) |
| nič od tega | lasten sistem — opiši vzorec, ki ga vidiš |

### 5. Glavni layout in utility classi — z vrednostmi

Z `query_styles` (več queryjev v enem klicu, vsak z `include_properties: true`) poberi dejanske vrednosti za ključne skupine. Prilagodi ključne besede sistemu iz koraka 4:

- **Section / page wrapper:** `section`, `page-wrapper`, `main-wrapper`
- **Container:** `container`, `max-width`, `wrapper`
- **Padding / spacing:** `padding`, `spacer`, `margin`, `gap`
- **Tipografija:** `heading`, `text-size`, `text-style`, `text-weight`, `text-color`, `text-align`
- **Gumbi in linki:** `button`, `link`
- **Ostali utility:** `hide`, `display`, `layer`, `overflow`, `pointer`, `aspect`, `z-index`, `background-color`

Za layout skupine (section, container, padding, max-width, heading) dodaj `include_breakpoints: ["main", "medium", "small", "tiny"]`, ker so tam responsive spremembe ključne. Za ostale zadostuje `main`.

Za vsak class zabeleži: ime, ključne propertyje, ali je vrednost **povezana na variablo** ali hardcoded.

Če sistem ni prepoznaven, poišči layout classe še po propertyjih: `properties: [{name: "max-width"}]`, `[{name: "padding-left"}]`, `[{name: "padding-top"}]`.

### 6. Kako je stran dejansko sestavljena

MCP ne vrne, kolikokrat je posamezen class uporabljen. Zato preveri strukturo na realni strani: preberi drevo elementov domače strani (in še ene vsebinske strani, če obstaja) z element toolom (`data_element_tool` / `element_snapshot_tool` — glej `webflow_guide_tool` za točne akcije) in zapiši tipično gnezdenje, npr.:

```
section_hero
└─ padding-global
   └─ container-large
      └─ padding-section-large
         └─ hero_component
```

To je najpomembnejši del cheat sheeta — pove, kako se gradi nova sekcija.

### 7. Opažanja (samo zapiši, ne popravljaj)

- podvojeni ali skoraj podvojeni classi (`container-large` in `container-lg`, dva classa z istimi propertyji)
- barve / velikosti v classih, ki so hardcoded, čeprav obstaja ustrezna variabla
- variable, ki imajo isto vrednost pod različnimi imeni
- komponente z 0 instancami
- classi, ki ne sledijo naming sistemu projekta

## Izhod

### Datoteka

Zapiši `WEBFLOW-PROJECT.md` v trenutni delovni direktorij (če že obstaja, jo najprej preberi in posodobi namesto da prepišeš na slepo). Struktura:

```markdown
# <Ime sita> — Webflow cheat sheet
Pregledano: <datum> · Site ID: <id> · Naming sistem: <sistem>

## Kako zgraditi novo sekcijo
<drevo iz koraka 6 + 1-2 stavka>

## Preden dodaš ... uporabi raje
| Potrebuješ | Obstaja |
|---|---|
| zunanji padding sekcije | `padding-global` (5% / 1.25rem mobile) |
| max širino vsebine | `container-large` (80rem), `container-medium` (64rem) ... |
| vertikalni razmik sekcije | `padding-section-small/medium/large` |
| primarno barvo | variabla `Brand / Primary` |
| gumb | komponenta `Button` (varianti: primary, secondary) |
...

## Variable
<po kolekcijah in tipih; ime → vrednost (po modih)>

## Komponente
<tabela: ime · group · instance · propi · variante>

## Layout classi
<section / container / padding / max-width z vrednostmi po breakpointih>

## Utility classi
<po skupinah, samo imena + bistven property>

## Tipografija
<heading-style-*, text-size-* ... z vrednostmi>

## Opažanja
<seznam iz koraka 7>
```

Tabela "Preden dodaš ... uporabi raje" je jedro — naj bo konkretna in kratka.

### Chat

Kratek povzetek (5-10 vrstic): naming sistem, kako zgraditi sekcijo, koliko je komponent / variabel / classov, najpomembnejša opažanja in pot do `WEBFLOW-PROJECT.md`.

## Med nadaljnjim delom

Ko v isti seji kasneje dodajaš classe, variable ali komponente, najprej preveri `WEBFLOW-PROJECT.md` (ali `query_styles` / `query_variables` / `query_components` po imenu), ali nekaj podobnega že obstaja. Če obstaja, uporabi obstoječe in to omeni.
