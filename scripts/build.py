#!/usr/bin/env python3
"""
Regenerates index.md and leads.csv from leads/*.md.

Pure stdlib on purpose — no pip install required, so any agent (Claude or
otherwise) can run this with a bare `python3 scripts/build.py` in any
environment that has Python 3.

DO NOT hand-edit index.md or leads.csv. They are derived mirrors of
leads/*.md, regenerated here and by .github/workflows/build.yml on every
push to main. Hand edits will be silently overwritten on the next build.
(This is the same discipline PMA uses for any aggregate that mirrors a
directory of individually-owned files: regenerate, never read-modify-write.)

Frontmatter format (flat on purpose — no nested YAML, no external parser
needed):

    ---
    id: LC-0001
    date_added: 2026-10-20
    status: open            # open | pending | resolved | rejected | example
    contributor: handle
    agent: claude-opus-4-7  # or gemini-..., codex-..., etc. Optional.
    score: 6.5               # Optional.
    headline: One sentence describing the candidate connection.
    old_source: Full citation + link, as one line.
    modern_problem: Full citation + link, as one line.
    cheapest_check: The cheapest concrete next check, with rough cost/time.
    ---
    Free-form body: the full verifier notes. What was checked, what could
    and couldn't be confirmed, every caveat, why it survived (or didn't).

Every frontmatter value must fit on one line. The body (after the second
`---`) can be as long as you like — that's where the real prose lives.
"""
import csv
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEADS_DIR = ROOT / "leads"
INDEX_MD = ROOT / "index.md"
LEADS_CSV = ROOT / "leads.csv"

# The public 8-column schema for leads.csv. Changing this is a schema change
# — per the project's own design decision, that needs a human go-ahead, not
# just an edit to this script. (Fields like contributor/agent live in the
# frontmatter and in git history even though they're not in the table below;
# promote them to a 9th/10th column deliberately, not by accident.)
#
# 2026-10-28, Betsy's explicit go-ahead: `score` was promoted to the PUBLIC
# PAGE and to docs/leads.json (see scripts/build_site.py), with a gloss
# explaining that slash-separated values are one score per verifier rather
# than a fraction. It was deliberately NOT added to leads.csv, because the
# CSV is the Google Sheet's feed and its column layout is settled there.
# Adding it here is a separate decision, still open.
COLUMNS = [
    "ID",
    "Date added",
    "Status",
    "Headline",
    "Old source",
    "Modern problem",
    "Cheapest next check",
    "Verifier notes",
]

STATUS_ORDER = {"open": 0, "pending": 1, "resolved": 2, "rejected": 3, "example": 9}


def parse_lead_file(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing frontmatter opening '---'")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: missing frontmatter closing '---'")
    _, fm_block, body = parts
    fields = {}
    for line in fm_block.strip("\n").splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{path}: malformed frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    fields["_body"] = body.strip()
    fields["_path"] = str(path.relative_to(ROOT))
    return fields


def load_all_leads() -> list[dict]:
    leads = []
    for path in sorted(LEADS_DIR.glob("*.md")):
        leads.append(parse_lead_file(path))
    # Group by status (open leads first, example/placeholder entries last
    # regardless of date), newest-first within each group.
    buckets: dict[str, list[dict]] = {}
    for lead in leads:
        buckets.setdefault(lead.get("status", ""), []).append(lead)
    ordered = []
    for status in sorted(buckets, key=lambda s: STATUS_ORDER.get(s, 5)):
        group = sorted(buckets[status], key=lambda l: l.get("date_added", ""), reverse=True)
        ordered.extend(group)
    return ordered


def flatten(text: str) -> str:
    """Collapse all whitespace (including newlines) to single spaces.

    Used for leads.csv specifically: some CSV consumers (notably Google
    Apps Script's Utilities.parseCsv) mis-parse fields containing literal
    line breaks even when properly quoted per RFC 4180. Keeping the CSV
    strictly one-line-per-record sidesteps that entirely. index.md and
    the individual leads/*.md files keep the real multi-paragraph prose —
    only the flat CSV gets this treatment.
    """
    return " ".join(text.split())


def truncate(text: str, n: int = 160) -> str:
    text = flatten(text)
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def build_index_md(leads: list[dict]) -> str:
    lines = []
    lines.append("# Literature Comb — surviving leads\n")
    lines.append(
        "Consolidated public ledger of surviving leads from the Literature Comb "
        'project — Swanson-style literature-based discovery, where "undiscovered '
        "public knowledge\" (a connection between two live literatures that have "
        "never cited each other) is surfaced by combing old and cross-field "
        "sources against modern problems. Each row is a hypothesis worth one "
        "cheap check, not a finding. Found by automated literature sweep; not "
        "refereed; no claim here is medical, clinical, legal, or financial "
        "advice.\n"
    )
    lines.append("| Field | |")
    lines.append("|---|---|")
    lines.append(f"| Last updated | {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} |")
    lines.append("| Public site | https://betsyisaac.github.io/literature-comb-ledger/ |")
    lines.append("| Maintainer | [@betsyisaac](https://github.com/betsyisaac) |")
    lines.append("| Per-contributor source ledgers | https://github.com/bambamramfan/literature-comb |")
    lines.append("| Project spec | https://github.com/bambamramfan/literature-comb/blob/main/SHARED-ROUTINE.md |")
    lines.append("| Machine-readable feed | [leads.csv](leads.csv) |")
    lines.append("")
    lines.append(
        "**DO NOT HAND-EDIT THIS FILE.** It is generated by `scripts/build.py` "
        "from `leads/*.md` and rebuilt automatically on every push to `main`. "
        "Edit the source file for the lead you want to change, not this one.\n"
    )
    lines.append("| " + " | ".join(COLUMNS) + " |")
    lines.append("|" + "|".join(["---"] * len(COLUMNS)) + "|")
    for lead in leads:
        row = [
            f"[{lead.get('id', '')}]({lead.get('_path', '')})",
            lead.get("date_added", ""),
            lead.get("status", ""),
            truncate(lead.get("headline", "")),
            truncate(lead.get("old_source", ""), 80),
            truncate(lead.get("modern_problem", ""), 80),
            truncate(lead.get("cheapest_check", ""), 80),
            truncate(lead.get("_body", ""), 140),
        ]
        row = [cell.replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


def build_leads_csv(leads: list[dict]) -> str:
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(COLUMNS)
    for lead in leads:
        writer.writerow([
            lead.get("id", ""),
            lead.get("date_added", ""),
            lead.get("status", ""),
            flatten(lead.get("headline", "")),
            flatten(lead.get("old_source", "")),
            flatten(lead.get("modern_problem", "")),
            flatten(lead.get("cheapest_check", "")),
            flatten(lead.get("_body", "")),
        ])
    return buf.getvalue()


def main() -> int:
    if not LEADS_DIR.is_dir():
        print(f"error: {LEADS_DIR} does not exist", file=sys.stderr)
        return 1
    try:
        leads = load_all_leads()
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not leads:
        print("warning: no lead files found under leads/", file=sys.stderr)
    INDEX_MD.write_text(build_index_md(leads), encoding="utf-8")
    LEADS_CSV.write_text(build_leads_csv(leads), encoding="utf-8")
    print(f"wrote {INDEX_MD.relative_to(ROOT)} and {LEADS_CSV.relative_to(ROOT)} from {len(leads)} lead file(s)")

    # The public GitHub Pages site. Imported here rather than at module level
    # because build_site imports from this module, and a top-level import
    # would be circular. Deliberately NOT wrapped in try/except: if the site
    # build breaks, CI should go red rather than quietly publishing a stale
    # page while reporting success. That failure mode — a green run over a
    # stale artefact — is exactly what cost three days on 2026-10-28.
    import build_site
    rc = build_site.main()
    if rc:
        print("error: site build failed", file=sys.stderr)
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
