# Avant Gay — a living archive

A community archive of the Avant Gay scene on Solana: the artists, collections, memes, feuds, forks, and lore — kept as an interlinked knowledge graph rather than a single narrative.

**Live site:** https://sonoflasg.github.io/avant-gay-archive/

Culture is a living organism. No single article can capture a scene; this archive holds many perspectives side by side, linked the way the culture actually connects. It started as one person's Obsidian vault, but ownership of the record belongs to the scene.

## How it works

- Every entry is a plain markdown note in this repo (this repo *is* an Obsidian vault — open it in Obsidian and you get the full graph locally).
- Notes link to each other with `[[wikilinks]]`. Entries follow this shape:

  ```
  Source: https://x.com/whoever/status/123
  Author: [[Their Name]]
  Date: 30/08/2025

  Summary or account of the thing, with [[links]] to related entries.
  ```

- On every push to `main`, GitHub Actions runs `scripts/build.py`, which turns the vault into the interactive graph site and deploys it to GitHub Pages.

## Contributing

Everyone's welcome — you don't need to know git. See [CONTRIBUTING.md](CONTRIBUTING.md), or jump straight in:

- **Add context, links, or a correction to an entry:** [open a contribution](../../issues/new?template=contribute.yml) (or click "Add context ✚" on any entry on the site)
- **Propose a missing entry:** [suggest a new entry](../../issues/new?template=new-entry.yml)
- **Comfortable with markdown?** Fork, add or edit a note, open a pull request.

Accepted contributions are credited in the entry. Disputed accounts aren't merged into one "truth" — they stand side by side, attributed.

## Building locally

```
python3 scripts/build.py
open site/index.html
```

No dependencies beyond Python 3.

## License

[CC BY-SA 4.0](LICENSE.md) — share and adapt freely, credit the archive, keep it open.
