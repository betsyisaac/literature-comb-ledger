# Promotion routine log

One entry per run of the daily promotion routine (see `promotion-state.json`
for the underlying dedup state, and the project README for how promotion
works). A run that finds nothing new logs that plainly — it's a correct,
complete result, not a gap.

---

## 2026-10-24 (session dd02cbae)

Waiting on PR #3 (`promote/2026-10-22`) to be merged; skipping today.

---

## 2026-10-23 (session 8eb00a64)

Waiting on PR #3 (`promote/2026-10-22`) to be merged; skipping today.

---

## 2026-10-21 (session 99d17795)

Read 1 contributor ledger (`bambamramfan/surviving.md`). Upstream advanced
from `66575dc` to `581c0a1` (code-only changes: `comb.js`, `generate.js`,
`targets.json`); no ledger entries added, renamed, changed, or vanished.
Comments feed configured, 3 total threads, none new or updated. Nothing
to do; bookkeeping committed to main.

---

## 2026-10-20 (first run; session 3ab640cb)

Read 1 contributor ledger (`bambamramfan/surviving.md`). Found 11 new
entries, none previously fingerprinted.

Promoted 5:

- **LC-0001** — bambamramfan:2026-10-16:erdos-open (prime case of Erdos #634 settled by Beeson arXiv:2607.23453)
- **LC-0002** — bambamramfan:2026-10-16:cauris (azalomycin F macrolide vs C. auris, untested)
- **LC-0003** — bambamramfan:2026-10-19:cauris:pyrrolnitrin (pyrrolnitrin / fludioxonil for topical / surface C. auris)
- **LC-0004** — bambamramfan:2026-10-20:cacao-cadmium (K2SO4 vs KCl in cacao, anion driver of bean Cd)
- **LC-0005** — bambamramfan:2026-10-20:inp-secondary-ice (calcium phosphate / apatite as atmospheric INP)

Skipped 6:

- bambamramfan:2026-10-19:cauris:azasteroid — source entry self-labels "Recorded as weak, not promoted"; 2 of 3 verifiers flagged primary source as undercutting the bridge.
- bambamramfan:2026-10-20:apple-replant-etiology — all three verifiers said the lead's headline framing is false; source labels WEAK, not promoted.
- bambamramfan:2026-10-20:secondary-al-iron — physics error (beta-AlFeSi is not buoyant) caught by all three verifiers; source labels WEAK.
- bambamramfan:2026-10-20:konzo-neurotoxin — scores 4/3/2 below source's own 6 threshold; phenotype mismatch and backwards stoichiometry; source labels WEAK SURVIVOR.
- bambamramfan:2026-10-20:zhf_core_temp_transient_deconvolution — 5/5/4 below threshold; all three verifiers flagged primary_source_undercuts_lead.
- bambamramfan:2026-10-20:lpbf-in-process-distortion-control — the specific novelty claim is false as written (Wu et al. 2019 and PAS 6012:2020 already cover the asserted-missing variable).

Note on fingerprint format: two entries on 2026-10-19 shared target slug
`cauris`, which collides under the documented `<handle>:<date>:<target>`
scheme. Disambiguated by appending a subject keyword
(`:pyrrolnitrin` / `:azasteroid`). Flagging in case the fingerprint spec
needs tightening upstream.

---

## 2026-10-20 (session 68e1329a)

Read 1 contributor ledger (`bambamramfan/surviving.md`). Upstream counts:
0 new, 0 renamed, 1 changed, 0 vanished. Comments: not configured.

Changed:

- **LC-0001** — bambamramfan:2026-10-16:erdos-open. Upstream added a
  dated RETRACTION block to the entry: the proof-claims thread on
  erdosproblems.com (the page our verifier could not reach because of a
  Cloudflare 403) already carried the same prime-case result, submitted
  2026-07-24 by jphme, two days before Beeson's preprint. The problem
  page itself (last edited 2025-12-30) already links Beeson's slides.
  The tracker is NOT stale, nothing is missing, and the draft issue
  must not be posted. The upstream retraction labels this the same
  failure as pilot #1221 — a blocked check is a refutation, not a
  caveat to publish alongside. **LC-0001 flipped from `open` to
  `rejected`** with a dated Update paragraph; lead body preserved.

Noted for next-time rule-tightening: v2 of my own routine already bars
promoting leads whose central-absence claim rests on a blocked page.
LC-0001 was promoted under v1 earlier today and is the exact case the
new rule exists to prevent; the retraction propagation worked as
designed.

Needs Betsy: none.
