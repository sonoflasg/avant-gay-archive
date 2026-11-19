# Contributing to the Avant Gay archive with an AI agent

**Point your agent here:** `https://raw.githubusercontent.com/sonoflasg/avant-gay-archive/main/AGENTS.md`

This page tells an agent (or a person) exactly how to add to this archive. Read all of it before you write anything. Humans are welcome to follow it too. The short version for people is in [CONTRIBUTING.md](CONTRIBUTING.md).

## 1. What this archive is

A community archive of the Avant Gay scene (Solana and Ethereum NFT art, roughly 2021 onward), kept as an Obsidian vault and published as a graph at https://avantgay.sonoflasg.com/.

- **Many attributed perspectives, not one story.** Every claim belongs to someone: a source, a participant, a critic. Write "X says…", not "it is a fact that…", whenever accounts differ.
- **Disagreement stands side by side.** Never resolve a dispute by picking a winner or deleting a version.
- **Sources over vibes.** Every claim needs a public source. If you can't find one, don't write the claim, or mark the entry `Status: needs-sources`.
- **Neutral, plain, archival prose.** No hype, no ranking of who is "best", no market talk.

## 2. Choose your path

| You want to… | Path | Issue form (no git) | PR type |
|---|---|---|---|
| Add a missing entry | **New entry** | `new-entry.yml` | New entry |
| Add facts or sources to an existing entry | **Addition** | `contribute.yml` | Addition |
| Fix something that is wrong in an existing entry | **Correction** | `correction.yml` | Correction |
| Dispute a claim, or record a different account | **Perspective (contest)** | `contest.yml` | Perspective |
| Suggest a sourced claim from X (no GitHub) | **Hashtag** | Tag a public post with `#AvantGayArchive` | — |

Forms live at `https://github.com/sonoflasg/avant-gay-archive/issues/new/choose`. A pull request is better if you can make one, because it is reviewed exactly as merged. An issue is fine. Maintainers convert accepted issues into entries. A tagged X post is also fine: it is queued for review the same way.

Before you start, search the vault for the name (filenames are case-insensitive; also try spelling variants). If an entry exists, use Addition, Correction or Perspective. Do not create a duplicate.

### 2a. Addition (existing entry)
Add new, sourced material without changing what is already there. Put it in a fitting existing section or a new `### ` section. Add its URLs to the entry's Sources list. Don't reword existing sentences "for style".

### 2b. Correction (existing entry)
For a plain factual error (wrong date, number, name of a work, broken link) where a source shows the error:
1. Change the wrong text.
2. Add, or extend, a `### Revisions` section at the end of the body (before Sources):
   ```
   ### Revisions
   - 14/11/2026 · @yourhandle: Date changed from 2022 to 15/01/2024. The Automat paper registers the mint on 15 Jan 2024: https://automat.art/research/avant-gay/
   ```
3. Cite the source that shows the error. "I remember it differently" is not a correction; it is a perspective (2c).

If the "error" is something people genuinely disagree about, it is not a correction. Use 2c.

### 2c. Perspective / contest (existing entry)
Never delete or overwrite the existing claim. Add an attributed account next to it:
```
### Perspectives

- **According to [source or person], DD/MM/YYYY:** what they say, in neutral words. Source: <url>
- **According to [other source], DD/MM/YYYY:** the competing account. Source: <url>
```
If the original claim had no attribution, keep it and attribute it to the entry's existing source or author. Optionally set `Status: contested`. First-hand accounts are welcome. Say they are first-hand and give the public post or written statement where you made them.

### 2d. New entry
Use the template for its type (section 4). Put the file in the folder for that type. The folder sets the node colour/type on the site.

### 2e. Public X post
Tag a public post that contains a sourced claim, piece or perspective with `#AvantGayArchive`. The maintainer's daily sweep queues tagged posts for review. Nothing goes live automatically. The same house rules apply: public sources only, no DMs or group-chat screenshots, no wallets, no doxxing. Contesting a claim adds your view beside the existing one; it never erases it.

## 3. Required format (every entry)

```
Source: <main public URL for the entry>
Author: <plain-text compiler or author, e.g. your handle>
Date: DD/MM/YYYY
Status: needs-sources        # optional; see below
X: @handle                   # optional; persona entries only, see below
Role: community              # optional; see below

---

Body in plain markdown, linking related entries with [[wikilinks]].

Sources:
- [Author, “Title,” publication, D Mon YYYY](https://…)
- [@handle on X, 14 Nov 2026 10:08am AEDT](https://x.com/handle/status/1234567890)
```

Rules:
- **Header lines are metadata, not graph edges.** Write `Author:` as plain text. Never put `[[wikilinks]]` in `Source/Author/Date/Status`.
- **Date** is `DD/MM/YYYY`: the date of the work or event for articles and threads, or the compile date for compiled entries.
- **X** (optional, for people, artists, collectives, platforms and accounts): the entity's own public X handle, as `X: @handle`. Add it only when a source confirms it is the right account: the Automat paper or another cited source linking the name to the handle, or the account's own profile clearly naming the entity. Never guess. Maintainers capture the profile picture locally (`scripts/pfp_capture.py`, `website/pfp/manifest.json`); don't add image files yourself. Like the other header lines, it is metadata, not a graph edge.
- **Role** (optional): `Role: community` marks a person, artist or account who lives the scene day to day as a collector, commentator, curator/documenter, Spaces host or meme-maker. It is metadata, not a graph edge, and it does not move the file. People who also make work stay in `People/` or `Artists/` and gain the Community filter on the map alongside their existing type. Write about what they did and said publicly, not who they are. A person can ask for a Community entry to be changed or removed through the [issue forms](https://github.com/sonoflasg/avant-gay-archive/issues/new/choose).
- **Status:** omit it for a sourced entry. Use `needs-sources` when claims still lack sources (never delete such entries; source them). Use `contested` when the entry holds unresolved competing accounts.
- **Wikilinks** are graph edges. Link to existing filenames exactly (`[[Galerie Yeche Lange]]`, not `[[Yeche Lange]]`). Use `[[Target|shown text]]` for a different label. A link to a name with no file creates a grey "phantom" node. Only do that on purpose, for something that deserves an entry. Link generously but meaningfully.
- **The site shows plain text.** Use headings, bullet lists, bold and links. Do not use markdown tables (the site doesn't render them).
- **File name = entry title.** Use the name the scene uses, with no slashes. One entry per file.
- **Retitling an entry.** Use `git mv` so the filename matches the new title. Do not leave the old file in place, and do not leave a `[[OldName]]` wikilink (that would create a phantom). Record the change in a `### Revisions` note that cites the old path (`People/OldName.md`) so the validator can treat it as a rename, not a deletion. Keep the old name in the body so search still finds the entry.

### Citation rules
- Cite **public URLs** for every claim: articles, mint/collection pages, exhibition pages, archived pages (web.archive.org is fine).
- **X posts:** use `https://x.com/<handle>/status/<id>` (no `?s=` tracking, no twitter.com), with the handle and the post's date and time in **Melbourne time**, labelled `AEDT` (UTC+11, early Oct to early Apr) or `AEST` (UTC+10). Example: `@Greekdx, 14 Nov 2026 10:08am AEDT`.
- **The Automat "Avant-Gay" paper** (https://automat.art/research/avant-gay/) is a major source. Cite it **once per entry** in Sources, with an anchor if useful. Don't add it as boilerplate wikilinks.
- **Mark inferences.** If you connect two sourced facts yourself, write `*Inference:* …`.
- **Quote sparingly** and attribute quotes. Paraphrase otherwise.
- **Don't invent sources, dates, numbers or URLs.** Agents: open each URL and confirm it says what you claim. Never cite a page you couldn't read. If a figure differs between sources, give both, attributed.

## 4. Templates by type

Fill in only what the sources support. Drop sections you can't source.

**Artist** (`Artists/Name.md`), **Person** (`People/Name.md`): critics, collectors, curators, organisers. Add `Role: community` when the sources show they also live the scene day to day (collector, commentator, curator/documenter, host). Keep the file in its folder; the tag adds a Community filter on the map, it does not change the node type.
```
Source: <their public profile or the main source>
Author: <you>
Date: DD/MM/YYYY
Role: community              # optional

---

Name (X: @handle) is a <role> associated with [[…]].

- **Work / role:** … (source)
- **Collections or exhibitions:** [[…]], [[…]]
- **Writing / interviews:** …

Sources:
- …
```
Use the public handle or artist name. **Never add the legal name of a pseudonymous person** unless they publicly use it themselves in this context.

**Collection** (`Collections/Name.md`)
```
---
*Name* is a <medium / format> by [[Artist]], released <date> on [[Solana]] / [[Ethereum]] (<platform>), <edition size> works.

- **Concept and method:** …
- **Traits / references:** …
- **Reception:** who said what (attributed)
- **Exhibitions:** [[Event]]

Sources:
- …
```

**Event / exhibition** (`Events/Name.md`): venue or platform, dates, artists, curator, and what sources say about it.

**Article / thread** (`ArticlesNthreads/Title.md`): Source = the URL, Author = the writer, Date = the publication date. Body: a neutral summary of the main claims, attributed to the author, with links to the entries it discusses.

**Platform** (`Platforms/Name.md`; VVV-related in `VVV/`): what it is, who runs it (by public names and handles), launch date, releases.

**Concept / lore** (vault root, `Name.md`): definitions and origin accounts side by side, attributed, with first known public uses as dated, linked posts.

## 5. Forbidden

Pull requests containing any of these are closed.
- **Private material:** DMs, group-chat or Discord/Telegram screenshots or quotes, or invite links, unless everyone in the conversation has consented, and the PR says so.
- **Wallet addresses, private keys, seed phrases**, or anything that links a pseudonym to a wallet.
- **Doxxing:** real names, locations, employers or family of pseudonymous people, or "identity reveals" from any site.
- **Unverified allegations** about people (misconduct, scams, crimes). Document feuds that shaped the scene only through public, attributed statements. Never assert them as fact.
- **Buying, selling or shilling:** prices as advice, "floor", "undervalued", mint calls, referral links.
- **Fabrication:** invented quotes, sources or dates, or AI text pasted without checking.
- Deleting entries, or removing someone's attributed account.

## 6. Steps: pull request (preferred)

1. Fork `sonoflasg/avant-gay-archive` and create a branch: `git checkout -b add-<short-name>`.
2. Add or edit files following sections 2–4.
3. Run the checks locally (Python 3 only):
   ```
   python3 scripts/validate.py --base origin/main     # or --base upstream/main in a fork
   python3 scripts/build.py && open site/index.html   # optional: see it on the graph
   ```
   Fix every `ERROR`. Read every `WARN` and fix or explain it in the PR.
4. Commit with a plain message (`Add Haircuts exhibition entry`, `Correct Little Swag World mint date`). Push your branch and open a pull request against `main`. Fill in the template: change type, sources, AI disclosure, credit.
5. A maintainer reviews it in the next periodic triage. Nothing is merged without the archive owner's approval. You may be asked for changes.

## 7. Steps: issue (no git)

Open the matching form at https://github.com/sonoflasg/avant-gay-archive/issues/new/choose. Agents can produce the form contents as text for the human to paste. Include the entry name, the exact text to add or change, every source URL (X posts with AEDT/AEST times), the AI disclosure and how to credit you.

## 8. Steps: public X post (no GitHub)

Post a sourced claim, piece or perspective on X and tag it `#AvantGayArchive`. The daily sweep queues tagged posts for review; nothing is added to the archive until a maintainer accepts it. The forbidden list in section 5 still applies.

## 9. Disclosure and credit

Say whether you used an LLM or agent, which one, and whether a human checked every claim against its source. Agent-assisted work is welcome. Unchecked agent output is not. Credit goes to your handle (or "anonymous") in the PR or issue, in git history, and, for substantial work, in the entry's Revisions or Author line.

## 10. Data & reuse

A machine-readable export of every entry is published with the site:

- JSON: https://avantgay.sonoflasg.com/archive.json
- CSV: https://avantgay.sonoflasg.com/archive.csv

The archive is licensed under [CC BY-SA 4.0](LICENSE.md). If you reuse it, cite the Avant Gay Archive and the entry's own sources.
