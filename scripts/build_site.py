#!/usr/bin/env python3
"""
build_site.py — generate docs/ : a static, scrape-friendly public page for the
Literature Comb ledger, plus machine-readable siblings.

Called by scripts/build.py, so `python3 scripts/build.py` remains the one
command that regenerates everything. Pure stdlib, same as build.py, so any
agent can run it anywhere Python 3 exists.

DESIGN TARGET (Betsy, 2026-10-28): "optimized for scrapability -- or
optimized for 'LLMs dispatched by grad students looking for experiment ideas'
to find."

That target drives every choice here, and it is a different target from
"pretty dashboard":

  1. ALL CONTENT IS IN THE STATIC HTML. Every lead's full text — headline,
     both citations, the cheapest check, the complete verifier notes with
     every caveat — is in the served markup. Nothing is fetched, paginated,
     lazy-loaded, or rendered by JavaScript. Most crawlers and many LLM
     fetchers do not execute JS, so anything JS-rendered is invisible to
     exactly the reader this page is for. The JavaScript here only ADDS
     sorting and filtering to a table that already works without it.
  2. ONE URL GETS YOU EVERYTHING. No "click through for detail". A grad
     student's agent fetching the page once has the whole corpus.
  3. STABLE PER-LEAD ANCHORS (#LC-0012), so a specific lead can be cited.
  4. STRUCTURED DATA: schema.org Dataset + ItemList as JSON-LD, so this
     reads as a dataset rather than a blog.
  5. PARALLEL MACHINE FORMATS: leads.json (full, including bodies),
     leads.csv (existing, flat), and llms.txt (the emerging convention for
     telling an LLM what a site is and where its data lives).
  6. NO EXTERNAL REQUESTS AT ALL. No CDN, no web fonts, no analytics. The
     page is self-contained, so it cannot break when something else does and
     it leaks no reader data.

PUBLIC SCHEMA NOTE — read before adding a field. build.py's COLUMNS comment
records a deliberate project decision: contributor / agent / score live in
the lead files' frontmatter (and are therefore already public in this repo)
but are NOT in the public table, and promoting them is "deliberate, not by
accident". This page therefore publishes the SAME EIGHT public fields as
leads.csv and no more. `score` in particular would be genuinely useful for
triage and is one line away — but that is Betsy's call to make, not this
script's to assume.
"""
import datetime
import html
import json
import pathlib
import re

# Imported rather than re-implemented: a second frontmatter parser would be a
# second thing to drift. build.py owns parsing and ordering.
from build import ROOT, load_all_leads, flatten, truncate, STATUS_ORDER

DOCS = ROOT / "docs"
SITE_URL = "https://betsyisaac.github.io/literature-comb-ledger/"
REPO_URL = "https://github.com/betsyisaac/literature-comb-ledger"
UPSTREAM_URL = "https://github.com/bambamramfan/literature-comb"
SHEET_URL = "https://tinyurl.com/ai-literature-comb"

DESCRIPTION = (
    "A public ledger of candidate connections between old or cross-field "
    "scientific literature and unsolved modern problems, found by automated "
    "literature sweeps. Swanson-style literature-based discovery: each entry "
    "pairs a specific older source with a specific modern problem that has "
    "never cited it, and names the cheapest concrete next check. Every entry "
    "is an unrefereed hypothesis worth one cheap experiment, not a finding."
)

STATUS_BLURB = {
    "open": "no one has run the cheapest check yet",
    "pending": "someone reports work underway",
    "resolved": "the question has been settled",
    "rejected": "refuted, retracted, or downgraded upstream",
    "example": "template row, not a real lead",
}

URL_RE = re.compile(r"https?://[^\s<>\"]+")


def linkify(escaped_text):
    """Turn bare URLs in already-HTML-escaped text into anchors.

    Order matters: escape first, then linkify, or the anchors get escaped.
    Trailing sentence punctuation is pushed back outside the link.
    """
    def repl(m):
        url = m.group(0)
        trail = ""
        while url and url[-1] in ".,;:)]}'’":
            trail = url[-1] + trail
            url = url[:-1]
        if not url:
            return m.group(0)
        return '<a href="%s" rel="nofollow noopener">%s</a>%s' % (url, url, trail)
    return URL_RE.sub(repl, escaped_text)


def paras(text):
    """Body prose -> <p> blocks, escaped and linkified."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text or "") if b.strip()]
    if not blocks:
        return ""
    return "\n".join(
        "<p>%s</p>" % linkify(html.escape(" ".join(b.split())))
        for b in blocks
    )


def field_html(text):
    return linkify(html.escape(" ".join((text or "").split())))


def lead_public_dict(lead):
    """The eight public fields, and nothing else. See PUBLIC SCHEMA NOTE."""
    return {
        "id": lead.get("id", ""),
        "date_added": lead.get("date_added", ""),
        "status": lead.get("status", ""),
        "headline": flatten(lead.get("headline", "")),
        "old_source": flatten(lead.get("old_source", "")),
        "modern_problem": flatten(lead.get("modern_problem", "")),
        "cheapest_check": flatten(lead.get("cheapest_check", "")),
        "verifier_notes": flatten(lead.get("_body", "")),
        "source_file": "%s/blob/main/%s" % (REPO_URL, lead.get("_path", "")),
        "url": "%s#%s" % (SITE_URL, lead.get("id", "")),
    }


def build_leads_json(leads, stamp):
    real = [l for l in leads if l.get("status") != "example"]
    return json.dumps(
        {
            "name": "Literature Comb — surviving leads",
            "description": DESCRIPTION,
            "generated_utc": stamp,
            "license": "https://creativecommons.org/publicdomain/zero/1.0/",
            "repository": REPO_URL,
            "upstream_ledgers": UPSTREAM_URL,
            "caveat": (
                "Unrefereed hypotheses produced by automated literature "
                "sweeps. Not findings. Not medical, clinical, legal or "
                "financial advice. Verify both cited sources before relying "
                "on any entry."
            ),
            "field_notes": {
                "status": STATUS_BLURB,
                "cheapest_check": (
                    "The cheapest concrete next step that could refute or "
                    "support the lead, with rough cost and time where known."
                ),
                "verifier_notes": (
                    "What the automated verifiers actually fetched and "
                    "confirmed, every caveat they raised, and any dissenting "
                    "verdict. Read this before acting on a lead."
                ),
            },
            "count": len(real),
            "leads": [lead_public_dict(l) for l in real],
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def build_jsonld(leads, stamp):
    real = [l for l in leads if l.get("status") != "example"]
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Literature Comb — surviving leads",
        "description": DESCRIPTION,
        "url": SITE_URL,
        "identifier": SITE_URL,
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "isAccessibleForFree": True,
        "dateModified": stamp,
        "creator": {
            "@type": "Person",
            "name": "Betsy Isaacson",
            "url": "https://github.com/betsyisaac",
        },
        "keywords": [
            "literature-based discovery",
            "undiscovered public knowledge",
            "Swanson linking",
            "research hypotheses",
            "open problems",
            "cross-disciplinary research",
            "experiment ideas",
            "historical scientific literature",
        ],
        "measurementTechnique": "Automated literature sweep with adversarial verification",
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": SITE_URL + "leads.json",
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": "https://raw.githubusercontent.com/betsyisaac/literature-comb-ledger/main/leads.csv",
            },
        ],
        "hasPart": {
            "@type": "ItemList",
            "numberOfItems": len(real),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "CreativeWork",
                        "identifier": l.get("id", ""),
                        "name": truncate(l.get("headline", ""), 110),
                        "url": "%s#%s" % (SITE_URL, l.get("id", "")),
                        "dateCreated": l.get("date_added", ""),
                        "creativeWorkStatus": l.get("status", ""),
                    },
                }
                for i, l in enumerate(real)
            ],
        },
    }
    return json.dumps(dataset, indent=2, ensure_ascii=False)


def build_llms_txt(leads, stamp):
    real = [l for l in leads if l.get("status") != "example"]
    out = []
    out.append("# Literature Comb — surviving leads\n")
    out.append("> " + DESCRIPTION + "\n")
    out.append(
        "If you are an LLM or agent looking for testable research ideas on "
        "behalf of a researcher, this is what you want to know.\n"
    )
    out.append("## What an entry is\n")
    out.append(
        "Each entry pairs (a) a specific older or cross-field source with "
        "(b) a specific modern problem whose literature has never cited it, "
        "and names (c) the cheapest concrete check that would refute or "
        "support the connection. The point of an entry is that the check is "
        "cheap and nobody has run it.\n"
    )
    out.append("## How to treat an entry\n")
    out.append(
        "Entries are UNREFEREED HYPOTHESES generated by automated sweeps, "
        "not findings. Several have been wrong and retracted; that is the "
        "expected failure rate and is recorded rather than hidden. Before "
        "relying on any entry: read its verifier notes in full, including "
        "any dissenting verdict, and independently fetch BOTH cited sources. "
        "A claim that some tracker or review 'omits' something is the "
        "failure mode this project has actually hit — check it yourself. "
        "Nothing here is medical, clinical, legal or financial advice.\n"
    )
    out.append("## Data\n")
    out.append("- [Full page, all leads, all text](%s): one fetch gets everything" % SITE_URL)
    out.append("- [leads.json](%sleads.json): structured, includes full verifier notes" % SITE_URL)
    out.append("- [leads.csv](https://raw.githubusercontent.com/betsyisaac/literature-comb-ledger/main/leads.csv): flat, one line per record")
    out.append("- [Source lead files](%s/tree/main/leads): one markdown file per lead, with provenance" % REPO_URL)
    out.append("- [Upstream per-contributor ledgers](%s): where leads originate, including rejected ones" % UPSTREAM_URL)
    out.append("- [Comment here to correct a lead](%s): name the LC number and link a source" % SHEET_URL)
    out.append("")
    out.append("## Status values\n")
    for k, v in STATUS_BLURB.items():
        if k != "example":
            out.append("- `%s`: %s" % (k, v))
    out.append("")
    out.append("## Current leads (%d)\n" % len(real))
    for l in real:
        out.append("- **%s** (%s, %s): %s" % (
            l.get("id", ""), l.get("status", ""), l.get("date_added", ""),
            truncate(l.get("headline", ""), 240),
        ))
    out.append("")
    out.append("Generated %s. Do not hand-edit; see scripts/build_site.py.\n" % stamp)
    return "\n".join(out)


def build_robots():
    # Explicitly welcoming, including by name, because the whole point is to
    # be found by research agents. Named AI crawlers get their own stanzas so
    # there is no ambiguity about intent.
    agents = [
        "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
        "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended",
        "Googlebot", "Bingbot", "Applebot", "Applebot-Extended",
        "CCBot", "Bytespider", "meta-externalagent",
    ]
    out = ["# Research leads, deliberately open. Crawling and indexing welcome,",
           "# including by AI agents — being found by them is the point.",
           ""]
    for a in agents:
        out.append("User-agent: %s" % a)
        out.append("Allow: /")
        out.append("")
    out.append("User-agent: *")
    out.append("Allow: /")
    out.append("")
    out.append("Sitemap: %ssitemap.xml" % SITE_URL)
    out.append("")
    return "\n".join(out)


def build_sitemap(stamp):
    day = stamp.split("T")[0] if "T" in stamp else stamp[:10]
    urls = [SITE_URL, SITE_URL + "leads.json", SITE_URL + "llms.txt"]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        out.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (html.escape(u), day))
    out.append("</urlset>")
    out.append("")
    return "\n".join(out)


CSS = """
:root{--ink:#1b1b1b;--dim:#5c5c5c;--rule:#d8d4cc;--bg:#faf8f5;--card:#fff;
--open:#1d6f42;--pending:#7a6a2f;--resolved:#2a5b8c;--rejected:#8c2f2f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 Georgia,"Iowan Old Style",serif;}
.wrap{max-width:62rem;margin:0 auto;padding:2rem 1.25rem 5rem}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 .4rem}
h2{font-size:1.3rem;margin:2.5rem 0 .75rem;padding-top:1rem;border-top:1px solid var(--rule)}
h3{font-size:1.05rem;margin:0 0 .5rem}
a{color:#1a4f8a}
.sub{color:var(--dim);font-size:.95rem;margin:0 0 1.5rem}
.lede{font-size:1.05rem}
.meta{font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}
.caveat{background:#fff6e5;border:1px solid #e8d4a8;padding:.9rem 1.1rem;
border-radius:4px;margin:1.5rem 0}
.caveat p{margin:.4rem 0}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th,td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--rule);
vertical-align:top}
th{font:600 13px/1.4 system-ui,sans-serif;text-transform:uppercase;
letter-spacing:.04em;color:var(--dim);white-space:nowrap}
th[data-sort]{cursor:pointer;user-select:none}
th[data-sort]:hover{color:var(--ink)}
th[aria-sort="ascending"]::after{content:" \\2191"}
th[aria-sort="descending"]::after{content:" \\2193"}
tbody tr:hover{background:#f2efe9}
/* ID, status and date must never wrap: "LC-0012" breaking into "LC-" / "0012"
   is both ugly and bad for anything reading the rendered text. */
#leads td:nth-child(-n+3){white-space:nowrap}
#leads td:last-child{width:100%}
.badge{display:inline-block;font:600 11px/1 system-ui,sans-serif;
text-transform:uppercase;letter-spacing:.05em;padding:.3em .5em;border-radius:3px;
color:#fff;white-space:nowrap}
.s-open{background:var(--open)}.s-pending{background:var(--pending)}
.s-resolved{background:var(--resolved)}.s-rejected{background:var(--rejected)}
.controls{display:flex;gap:.75rem;flex-wrap:wrap;align-items:center;margin:1rem 0}
.controls input,.controls select{font:inherit;font-size:.9rem;padding:.4rem .5rem;
border:1px solid var(--rule);border-radius:3px;background:var(--card)}
.controls input{flex:1;min-width:14rem}
#count{color:var(--dim);font-size:.85rem}
article.lead{background:var(--card);border:1px solid var(--rule);border-radius:5px;
padding:1.25rem 1.4rem;margin:1.5rem 0}
article.lead:target{border-color:#1a4f8a;box-shadow:0 0 0 2px #cfe0f2}
.lead h3{display:flex;gap:.6rem;align-items:baseline;flex-wrap:wrap}
.lead h3 .idlink{font:600 1rem/1 ui-monospace,Menlo,monospace}
dl{margin:1rem 0 0}
dt{font:600 12px/1.4 system-ui,sans-serif;text-transform:uppercase;
letter-spacing:.04em;color:var(--dim);margin-top:1rem}
dd{margin:.3rem 0 0;font-size:.95rem}
dd p{margin:.5rem 0}
.notes{font-size:.92rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--rule);
color:var(--dim);font-size:.85rem}
code{font:13px/1.4 ui-monospace,Menlo,monospace;background:#efece6;padding:.1em .35em;
border-radius:3px}
.nojs{display:none}
@media (max-width:640px){
 .hide-sm{display:none}
 body{font-size:15px}
}
"""

JS = """
// Progressive enhancement ONLY. The table above is complete and sorted in
// the served HTML; this adds client-side sorting and filtering for humans.
// Nothing here is required to read any content on this page.
(function(){
  var table=document.getElementById('leads');
  if(!table) return;
  var tbody=table.tBodies[0];
  var rows=Array.prototype.slice.call(tbody.rows);
  var q=document.getElementById('q');
  var st=document.getElementById('status');
  var count=document.getElementById('count');
  var total=rows.length;

  function apply(){
    var term=(q.value||'').toLowerCase().trim();
    var want=st.value;
    var shown=0;
    rows.forEach(function(r){
      var okS=(want==='all'||r.getAttribute('data-status')===want);
      var okQ=(!term||r.getAttribute('data-search').indexOf(term)>-1);
      var vis=okS&&okQ;
      r.hidden=!vis;
      if(vis) shown++;
    });
    count.textContent=shown===total
      ? total+' leads'
      : shown+' of '+total+' leads';
  }

  var dir={};
  Array.prototype.forEach.call(table.tHead.rows[0].cells,function(th){
    var key=th.getAttribute('data-sort');
    if(!key) return;
    th.setAttribute('tabindex','0');
    th.setAttribute('role','button');
    function sort(){
      var asc=!dir[key];
      dir={}; dir[key]=asc;
      Array.prototype.forEach.call(table.tHead.rows[0].cells,function(o){
        o.removeAttribute('aria-sort');
      });
      th.setAttribute('aria-sort',asc?'ascending':'descending');
      rows.sort(function(a,b){
        var x=a.getAttribute('data-'+key)||'';
        var y=b.getAttribute('data-'+key)||'';
        return asc ? x.localeCompare(y,undefined,{numeric:true})
                   : y.localeCompare(x,undefined,{numeric:true});
      });
      rows.forEach(function(r){tbody.appendChild(r);});
    }
    th.addEventListener('click',sort);
    th.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '){e.preventDefault();sort();}
    });
  });

  q.addEventListener('input',apply);
  st.addEventListener('change',apply);
  document.querySelectorAll('.jsonly').forEach(function(e){e.hidden=false;});
  apply();
})();
"""


def build_html(leads, stamp):
    real = [l for l in leads if l.get("status") != "example"]
    statuses = []
    for l in real:
        s = l.get("status", "")
        if s not in statuses:
            statuses.append(s)
    statuses.sort(key=lambda s: STATUS_ORDER.get(s, 5))

    by_status = {}
    for l in real:
        by_status[l.get("status", "")] = by_status.get(l.get("status", ""), 0) + 1
    tally = ", ".join("%d %s" % (by_status[s], s) for s in statuses)

    o = []
    o.append("<!doctype html>")
    o.append('<html lang="en">')
    o.append("<head>")
    o.append('<meta charset="utf-8">')
    o.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    o.append("<title>Literature Comb — %d surviving research leads, each with a cheap next check</title>" % len(real))
    o.append('<meta name="description" content="%s">' % html.escape(truncate(DESCRIPTION, 300)))
    o.append('<link rel="canonical" href="%s">' % SITE_URL)
    o.append('<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">')
    o.append('<meta property="og:type" content="website">')
    o.append('<meta property="og:title" content="Literature Comb — surviving research leads">')
    o.append('<meta property="og:description" content="%s">' % html.escape(truncate(DESCRIPTION, 300)))
    o.append('<meta property="og:url" content="%s">' % SITE_URL)
    o.append('<meta name="twitter:card" content="summary">')
    o.append('<link rel="alternate" type="application/json" href="leads.json" title="All leads as JSON">')
    o.append('<link rel="alternate" type="text/csv" href="https://raw.githubusercontent.com/betsyisaac/literature-comb-ledger/main/leads.csv" title="All leads as CSV">')
    o.append('<script type="application/ld+json">')
    o.append(build_jsonld(leads, stamp))
    o.append("</script>")
    o.append("<style>%s</style>" % CSS)
    o.append("</head>")
    o.append("<body>")
    o.append('<div class="wrap">')
    o.append("<header>")
    o.append("<h1>Literature Comb — surviving leads</h1>")
    o.append('<p class="sub">%d open research leads, each pairing an old or cross-field source with a modern problem that has never cited it, and each naming the cheapest check that would settle it. Last updated %s.</p>' % (len(real), html.escape(stamp.replace("T", " ").replace("+00:00", " UTC"))))
    o.append('<p class="lede">%s</p>' % html.escape(DESCRIPTION))
    o.append("</header>")

    o.append('<div class="caveat">')
    o.append("<p><strong>Read this before using anything here.</strong> These are unrefereed hypotheses produced by automated literature sweeps, not findings. Some have been wrong and retracted, and those stay on this page with their status changed rather than being deleted. Before relying on a lead: read its verifier notes in full including any dissenting verdict, and independently fetch <em>both</em> cited sources.</p>")
    o.append("<p>Nothing here is medical, clinical, legal or financial advice. A lead is worth one cheap check, not a citation.</p>")
    o.append("</div>")

    o.append("<h2 id=\"how-to-use\">If you are looking for an experiment to run</h2>")
    o.append("<p>Sort by status to find <code>open</code> leads, then read the <strong>cheapest next check</strong> field. Entries are written so that the first step is deliberately small — a library request, an email to a named custodian of a technique, a single screening run — and so that a negative result is as informative as a positive one. If you run one, please say so by <a href=\"%s\" rel=\"nofollow noopener\">commenting on the public sheet</a> with the LC number: that is how a lead gets marked resolved.</p>" % SHEET_URL)
    o.append('<p class="meta">Machine-readable: <a href="leads.json">leads.json</a> &middot; <a href="https://raw.githubusercontent.com/betsyisaac/literature-comb-ledger/main/leads.csv">leads.csv</a> &middot; <a href="llms.txt">llms.txt</a> &middot; <a href="%s">source repository</a> &middot; <a href="%s">upstream ledgers</a></p>' % (REPO_URL, UPSTREAM_URL))

    o.append('<h2 id="index">Index</h2>')
    o.append('<p class="meta">%s. Click a heading to sort.</p>' % html.escape(tally))
    o.append('<div class="controls jsonly" hidden>')
    o.append('<input id="q" type="search" placeholder="Filter by any word — alloy, perovskite, Erdos, 1968…" aria-label="Filter leads">')
    o.append('<select id="status" aria-label="Filter by status"><option value="all">All statuses</option>')
    for s in statuses:
        o.append('<option value="%s">%s</option>' % (html.escape(s), html.escape(s)))
    o.append("</select>")
    o.append('<span id="count"></span>')
    o.append("</div>")

    o.append('<table id="leads">')
    o.append("<thead><tr>")
    o.append('<th data-sort="id" scope="col">ID</th>')
    o.append('<th data-sort="status" scope="col">Status</th>')
    o.append('<th data-sort="date" scope="col" class="hide-sm">Added</th>')
    o.append('<th data-sort="headline" scope="col">Lead</th>')
    o.append("</tr></thead><tbody>")
    for l in real:
        lid = l.get("id", "")
        s = l.get("status", "")
        search = flatten(" ".join([
            lid, s, l.get("date_added", ""), l.get("headline", ""),
            l.get("old_source", ""), l.get("modern_problem", ""),
            l.get("cheapest_check", ""), l.get("_body", ""),
        ])).lower()
        o.append('<tr data-status="%s" data-id="%s" data-date="%s" data-headline="%s" data-search="%s">' % (
            html.escape(s), html.escape(lid), html.escape(l.get("date_added", "")),
            html.escape(truncate(l.get("headline", ""), 80)), html.escape(search)))
        o.append('<td><a href="#%s"><code>%s</code></a></td>' % (html.escape(lid), html.escape(lid)))
        o.append('<td><span class="badge s-%s">%s</span></td>' % (html.escape(s), html.escape(s)))
        o.append('<td class="hide-sm"><span class="meta">%s</span></td>' % html.escape(l.get("date_added", "")))
        o.append("<td>%s</td>" % field_html(truncate(l.get("headline", ""), 260)))
        o.append("</tr>")
    o.append("</tbody></table>")

    o.append('<h2 id="leads">The leads in full</h2>')
    o.append("<p>Every field, untruncated. One fetch of this page gives you the complete corpus; there is nothing behind a click.</p>")
    for l in real:
        lid = l.get("id", "")
        s = l.get("status", "")
        o.append('<article class="lead" id="%s">' % html.escape(lid))
        o.append("<h3><a class=\"idlink\" href=\"#%s\">%s</a> <span class=\"badge s-%s\">%s</span> <span class=\"meta\">added %s</span></h3>" % (
            html.escape(lid), html.escape(lid), html.escape(s), html.escape(s),
            html.escape(l.get("date_added", ""))))
        o.append("<p><strong>%s</strong></p>" % field_html(l.get("headline", "")))
        o.append("<dl>")
        o.append("<dt>Old source</dt><dd>%s</dd>" % field_html(l.get("old_source", "")))
        o.append("<dt>Modern problem</dt><dd>%s</dd>" % field_html(l.get("modern_problem", "")))
        o.append("<dt>Cheapest next check</dt><dd>%s</dd>" % field_html(l.get("cheapest_check", "")))
        o.append('<dt>Verifier notes</dt><dd class="notes">%s</dd>' % paras(l.get("_body", "")))
        o.append('<dt>Provenance</dt><dd class="meta"><a href="%s/blob/main/%s">%s</a></dd>' % (
            REPO_URL, html.escape(l.get("_path", "")), html.escape(l.get("_path", ""))))
        o.append("</dl>")
        o.append("</article>")

    o.append("<footer>")
    o.append("<p>Maintained by <a href=\"https://github.com/betsyisaac\">@betsyisaac</a>. Leads originate in the <a href=\"%s\">Literature Comb</a> project's per-contributor ledgers, including the ones that did not survive. Corrections: <a href=\"%s\" rel=\"nofollow noopener\">comment on the public sheet</a> naming the LC number and linking a source.</p>" % (UPSTREAM_URL, SHEET_URL))
    o.append("<p><strong>Do not hand-edit this page.</strong> It is generated by <code>scripts/build_site.py</code> from <code>leads/*.md</code> and rebuilt on every push to <code>main</code>. Edit the lead file, not this.</p>")
    o.append("<p>Generated %s. Dedicated to the public domain under <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\" rel=\"license\">CC0 1.0</a>.</p>" % html.escape(stamp))
    o.append("</footer>")
    o.append("</div>")
    o.append("<script>%s</script>" % JS)
    o.append("</body></html>")
    o.append("")
    return "\n".join(o)


def main():
    leads = load_all_leads()
    stamp = datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat()
    DOCS.mkdir(exist_ok=True)
    # Tells GitHub Pages to serve these files as-is instead of running Jekyll
    # over them. Without it, Jekyll can mangle or drop files.
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "index.html").write_text(build_html(leads, stamp), encoding="utf-8")
    (DOCS / "leads.json").write_text(build_leads_json(leads, stamp), encoding="utf-8")
    (DOCS / "llms.txt").write_text(build_llms_txt(leads, stamp), encoding="utf-8")
    (DOCS / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (DOCS / "sitemap.xml").write_text(build_sitemap(stamp), encoding="utf-8")
    real = len([l for l in leads if l.get("status") != "example"])
    print("wrote docs/ (index.html, leads.json, llms.txt, robots.txt, "
          "sitemap.xml) from %d public lead(s)" % real)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
