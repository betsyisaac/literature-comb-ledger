# Promotion routine log

One entry per run of the daily promotion routine (see `promotion-state.json`
for the underlying dedup state, and the project README for how promotion
works). A run that finds nothing new logs that plainly — it's a correct,
complete result, not a gap.

---

## 2026-10-26 (session fc0cde6a)

Read 1 contributor ledger (`bambamramfan/surviving.md`). Upstream at
d3ceeb3 — no change since last run. 0 new / 0 renamed / 0 changed / 0
vanished. Comment feed: 3 threads total, none new or updated. Nothing to
do.

---

## 2026-10-25 (session 713397ec)

Waiting on PR #3 (`promote/2026-10-22`) to be merged; skipping today.

---

## 2026-10-24 (session dd02cbae)

Waiting on PR #3 (`promote/2026-10-22`) to be merged; skipping today.

---

## 2026-10-23 (session 8eb00a64)

Waiting on PR #3 (`promote/2026-10-22`) to be merged; skipping today.

---

## 2026-10-22 (session 49ec4f7b)

Read 1 contributor ledger (`bambamramfan/surviving.md`). Upstream advanced
from `581c0a1` to `d3ceeb3`. 14 new entries, 0 renamed, 0 changed, 0
vanished. Comments feed configured, 3 total threads, none new or updated.

Promoted 6 (one LC consolidates two sibling entries):

- **LC-0006** — bambamramfan:2026-10-21:tial_hot_salt_scc_300_500C (7/5/3; NASA CR-1133 Al2O3-accelerator pyrohydrolysis mechanism → gamma-TiAl HSSCC lower-than-canonical onset temperature)
- **LC-0007** — bambamramfan:2026-10-21:glass-core-static-fatigue (merged the 8/5/5-0-refuted entry with the 8/3/7 sibling — same W&B 1970 Table II → glass-core lifetime bridge, parameter-truncation framing with threshold-asymmetry angle folded in)
- **LC-0008** — bambamramfan:2026-10-21:dryland_station_soil_moisture_1906_1940 (6/6/3; Kansas SB 273 + Cole & Mathews / Rogler & Haas against Wang 2009 LSM ensemble; promoted with narrower framing — annual seeding-time snapshot ending 1934, not continuous 1906-1940)
- **LC-0009** — bambamramfan:2026-10-21:firn_tunnel_closure_calibration (7/6/5, 0 refuted; Landauer SIPRE RR 30 Site 2 excavation data → GM97 compressibility k; promoted with reframed cheap check — oblique diameters + deep-pit depth-dependence, not the naive three-way ratio)
- **LC-0010** — bambamramfan:2026-10-21:lusatia-flowliq-population (7/4/3; Wittig 2017 h_F/h_K arrest criterion from 67 Lusatian dump liquefactions → tailings-flow screen; promoted reframed as retrodiction on ~10 pre-failure-terrain flow failures, not against Ghahramani's post-event-only 33-case set)
- **LC-0011** — bambamramfan:2026-10-21:grain-storage-hermetic-insect-control (7/5/2; Banks 1978 CSIRO fractional-interchange sealing criterion → smallholder hermetic-bag airtightness tolerance; promoted with indoor/outdoor and two-fill-level controls folded in to separate thermal breathing and envelope compliance from leakage)

Skipped 8:

- **glass-core-static-fatigue 7/4/2** (NASA TM-103543 proof-test diagram): US 7,461,564 B2 (Glaesemann, Corning, 2006) already proof-tests glass panels for multi-year lifetime, so the institutional-separation gap mechanism fails; verifier 2 also noted its WebSearch budget ran out mid-sweep, so the ECTC/IMAPS/thesis proceedings search did not complete.
- **glass-core-static-fatigue 7/3/2** (NASA Bernstein / NASA-STD-5018 transplant): the same proof-test-plus-stress-corrosion-to-lifetime formalism is already an IEC standard (IEC/TR 62048, Telcordia GR-20) and Corning has published n ~20 for display glass; NASA-STD-5018 §§4.9.3/4.9.9 says proof testing cannot envelope residual-stress fields and edges are "extremely difficult to proof test adequately."
- **lpa 8/7/3** (constant-Reynolds staging from NASA TN D-8433): likely closest prior art is Gallardo Hevia 2023 Harvard PhD "Cascadable elastomer-based fluidic circuits"; two upstream verifiers could not open it (DASH 429, Wiley 403) or complete the search (OpenAlex 429). Unverified prior art is a failed check, not a caveat.
- **lpa 6/3/5** (power-modulation / short-splitter from HDL-CR-85-122-1): verifier 2 refuted — Gallardo Hevia 2023 Chapter 3 "Soft, Fluidic Power Amplifier" explicitly treats impedance matching for maximum power transfer, citing Bain 1970, Cycon & Schaffer 1982, Joyce 1983 HDL fluidics handbook; the connection is already in print.
- **deepwater_sludge_as_mcdr_analog 4/5/2**: the ~60 mg/m2/day loading is a MODEL prediction, delivered fraction is bounded only at 20-70%, the 10^4 km2 footprint is the C. perfringens tracer map not the benthic-oxygen result; Bauer et al. 2026 (Commun. Earth Environ.) is a year-long deliberate deep-ocean kelp emplacement with benthic monitoring — the substrate-correct regeneration of exactly this calibration.
- **phreatophyte_tank_et_vs_watertable_depth 4/6/2**: "Tamarix"/"saltcedar" appear zero times in TM 6-A39; the transitional riparian group is defined on outer-edge facultative species for which a deeper water table may be ideal by definition. Saltcedar maps to deep-rooted riparian (Table A5) which already declines monotonically with depth. Van Hylckama himself disclaims the 2.7 m endpoint on salinity grounds.
- **si3n4_static_fatigue_vs_amb_power_substrate_qualification 6/2/3**: Fig. 7 panel-misread corrected gives a 4-6 decade margin, the effective-volume move runs backwards, and a static-fatigue threshold near 390 MPa invalidates the power-law extrapolation across the window of interest. The gap is a correct null.
- **glass-core-static-fatigue 8/3/7** was recorded as "promoted" with LC-0007 (merged with the 0-refuted 8/5/5 sibling into one lead at discovery to avoid two LC numbers for substantially the same bridge); not an independent skip.

Comment threads handled: 0 (all three existing threads unchanged since last run; feed is quiet). Needs Betsy: nothing.

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
