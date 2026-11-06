---
name: pre-qa-check
description: Hiter vizualni in copy pregled spletne strani glede na Figma export pred predajo v QA. Uporabi, ko uporabnik prilepi URL strani in sliko desktop dizajna (opcijsko še mobile) ter želi preveriti, ali stran izgleda kot dizajn in ali se besedila ujemajo. Triggers: "pre-QA", "vizualni check", "copy check", "primerjaj z dizajnom".
---

# Pre-QA vizualni in copy check

Hiter pregled, preden gre stran v QA. Cilj je najti stvari, ki so **očitno narobe**, ne pixel-perfect primerjava.

## Vhod

- **URL** strani (obvezno)
- **Desktop export** iz Figme (obvezno)
- **Mobile export** iz Figme (opcijsko)

Če URL ali desktop slika manjka, vprašaj zanju in počakaj.

## Postopek

1. Preberi priložene Figma slike.
2. Odpri URL v brskalniku (privzeto vgrajeni browser `mcp__Claude_Browser__*`).
3. **Desktop:** nastavi širino na približno širino Figma exporta (običajno 1440px). Posnemi stran od vrha do dna (scroll + screenshot po sekcijah) in primerjaj z dizajnom sekcijo za sekcijo.
4. **Copy:** z `get_page_text` preberi besedilo strani in ga primerjaj z besedilom na Figma sliki.
5. **Mobile** (samo če je priložen mobile export): nastavi viewport na `mobile` (375px), ponovno naloži stran, posnemi in primerjaj. Na koncu vrni viewport na `desktop`.

## Kaj iskati

**Vizualno** — samo stvari, ki so vidno mimo:
- manjkajoča ali odvečna sekcija / element
- napačen vrstni red sekcij ali elementov
- popolnoma drugačna postavitev (npr. 2 stolpca namesto 3, slika na napačni strani)
- napačna ali manjkajoča slika / ikona
- očitno napačna barva (ozadje, gumb, tekst)
- očitno napačen font ali velikost naslova
- precej prevelik / premajhen razmik, ki poruši vtis
- zlomljen layout: prekrivanje, overflow, horizontalni scroll, odrezan tekst

**Copy:**
- tipkarske napake, manjkajoče ali odvečne besede
- besedilo, ki se razlikuje od dizajna
- placeholder tekst (Lorem ipsum, "Heading", "Button text")
- napačna oznaka gumba ali linka
- velike/male začetnice drugače kot v dizajnu

## Česa NE prijavljati

- razlike nekaj pikslov v razmikih ali poravnavi
- rahle razlike v renderiranju fontov ali odtenkih barv
- interakcije, animacije, hover stanja, funkcionalnost, performance, SEO, dostopnost
- vsebino, ki je očitno dinamična (datumi, CMS seznami), razen če je prazna ali zlomljena

Ko nisi prepričan, ali je razlika dovolj velika: če je QA tester ne bi opazil v 5 sekundah, je ne prijavi.

## Izhod

Odgovori v slovenščini, točno v tej obliki. Vsaka točka pove **kje** (sekcija), **kaj je zdaj** in **kaj bi moralo biti**. Če je samo na mobile ali samo na desktop, to označi z `[mobile]` / `[desktop]`.

```
## Vizualni popravki
- **Hero** — gumb je moder, v dizajnu je črn.
- **Features** [mobile] — kartice so v 2 stolpcih, v dizajnu 1 stolpec.

## Copy popravki
- **Hero naslov** — "Zgradimo prihodnost skupaj" → v dizajnu "Gradimo prihodnost skupaj".
- **Footer** — manjka vrstica "Vse pravice pridržane".
```

Če v sekciji ni napak, napiši `Brez popravkov.` Ne dodajaj povzetkov, ocen ali predlogov izven teh dveh sekcij.
