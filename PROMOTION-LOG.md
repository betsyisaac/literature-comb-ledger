# Promotion routine log

One entry per run of the daily promotion routine (see `promotion-state.json`
for the underlying dedup state, and the project README for how promotion
works). A run that finds nothing new logs that plainly — it's a correct,
complete result, not a gap.

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
