# Contributing to the archive

This archive belongs to the scene. Your material is welcome whether you were there from the start or arrived last week. Using an AI agent is fine: point it at **[AGENTS.md](AGENTS.md)** (raw: `https://raw.githubusercontent.com/sonoflasg/avant-gay-archive/main/AGENTS.md`), which holds the full rules and templates. This page is the short version.

## Four kinds of contribution

1. **New entry:** something missing from the archive.
2. **Addition:** new sourced facts or context for an existing entry. Nothing existing is changed.
3. **Correction:** a plain factual error, fixed with a source that shows the error. It is logged in the entry's `### Revisions` section.
4. **Perspective / contest:** a different account of something. The existing claim is never deleted. Yours is added beside it under `### Perspectives`, attributed (who, when, source).

## Three ways to send it

- **No git:** open the matching [issue form](../../issues/new/choose) (New entry, Addition, Correction, Perspective). A maintainer folds accepted material into the archive.
- **Pull request:** fork the repo, add or edit notes as described in [AGENTS.md](AGENTS.md), run `python3 scripts/validate.py`, and open a PR using the template. A read-only check runs the same validator on every PR.
- **On X:** tag a public post that contains a sourced claim, piece or perspective with `#AvantGayArchive`. The daily sweep queues tagged posts for review. Nothing goes live automatically. The same house rules apply.

Submissions are reviewed in periodic batches ([REVIEW.md](REVIEW.md)). Nothing is merged without the archive owner's approval. Every contribution is credited to the handle you give, or to "anonymous".

## Entry shape

```
Source: <main public URL>
Author: <plain text, e.g. your handle>
Date: DD/MM/YYYY
Status: needs-sources     # optional: needs-sources | contested
X: @handle                # optional: a persona's own confirmed X handle
Role: community           # optional: day-to-day collector, commentator, curator, host

---

The account, linking related entries with [[wikilinks]].

Sources:
- [Author, “Title,” publication, date](https://…)
```

`X:` holds a person's, collective's or platform's own public X handle, and only one a source confirms. The site shows that account's profile picture from a local copy. `Role: community` is an optional tag for people who live the scene day to day (collectors, commentators, curators/documenters, Spaces hosts, meme-makers). It does not move the file or change the node type; it adds a Community filter on the map. The header lines are metadata, not graph edges, so don't put `[[wikilinks]]` in them. `Status: needs-sources` flags a draft that still lacks primary sources. Never delete those notes; source them. Grey "phantom" nodes on the site are entries the archive already wants.

If you have a Community entry and want it changed or removed, say so through the [issue forms](../../issues/new/choose) (Correction or Perspective is fine). The archive will not treat that as a dispute to be argued out in public if you are asking about your own entry.

## Editorial principles

1. **Sources over vibes.** Every claim links to public material. X posts are cited by URL, with the date and time in Melbourne time (AEDT/AEST).
2. **Perspectives stand side by side.** Contested history isn't merged into one account. Each version is attributed.
3. **Attribution always.** Contributors are credited in the entry and in git history. Disclose AI assistance in your PR or issue.
4. **Consent for private material.** DMs and private chats only go in with the consent of the people in them. Never include wallet addresses, keys or seed phrases. Never include real names of pseudonymous people.
5. **People over beef.** Documenting feuds that shaped the scene: yes, through public, attributed statements. Using the archive to prosecute them, or to push allegations or shill: no.

## Maintainers

Maintainers triage issues and PRs ([REVIEW.md](REVIEW.md)). Active, trusted contributors will be invited as maintainers over time. Stewardship is meant to be shared.
