# Contributing to the archive

This archive belongs to the scene. Whether you were there for the fracture or arrived last week, your material is welcome. There are two paths, depending on your comfort level.

## Path 1 — no git required

Open an issue and a maintainer will fold your material into the archive:

- [Add context / material / a correction to an existing entry](../../issues/new?template=contribute.yml)
- [Propose a new entry](../../issues/new?template=new-entry.yml)

You'll be credited however you ask to be (handle or anonymous).

## Path 2 — pull requests

The repo is an Obsidian vault: every entry is a markdown file, folders indicate type (`Artists/`, `Collections/`, `ArticlesNthreads/`, etc.).

1. Fork the repo, add or edit a note.
2. Follow the entry shape:

   ```
   Source: <link to the tweet/thread/article/mint>
   Author: [[Who made or said it]]
   Date: DD/MM/YYYY
   Status: needs-sources   # optional

   The account itself, linking related entries with [[wikilinks]].
   ```

`Status: needs-sources` flags a draft that is already in the vault but still lacks primary sources (for example early Grok-generated notes). Do not delete those notes; mark them so they can be sourced later. Compiled entries should name their sources in the body (use a normal markdown URL in a Sources section for bibliographic citations; only `[[wikilink]]` a source when the note actually discusses that work or person). Credit the compiler in the Author line as plain text (usually `SonOfLasG`) — the Author/Source/Date/Status fields are metadata, not graph edges.

3. Open a pull request. The site rebuilds automatically when it's merged.

Tips: link generously — the graph is the point. New entries with zero `[[links]]` float disconnected. Check the site's grey "phantom" nodes for entries the archive already wants: they're referenced but unwritten.

## Editorial principles

1. **Sources over vibes.** Claims should link to primary material (tweets, mints, articles) wherever possible.
2. **Perspectives stand side by side.** Contested history doesn't get merged into one account. Competing versions co-exist in the same note (or linked notes), each attributed. The graph can hold disagreement; a single narrative can't.
3. **Attribution always.** Every contribution is credited — in the note's Author/Contributors line and in the git history.
4. **Consent for private material.** DMs and private conversations only go in with the consent of the people in them.
5. **People over beef.** Documenting feuds that shaped the scene: yes. Using the archive to prosecute them: no.

## Maintainers

Maintainers review issues and PRs, and merge accepted material. Active, trusted contributors will be invited as maintainers over time — stewardship is meant to be shared.
