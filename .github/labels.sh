#!/usr/bin/env bash
# Create or update the triage labels used by the issue forms and REVIEW.md.
# Safe to re-run. Needs: gh auth with write access to the repo.
set -euo pipefail
R="${1:-sonoflasg/avant-gay-archive}"
mk() { gh label create "$1" --repo "$R" --color "$2" --description "$3" --force; }
mk submission       "ff4fa3" "Contribution from the issue forms or a PR, awaiting triage"
mk new-entry        "7bdcff" "Proposes a new archive entry"
mk addition         "6ee7a0" "Adds sourced material to an existing entry"
mk correction       "f4845f" "Corrects a factual error in an existing entry, with a source"
mk perspective      "b39dff" "Contests a claim; adds an attributed account side by side"
mk needs-sources    "e6c07b" "Claims still lack public sources"
mk agent-assisted   "57565f" "Prepared with an LLM or agent (disclosed)"
mk ready-for-review "0e8a16" "Triaged and checked; awaiting the archive owner's decision"
