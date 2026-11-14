# Reviewing contributions (maintainers)

How submissions are triaged. Contributors follow [AGENTS.md](AGENTS.md). This page is for the people who review.

## Cadence

Triage runs periodically (proposed: weekly, or when the owner asks). One pass covers everything with the `submission` label, plus every open PR.

```
gh issue list --repo sonoflasg/avant-gay-archive --label submission --state open
gh pr list    --repo sonoflasg/avant-gay-archive --state open
```

## What gets checked

For each item:
1. **Type is right.** New entry, addition, correction or perspective. A "correction" that is really a disagreement is relabelled `perspective`.
2. **Validator.** On PRs, read the "Validate contribution" check. No ERRORs are allowed, and every WARN is either fixed or explained. For issues, run `python3 scripts/validate.py --files <draft>.md` on the converted draft.
3. **Sources open and say what is claimed.** Spot-check every new claim, and every X post (handle, date, AEDT/AEST time). Unsourced claims are cut, or the entry is marked `Status: needs-sources`.
4. **Existing material is kept.** Additions don't reword. Corrections carry a `### Revisions` note with the source. Contests add a `### Perspectives` section and keep the original claim.
5. **Safety.** No private chats without consent, no wallet addresses, keys or seed phrases, no real names of pseudonymous people, no unverified allegations, no shilling. If any of these appear, stop: don't quote the content anywhere, and flag the item to the owner.
6. **Disclosure and credit.** Add `agent-assisted` if an LLM was used. Record the credit handle.

Items that pass get `ready-for-review`. Items with fixable problems get a short, neutral comment asking for changes. Comments are posted only once the owner has approved posting them.

## Summary for the owner

Each pass ends with one short summary for Tolu:
- counts by type and by status (ready / needs changes / reject)
- for each ready item: the entry, the change in one line, its main source, the contributor handle, whether it was agent-assisted, and any warnings
- anything contested or sensitive, flagged separately, with the competing accounts named
- proposed actions (merge, request changes, close, convert an issue to a PR)

## Merging

**Nothing merges without Tolu's explicit go, item by item.** Reviewers and agents never push to `main`, merge, or change repo settings. Accepted issues are converted on a branch (`contrib/<issue-number>-<slug>`) as a PR that credits the submitter and links the issue (`Closes #n`). They then wait for the same go-ahead. After a merge, the deploy workflow rebuilds the site.
