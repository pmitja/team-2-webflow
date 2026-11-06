# Flowout Team 2 — Webflow skilli za Claude Code

Skilli, ki jih Team 2 uporablja pri Webflow projektih, in predstavitve zanje.

| Skill | Kaj naredi | Ukaz |
|---|---|---|
| [pre-qa-check](skills/pre-qa-check/SKILL.md) | Vizualni in copy pregled strani glede na Figma dizajn pred QA | `/pre-qa-check <url>` + Figma export |
| [webflow-onboarding](skills/webflow-onboarding/SKILL.md) | Cheat sheet obstoječih classov, variabel in komponent na novem projektu | `/webflow-onboarding` |
| [webflow-launch-audit](skills/webflow-launch-audit/SKILL.md) | Dostopnost, linki, SEO in slike pred objavo | `/webflow-launch-audit <url>` |
| [webflow-components-guide](skills/webflow-components-guide/SKILL.md) | HTML vodič po komponentah za stranko | `/webflow-components-guide` |

Vsi skilli v Webflowu samo berejo in ničesar ne spreminjajo.

## Namestitev

Kloniraj repo in poveži skille v `~/.claude/skills/`, da se ob `git pull` samodejno posodobijo:

```bash
git clone https://github.com/pmitja/team-2-webflow.git ~/Projects/team-2-webflow
```

```bash
mkdir -p ~/.claude/skills && for s in ~/Projects/team-2-webflow/skills/*/; do ln -sfn "$s" ~/.claude/skills/$(basename "$s"); done
```

Ponovno zaženi Claude Code. Skilli so na voljo kot `/ime-skilla`.

## Kaj rabiš

- **Claude Code** (CLI ali desktop app)
- **Webflow MCP 2.0** za onboarding, launch audit in components guide
- **Google Chrome** in **Node 22+** za screenshote v components guide
- **Figma MCP** (opcijsko) — ko je prijavljen, bo pre-qa-check lahko bral dizajn direktno iz Figme

## Predstavitve

PDF-ji so v [predstavitve/](predstavitve). Izvorni HTML je v `predstavitve/src/`. Po spremembi jih ponovno zgradiš z:

```bash
cd predstavitve && python3 src/build.py
```

Za gradnjo rabiš Google Chrome in internet (pisave).

## Status

| Skill | Status |
|---|---|
| pre-qa-check | Preizkušen na eni strani |
| webflow-onboarding | Pripravljen, še ni pognan na projektu |
| webflow-launch-audit | Pripravljen, še ni pognan na projektu |
| webflow-components-guide | Screenshoti in HTML preizkušeni, celoten tok še ne |
