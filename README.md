# Avant Gay — a living archive

A community archive of the Avant Gay scene on Solana: the artists, collections, memes, feuds, forks, and lore — kept as an interlinked knowledge graph rather than a single narrative.

**Live site:** https://sonoflasg.github.io/avant-gay-archive/

Culture is a living organism. No single article can capture a scene; this archive holds many perspectives side by side, linked the way the culture actually connects. It started as one person's Obsidian vault, but ownership of the record belongs to the scene.

## How it works

- Every entry is a plain markdown note in this repo (this repo *is* an Obsidian vault — open it in Obsidian and you get the full graph locally).
- Notes link to each other with `[[wikilinks]]`. Entries follow this shape:

  ```
  Source: https://x.com/whoever/status/123
  Author: Their Name
  Date: 30/08/2025

  ---

  Summary or account of the thing, with [[links]] to related entries.

  Sources:
  - [@whoever on X, 30 Aug 2025 9:15pm AEST](https://x.com/whoever/status/123)
  ```

- On every push to `main`, GitHub Actions runs `scripts/build.py`, which turns the vault into the interactive graph site and deploys it to GitHub Pages.

## Contributing

Everyone's welcome, and you don't need to know git. AI agents are welcome too: point yours at [AGENTS.md](AGENTS.md) (`https://raw.githubusercontent.com/sonoflasg/avant-gay-archive/main/AGENTS.md`). Short version: [CONTRIBUTING.md](CONTRIBUTING.md).

- **Add to an entry:** [Addition](../../issues/new?template=contribute.yml) (or "Add context ✚" on any entry on the site)
- **Fix a factual error:** [Correction](../../issues/new?template=correction.yml), with a source that shows the error
- **Dispute a claim:** [Perspective](../../issues/new?template=contest.yml). Your account is added beside the existing one; nothing is deleted.
- **Propose a missing entry:** [New entry](../../issues/new?template=new-entry.yml)
- **Comfortable with markdown?** Fork the repo, follow AGENTS.md, run `python3 scripts/validate.py`, and open a pull request.

Accepted contributions are credited in the entry. Disputed accounts aren't merged into one "truth" — they stand side by side, attributed.

## Building locally

```
python3 scripts/build.py
open site/index.html
```

No dependencies beyond Python 3. Check your changes with `python3 scripts/validate.py` (see AGENTS.md).

## License

[CC BY-SA 4.0](LICENSE.md) — share and adapt freely, credit the archive, keep it open.
