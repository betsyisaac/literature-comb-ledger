# Literature Comb — public ledger

The rendered, consolidated view is **[index.md](index.md)**.
The machine-readable feed is **[leads.csv](leads.csv)**.

## What this is

[Literature Comb](https://github.com/bambamramfan/literature-comb) is a
distributed Swanson-style literature-based-discovery project: volunteers spend
leftover LLM budget combing old and cross-field literature against modern
problems, looking for **"undiscovered public knowledge"** — pairs of
literatures that each hold half an answer and have never cited each other.
Survivors (leads that pass adversarial verification) are recorded in
per-contributor ledgers in that repo.

This repo is a **derived, curated public view** on top of those ledgers —
same relationship a Krakovna-style public tracker has to the underlying
incident reports it's built from. The per-contributor repo is contributor
hygiene; this one is public discoverability, including by AI agents that
researchers point at it directly (`leads.csv` is the stable, scrapable feed).

Maintained by Betsy Isaacson. The per-contributor ledgers are maintained by
Tony (bambamramfan) and other contributors; this repo doesn't replace them,
it curates a public-facing subset.

## How it works

- `leads/*.md` — one file per lead. Each has a short YAML-ish frontmatter
  block (flat key: value pairs, one line each — see `scripts/build.py`'s
  docstring for the exact schema) and a free-form body holding the full
  verifier notes.
- `scripts/build.py` reads every file in `leads/` and regenerates
  `index.md` (human-readable) and `leads.csv` (machine-readable). **Never
  hand-edit `index.md` or `leads.csv` directly** — edit the source file in
  `leads/` instead; both derived files get silently overwritten on the next
  build.
- `.github/workflows/build.yml` runs `scripts/build.py` automatically on
  every push to `main` that touches `leads/` or the build script, so the
  generated files never go stale.

Adding a lead is: write one new file in `leads/`, open a pull request,
Betsy reviews and merges. That's the same human-glance-before-publish gate
the underlying project requires for any AI-generated content going outward.

## The promotion routine

New leads mostly arrive here via an automated daily routine, not by hand.
Once a day it reads every contributor's `ledger/*/surviving.md` in the
parent project, decides which newly-seen entries are worth promoting
(real sources, real verification, a concrete next check — see
`promotion-state.json` for exactly what's been considered and why), and
opens a PR here with any it selects. "Nothing new" is a normal, correctly
logged outcome, not a failure — see `PROMOTION-LOG.md` for the run-by-run
record. Every PR it opens still needs Betsy's merge before anything goes
live; the routine proposes, it doesn't publish on its own.

`promotion-state.json` is the dedup/decision ledger (don't hand-edit —
it's written by the routine) and `PROMOTION-LOG.md` is the human-readable
run log. Scoped to `surviving.md` only for now; `rejected.md` mirroring
is a reasonable future extension, not yet built.

## Status values

- `open` — survived verification, not yet independently resolved.
- `resolved` — someone ran the cheap check; outcome known.
- `rejected` — **stays in the repo, status flipped, never deleted.** The
  rejected leads are as valuable as the survivors: they stop the pool
  re-walking dead ground and keep the real hit rate visible.
- `example` — placeholder/demo content, not a real lead. See `leads/EXAMPLE.md`.

## Rules this repo inherits from the parent project

- A surviving lead is a **hypothesis worth one cheap check**, never a finding.
- Never medical, clinical, legal, or financial advice.
- Never cite a source nobody fetched.
- Disclose method: "found by an automated literature sweep; not refereed."
- "Nothing survived" is a correct, complete result. Padding the ledger to
  look productive is the one failure mode that makes this worthless.

Full spec: https://github.com/bambamramfan/literature-comb/blob/main/SHARED-ROUTINE.md
