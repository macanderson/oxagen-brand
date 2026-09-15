"""The message registry: load it, check it, and generate from it.

    python3 build/messages.py --check     # validate the registry and the generated files, write nothing
    python3 build/messages.py             # write messages/index.json and message-bank.html
    python3 build/messages.py --verbose   # also list context-dependent words to read in place

Every line either brand publishes is one YAML file under `messages/`. This
module is the only reader of those files: `build/build.py` takes its ad copy
and taglines from `ad_campaigns()` and `taglines()`, and the message bank and
the JSON index are rendered here. Nothing downstream keeps its own copy, so a
line changes in one place.

Needs PyYAML and nothing else (`.venv/bin/pip install pyyaml`).
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    sys.exit("PyYAML is required: .venv/bin/pip install pyyaml (or python3 -m pip install pyyaml)")

ROOT = Path(__file__).resolve().parent.parent
MESSAGES = ROOT / "messages"
FINDINGS = MESSAGES / "findings.yaml"
INDEX = MESSAGES / "index.json"
BANK = ROOT / "message-bank.html"
WORDS = ROOT / "skills" / "oxagen-branding" / "references" / "words.md"
ADS = ROOT / "ads"
BUILD_PY = ROOT / "build" / "build.py"

BRANDS = ("oxagen", "stella")
KINDS = ("headline", "eyebrow", "pitch", "section", "card", "entry-point", "rule", "proof", "pair",
         "email", "announcement", "ad", "glossary")
AUDIENCES = ("operator", "platform", "security", "finance", "engineering", "knowledge", "investor")
CLAUSES = ("access", "budget", "equipment", "record", "operations", "none")
STATUSES = ("candidate", "approved", "retired")
RELEASES = ("launch", "held")
PICTURES = ("ghost", "orbit")

#: Folder name, page heading. The order is the order of the page.
GROUPS = (
    ("lead", "Lead"),
    ("sections", "Sections"),
    ("entry-points", "Entry points"),
    ("access", "Access"),
    ("proof", "Proof"),
    ("mission-control", "Mission Control"),
    ("definition-of-done", "Definition of done"),
    ("witness", "Witness"),
    ("identity-equipment", "Identity and equipment"),
    ("outreach", "Outreach"),
    ("ads", "Ads"),
    ("voice", "Voice"),
    ("rules", "Rules"),
    ("retired", "Retired"),
)
CARD_GROUPS = ("mission-control", "definition-of-done", "witness", "identity-equipment")

#: Every ad ships at these sizes, on both grounds. build.py renders exactly this set.
AD_SIZES = [(1080, 1080, "square"), (1080, 1350, "portrait"), (1200, 628, "landscape"), (300, 250, "mpu")]
SCHEMES = ("dark", "light")

#: The registry entry each brand's social and manifest tagline comes from.
TAGLINE_IDS = {"oxagen": "hero-headline", "stella": "stella-tagline"}

STR_FIELDS = ("id", "brand", "kind", "title", "short", "long", "cta", "cta_destination", "kicker", "subline",
              "subshort", "picture", "before", "after", "clause", "status", "release", "qualifier", "evidence",
              "owner", "notes")
LIST_FIELDS = ("audience", "surfaces", "gate", "findings", "headline", "wide", "short_lines", "scope_terms", "phrases")
ALL_FIELDS = set(STR_FIELDS) | set(LIST_FIELDS) | {"order", "rows", "review_by", "replaced_by"}
REQUIRED = ("id", "brand", "kind", "title", "audience", "clause", "surfaces", "status", "owner", "findings")
EVIDENCE_KINDS = {"headline", "eyebrow", "pitch", "section", "card", "entry-point", "proof", "email", "announcement", "ad"}

#: Customer-facing text. `before` is the wrong version on purpose and is left out.
TEXT_FIELDS = ("title", "short", "long", "cta", "kicker", "subline", "subshort", "qualifier", "after")
LINE_FIELDS = ("headline", "wide", "short_lines")

DASHES = re.compile("[‒–—―]")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

#: The floor of the prospect blocklist, in case the rule file is edited away.
PROSPECT_RULE = "rule-prospect-markers"
PROSPECT_FLOOR = ("Dan,", "Cary", "design partners", "council of nine")

#: Words the brand allows although an older list avoided them.
AVOID_ALLOWED = {"workforce", "autonomous"}
#: Used only if words.md loses its "Avoid these" section.
AVOID_FALLBACK = ("seamless", "robust", "powerful", "revolutionary", "comprehensive", "end-to-end", "intelligent",
                  "magic", "excited", "thrilled", "guardrails", "observability", "trust layer", "AI-powered",
                  "agentic", "connect your agent to", "give the agent access to", "auto-approve")


# ---------------------------------------------------------------------------- loading


def load() -> list[dict]:
    """Every entry, with `group` and `path` added, in page order. Raises on unreadable YAML."""
    entries = []
    order = {g: i for i, (g, _) in enumerate(GROUPS)}
    for p in sorted(MESSAGES.rglob("*.yaml")):
        if p == FINDINGS:
            continue
        rel = p.relative_to(MESSAGES)
        data = yaml.safe_load(p.read_text())
        if not isinstance(data, dict):
            data = {"__invalid__": True}
        if isinstance(data.get("review_by"), dt.date):
            data["review_by"] = data["review_by"].isoformat()
        data["_group"] = rel.parts[0] if len(rel.parts) == 2 else ""
        data["_path"] = f"messages/{rel.as_posix()}"
        data["_stem"] = p.stem
        entries.append(data)
    entries.sort(key=lambda e: (order.get(e["_group"], 99), e.get("order", 0) if isinstance(e.get("order"), int) else 0, str(e.get("id", ""))))
    return entries


def load_findings() -> list[dict]:
    data = yaml.safe_load(FINDINGS.read_text())
    return list(data.get("findings", [])) if isinstance(data, dict) else []


def public(e: dict) -> dict:
    """The entry as it appears in index.json: its fields, plus group and path."""
    out = {k: v for k, v in e.items() if not k.startswith("_")}
    out["group"] = e["_group"]
    out["path"] = e["_path"]
    return out


def by_id(entries: list[dict]) -> dict[str, dict]:
    return {e["id"]: e for e in entries if isinstance(e.get("id"), str)}


def live(e: dict) -> bool:
    return e.get("status") == "approved" and e.get("release") == "launch"


def slug_of(e: dict) -> str:
    return str(e["id"])[len(f"ad-{e['brand']}-"):]


def ad_campaigns(entries: list[dict] | None = None) -> dict[str, list[dict[str, object]]]:
    """Approved, launch-released ads as build.py's campaign dicts. Held and retired ads are not rendered."""
    entries = load() if entries is None else entries
    out: dict[str, list[dict[str, object]]] = {b: [] for b in BRANDS}
    for e in entries:
        if e.get("kind") != "ad" or not live(e):
            continue
        c: dict[str, object] = {
            "slug": slug_of(e),
            "kicker": e["kicker"],
            "headline": list(e["headline"]),
            "short": list(e["short_lines"]),
            "cta": e["cta"],
            "id": e["id"],
        }
        for f in ("wide", "subline", "subshort", "picture"):
            if f in e:
                c[f] = list(e[f]) if isinstance(e[f], list) else e[f]
        out[e["brand"]].append(c)
    return out


def taglines(entries: list[dict] | None = None) -> dict[str, str]:
    """The social and manifest tagline for each brand, from an approved, launch-released entry."""
    ids = by_id(load() if entries is None else entries)
    out = {}
    for brand, eid in TAGLINE_IDS.items():
        e = ids.get(eid)
        if not e or not live(e) or e.get("brand") != brand:
            raise SystemExit(f"tagline for {brand} needs an approved, launch-released entry {eid}")
        out[brand] = str(e["title"])
    return out


# ---------------------------------------------------------------------------- words


def _split_top_level(line: str) -> list[str]:
    items, depth, cur = [], 0, []
    for ch in line:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            items.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    items.append("".join(cur))
    return items


def avoid_terms() -> tuple[list[tuple[str, bool, str]], list[str]]:
    """(term, qualified, group) from words.md's "Avoid these" section.

    A term with a parenthetical, such as `never (about outcomes)`, depends on
    context, so it is a warning. The parser skips prose, tables, and
    Before/After example lines, so new groups can be added freely.
    """
    notes: list[str] = []
    if not WORDS.exists():
        return [(t, False, "fallback") for t in AVOID_FALLBACK], [f"{WORDS.relative_to(ROOT)} not found; using the built-in avoid list"]
    terms: list[tuple[str, bool, str]] = []
    inside, group = False, ""
    for raw in WORDS.read_text().splitlines():
        line = raw.strip()
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith("avoid")
            group = ""
            continue
        if not inside:
            continue
        if line.startswith("### "):
            group = line[4:].strip()
            continue
        if not line or not group or line.startswith(("|", ">", "```", "#")):
            continue
        line = re.sub(r"^[-*+]\s+", "", line)
        if re.match(r"^\**(before|after|example|examples|note|notes|why|instead)\b", line, re.I):
            continue
        if len(line.split()) > 8 and "," not in line:
            continue  # a sentence, not a list
        for item in _split_top_level(line):
            item = item.strip().strip("*`").strip()
            qualified = "(" in item
            term = re.sub(r"\s*\(.*?\)\s*", " ", item).strip()
            term = term.strip("\"'“”‘’").rstrip(".;:").strip()
            if not term or len(term.split()) > 6 or term.lower() in AVOID_ALLOWED:
                continue
            terms.append((term, qualified, group))
    if not terms:
        notes.append("words.md has no parsable Avoid these section; using the built-in avoid list")
        terms = [(t, False, "fallback") for t in AVOID_FALLBACK]
    return terms, notes


def avoid_groups() -> list[tuple[str, list[str]]]:
    """The avoid lists as groups, for the page."""
    terms, _ = avoid_terms()
    groups: dict[str, list[str]] = {}
    for t, _q, g in terms:
        groups.setdefault(g, []).append(t)
    return list(groups.items())


def _pattern(term: str, *, case: bool) -> re.Pattern[str]:
    body = re.escape(term.replace("’", "'"))
    pre = r"(?<!\w)" if re.match(r"\w", term) else ""
    post = r"(?!\w)" if re.search(r"\w$", term) else ""
    return re.compile(pre + body + post, 0 if case else re.I)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'")).strip().lower()


# ---------------------------------------------------------------------------- validation


def customer_texts(e: dict):
    for f in TEXT_FIELDS:
        v = e.get(f)
        if isinstance(v, str) and v:
            yield f, v
    for f in LINE_FIELDS:
        for i, v in enumerate(e.get(f) or []):
            if isinstance(v, str):
                yield f"{f}[{i}]", v
    for i, r in enumerate(e.get("rows") or []):
        if isinstance(r, dict):
            for k in ("label", "text"):
                if isinstance(r.get(k), str):
                    yield f"rows[{i}].{k}", r[k]


def all_texts(e: dict):
    yield from customer_texts(e)
    for f in ("before", "notes", "evidence", "cta_destination", "owner"):
        v = e.get(f)
        if isinstance(v, str) and v:
            yield f, v
    for i, v in enumerate(e.get("phrases") or []):
        if isinstance(v, str):
            yield f"phrases[{i}]", v


def prose_problems(text: str) -> list[str]:
    out = []
    if DASHES.search(text):
        out.append("an em or en dash")
    if "!" in text:
        out.append("an exclamation point")
    return out


def blocklists(entries: list[dict]) -> tuple[list[tuple[str, str]], list[str]]:
    """(phrase, rule id) for claim phrases, and the prospect markers."""
    claims, prospects = [], list(PROSPECT_FLOOR)
    for e in entries:
        if e.get("kind") != "rule" or e.get("status") == "retired":
            continue
        for ph in e.get("phrases") or []:
            if not isinstance(ph, str):
                continue
            if e.get("id") == PROSPECT_RULE:
                if ph not in prospects:
                    prospects.append(ph)
            else:
                claims.append((ph, str(e["id"])))
    return claims, prospects


def phrase_hits(text: str, phrases) -> list[str]:
    return [ph for ph in phrases if _pattern(ph, case=any(c.isupper() for c in ph)).search(text.replace("’", "'"))]


def validate(entries: list[dict], findings: list[dict], *, today: dt.date | None = None) -> tuple[list[str], list[str], Counter]:
    """Every problem with the registry itself. Returns (errors, warnings, context-word counts)."""
    today = today or dt.date.today()
    errors: list[str] = []
    warnings: list[str] = []
    context_words: Counter = Counter()
    groups = {g for g, _ in GROUPS}
    finding_ids = {str(f.get("id")) for f in findings}
    if len(finding_ids) != len(findings) or not finding_ids:
        errors.append("messages/findings.yaml: findings need unique ids")
    for f in findings:
        for k in ("id", "priority", "title", "rule"):
            if not isinstance(f.get(k), str) or not f.get(k):
                errors.append(f"messages/findings.yaml: finding {f.get('id')} is missing {k}")

    seen: dict[str, str] = {}
    ids = by_id(entries)
    terms, notes = avoid_terms()
    warnings.extend(notes)
    avoid = [(t, q, _pattern(t, case=False)) for t, q, _ in terms]
    claims, prospects = blocklists(entries)
    retired_texts = [(_norm(str(e["title"])).rstrip("."), e["id"]) for e in entries
                     if e.get("status") == "retired" and isinstance(e.get("title"), str) and len(_norm(e["title"])) > 8]

    for e in entries:
        where = e["_path"]
        err = lambda msg: errors.append(f"{where}: {msg}")  # noqa: E731
        if e.get("__invalid__"):
            err("is not a YAML mapping")
            continue
        if e["_group"] not in groups:
            err(f"sits outside a known group folder ({', '.join(g for g, _ in GROUPS)})")
        for k in e:
            if not k.startswith("_") and k not in ALL_FIELDS:
                err(f"unknown field {k!r}")
        for k in REQUIRED:
            if k not in e or e[k] in (None, "") and k != "findings":
                err(f"missing required field {k!r}")
        eid = e.get("id")
        if isinstance(eid, str):
            if not KEBAB.match(eid):
                err(f"id {eid!r} is not kebab case")
            if eid != e["_stem"]:
                err(f"id {eid!r} does not match the file name {e['_stem']!r}")
            if eid in seen:
                err(f"duplicate id {eid!r}, also in {seen[eid]}")
            seen[eid] = where
        for k in STR_FIELDS:
            if k in e and e[k] is not None and not isinstance(e[k], str):
                err(f"{k} must be a string")
        for k in LIST_FIELDS:
            if k in e and (not isinstance(e[k], list) or not all(isinstance(x, str) and x for x in e[k])):
                err(f"{k} must be a list of non-empty strings")
        if "order" in e and not isinstance(e["order"], int):
            err("order must be an integer")
        if "rows" in e and (not isinstance(e["rows"], list) or not all(
                isinstance(r, dict) and set(r) == {"label", "text"} and all(isinstance(v, str) for v in r.values()) for r in e["rows"])):
            err("rows must be a list of {label, text}")

        enum = (("brand", BRANDS), ("kind", KINDS), ("clause", CLAUSES), ("status", STATUSES), ("release", RELEASES), ("picture", PICTURES))
        for k, allowed in enum:
            if k in e and e[k] not in allowed:
                err(f"{k} {e[k]!r} is not one of {', '.join(allowed)}")
        for a in e.get("audience") or []:
            if a not in AUDIENCES:
                err(f"audience {a!r} is not one of {', '.join(AUDIENCES)}")
        if isinstance(e.get("audience"), list) and not e["audience"]:
            err("audience needs at least one reader")
        for fid in e.get("findings") or []:
            if fid not in finding_ids:
                err(f"finding {fid!r} is not in messages/findings.yaml")
        for g in e.get("gate") or []:
            if not KEBAB.match(g):
                err(f"gate {g!r} is not kebab case")

        status, kind = e.get("status"), e.get("kind")
        if status == "retired":
            if "replaced_by" not in e:
                err("retired without replaced_by")
            rep = e.get("replaced_by")
            if rep is None and not e.get("notes"):
                err("retired with replaced_by null and no notes saying why")
            if rep is not None:
                target = ids.get(rep) if isinstance(rep, str) else None
                if not target:
                    err(f"replaced_by {rep!r} is not an entry")
                elif target.get("status") == "retired":
                    err(f"replaced_by {rep!r} is itself retired")
        else:
            if "replaced_by" in e:
                err("replaced_by belongs only on a retired entry")
            for k in ("release", "review_by"):
                if not e.get(k):
                    err(f"missing required field {k!r}")
            if e.get("release") == "held" and not e.get("gate"):
                err("held without a gate")
            if e.get("release") == "launch" and e.get("gate"):
                err("released at launch but still names a gate")
            if status == "approved" and e.get("release") == "launch" and kind in EVIDENCE_KINDS and not e.get("evidence"):
                err("approved launch copy needs evidence")
            rb = e.get("review_by")
            if isinstance(rb, str):
                try:
                    if dt.date.fromisoformat(rb) < today:
                        warnings.append(f"{where}: review_by {rb} has passed")
                except ValueError:
                    err(f"review_by {rb!r} is not an ISO date")

        if kind == "ad":
            for k in ("kicker", "headline", "short_lines", "cta"):
                if not e.get(k):
                    err(f"an ad needs {k}")
            if isinstance(eid, str) and e.get("brand") in BRANDS and not eid.startswith(f"ad-{e['brand']}-"):
                err(f"an ad id starts with ad-{e.get('brand')}-")
            title = _norm(str(e.get("title", "")))
            for k in ("headline", "wide"):
                if isinstance(e.get(k), list) and _norm(" ".join(e[k])) != title:
                    err(f"{k} does not join to the title")
            terms_ = [t.lower() for t in e.get("scope_terms") or []]
            if terms_:
                for k in ("subline", "subshort"):
                    if isinstance(e.get(k), str) and not any(t in e[k].lower() for t in terms_):
                        err(f"{k} drops the scope: it needs one of {', '.join(terms_)}")
        else:
            for k in ("kicker", "headline", "wide", "short_lines", "subline", "subshort", "picture", "scope_terms"):
                if k in e:
                    err(f"{k} belongs only on an ad")
        if kind == "pair" and status != "retired" and not (e.get("before") and e.get("after")):
            err("a pair needs before and after")
        if "phrases" in e and kind != "rule":
            err("phrases belong only on a rule")

        # prose
        for f, text in all_texts(e):
            for p in prose_problems(text):
                err(f"{f} has {p}")
        if e.get("id") != PROSPECT_RULE:
            for f, text in all_texts(e):
                for ph in phrase_hits(text, prospects):
                    err(f"{f} carries a prospect or deal marker ({ph!r})")
        if status != "retired" and kind != "rule":
            for f, text in customer_texts(e):
                flat = text.replace("’", "'")
                for term, qualified, pat in avoid:
                    if pat.search(flat):
                        if qualified:
                            context_words[term] += 1
                            warnings.append(f"{where}: {f} uses {term!r}, which words.md allows only in context")
                        else:
                            err(f"{f} uses the avoided word {term!r}")
                for ph, rid in claims:
                    if phrase_hits(text, [ph]):
                        err(f"{f} uses {ph!r}, blocked by {rid}")
        if status == "approved" and kind != "rule":
            for f, text in customer_texts(e):
                flat = _norm(text)
                for rt, rid in retired_texts:
                    if rt and rt in flat:
                        err(f"{f} repeats retired text from {rid}")
    return errors, warnings, context_words


def check_ads_on_disk(entries: list[dict]) -> list[str]:
    """Every file in ads/ comes from an approved, launch-released ad, and every such ad is complete."""
    problems = []
    campaigns = ad_campaigns(entries)
    expected = {f"{b}-{c['slug']}-{tag}-{w}x{h}-{s}" for b in BRANDS for c in campaigns[b]
                for w, h, tag in AD_SIZES for s in SCHEMES}
    if not ADS.exists():
        return ["ads/ does not exist; run .venv/bin/python build/build.py --only ads"]
    stems_by_ext: dict[str, set[str]] = {".svg": set(), ".png": set()}
    for p in sorted(ADS.iterdir()):
        if p.name.startswith("."):
            continue
        if p.suffix not in stems_by_ext:
            problems.append(f"ads/{p.name}: not an ad file")
            continue
        stems_by_ext[p.suffix].add(p.stem)
        if p.stem not in expected:
            problems.append(f"ads/{p.name}: no approved, launch-released ad entry renders this file")
    for stem in sorted(expected - stems_by_ext[".svg"]):
        problems.append(f"ads/{stem}.svg is missing; run .venv/bin/python build/build.py --only ads")
    if stems_by_ext[".png"]:
        for stem in sorted(expected - stems_by_ext[".png"]):
            problems.append(f"ads/{stem}.png is missing beside its SVG")
    src = BUILD_PY.read_text() if BUILD_PY.exists() else ""
    if re.search(r'"kicker"\s*:', src) or re.search(r'"subline"\s*:\s*"', src):
        problems.append("build/build.py hard-codes ad copy; ads come from messages/ads/")
    return problems


# ---------------------------------------------------------------------------- page

T = lambda s: html.escape(str(s), quote=False)  # noqa: E731
A = lambda s: html.escape(str(s), quote=True)  # noqa: E731


def paras(text: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{T(p.strip())}</p>" for p in str(text).split("\n\n") if p.strip())


class Page:
    def __init__(self, entries: list[dict], findings: list[dict]):
        self.entries = entries
        self.findings = findings
        self.ids = by_id(entries)
        self.rendered: set[str] = set()

    def of(self, group: str, kind: str | None = None, prefix: str | None = None) -> list[dict]:
        return [e for e in self.entries if e["_group"] == group and (kind is None or e["kind"] == kind)
                and (prefix is None or e["id"].startswith(prefix))]

    def anchor(self, e: dict) -> str:
        self.rendered.add(e["id"])
        return f'id="m-{A(e["id"])}"'

    def link(self, eid: str | None) -> str:
        if not eid or eid not in self.ids:
            return "not carried"
        return f'<a href="#m-{A(eid)}">{T(self.ids[eid]["title"])}</a>'

    @staticmethod
    def badges(e: dict) -> str:
        out = []
        if e["status"] == "retired":
            out.append('<span class="badge retired">retired</span>')
        else:
            out.append(f'<span class="badge {A(e["status"])}">{T(e["status"])}</span>')
            if e.get("release") == "held":
                out.append(f'<span class="badge held">held until {T(", ".join(e.get("gate") or []))}</span>')
            else:
                out.append('<span class="badge launch">launch</span>')
        if e.get("brand") == "stella":
            out.append('<span class="badge">stella</span>')
        out.append(f'<span class="badge id">{T(e["id"])}</span>')
        return "".join(out)

    def meta(self, e: dict) -> str:
        rows = []
        if e.get("qualifier"):
            rows.append(("Scope", T(e["qualifier"])))
        if e.get("audience"):
            rows.append(("Readers", T(", ".join(e["audience"]))))
        if e.get("surfaces"):
            rows.append(("Used on", T(", ".join(s.replace("-", " ") for s in e["surfaces"]))))
        if e.get("evidence"):
            rows.append(("Launch evidence", T(e["evidence"])))
        rows.append(("Owner", T(e["owner"]) + (f", review by {T(e['review_by'])}" if e.get("review_by") else "")))
        if e.get("findings"):
            rows.append(("Findings", ", ".join(f'<a href="#finding-{A(f)}">{T(f)}</a>' for f in e["findings"])))
        if e.get("cta_destination"):
            rows.append(("Action leads to", T(e["cta_destination"])))
        if e.get("notes"):
            rows.append(("Notes", T(e["notes"])))
        body = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
        return (f'<div class="meta">{self.badges(e)}<details><summary>Scope, evidence, and owner</summary>'
                f'<dl>{body}</dl></details></div>')

    # ------------------------------------------------------------------ sections

    def hero(self) -> str:
        head, brow = self.ids["hero-headline"], self.ids["hero-eyebrow"]
        c = Counter(e["status"] for e in self.entries)
        r = Counter(e.get("release") for e in self.entries if e["status"] != "retired")
        return f"""<section class="hero" style="border-top:0;padding-top:0">
<p class="eyebrow">{T(brow["title"])}</p>
<h1>{T(head["title"])}</h1>
<p class="lead">{T(head["short"])}</p>
<p class="note">Every line on this page is generated from the registry in <span class="mono">messages/</span>. To change one, edit its YAML file and run <span class="mono">python3 build/messages.py</span>. The registry holds {len(self.entries)} entries: {c["approved"]} approved, {c["candidate"]} candidate, and {c["retired"]} retired. Of the live ones, {r["launch"]} ship at launch and {r["held"]} wait for a capability.</p>
<div class="hero-actions"><a class="btn primary" href="#lines" style="display:inline-flex;align-items:center">Pick a line</a><a class="btn" href="#held" style="display:inline-flex;align-items:center">See what is held</a></div>
</section>"""

    def claim(self) -> str:
        claim, mandate = self.ids["claim-one-mandate"], self.ids["glossary-mandate"]
        rows = "".join(
            f'<tr {self.anchor(e)}><td><b>{T(e["title"])}</b></td><td>{T(", ".join(e["audience"]))}</td><td>{T(e["long"])}</td></tr>'
            for e in self.of("lead", "glossary", "clause-"))
        lead_rule = self.ids.get("rule-lead-with-clause")
        return f"""<section id="claim"><p class="eyebrow q">The claim</p><h2 {self.anchor(claim)}>{T(claim["title"])}</h2>
{paras(claim["long"])}{self.meta(claim)}
<div class="ex" {self.anchor(mandate)}><div class="lbl">{T(mandate["title"])}, defined once</div><p>{T(mandate["long"])}</p><p>{T(mandate["short"])}</p>{self.meta(mandate)}</div>
<div class="tw"><table><thead><tr><th>Clause</th><th>Read first by</th><th>What it covers</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">{T(lead_rule["long"]) if lead_rule else ""} See <a href="#avoid">the rules</a>.</p></section>"""

    def lines(self) -> str:
        rows = []
        for e in self.of("lead"):
            if e["kind"] not in ("headline", "eyebrow"):
                continue
            rows.append(f'<tr {self.anchor(e)}><td><b>{T(e["title"])}</b></td><td>{T(", ".join(s.replace("-", " ") for s in e["surfaces"]))}</td>'
                        f'<td>{T(e.get("qualifier", ""))}</td><td>{self.badges(e)}</td></tr>')
        refs = [self.ids[i] for i in ("access-keys", "security-headline", "finance-headline", "knowledge-headline",
                                      "dod-not-your-call", "dod-define-before") if i in self.ids]
        for e in refs:
            rows.append(f'<tr><td><b><a href="#m-{A(e["id"])}">{T(e["title"])}</a></b></td><td>{T(", ".join(s.replace("-", " ") for s in e["surfaces"]))}</td>'
                        f'<td>{T(e.get("qualifier", ""))}</td><td>{self.badges(e)}</td></tr>')
        return f"""<section id="lines"><p class="eyebrow q">Lines</p><h2>Approved messages, with release status and scope</h2>
<p>The lead lines, then the headlines that open a page or a section. A held line waits for the capability named on its badge. Open any entry for its launch evidence and owner.</p>
<div class="tw"><table><thead><tr><th>Line</th><th>Use it for</th><th>Scope</th><th>Status</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="note">Mission Control is the product. The agent control plane is the category. <a href="#m-rule-naming">The naming rule</a> has the rest.</p></section>"""

    def pitch(self) -> str:
        blocks = []
        for e in self.of("lead", "pitch"):
            if e["id"] == "claim-one-mandate":
                continue
            label = "One sentence" if e["id"] == "pitch-one-sentence" else e["title"]
            body = f"<p>{T(e['title'])}</p>" if e["id"] == "pitch-one-sentence" else paras(e.get("long", ""))
            act = f'<span class="action">{T(e["cta"])}</span>' if e.get("cta") else ""
            blocks.append(f'<div class="ex" {self.anchor(e)}><div class="lbl">{T(label)}</div>{body}{act}{self.meta(e)}</div>')
        return f'<section id="pitch"><p class="eyebrow q">The pitch</p><h2>One sentence, then the paragraph</h2>{"".join(blocks)}</section>'

    def sections(self) -> str:
        blocks = []
        for e in self.of("sections", "section"):
            if e["id"] in ("docs-writing-a-rule", "ui-strings-access"):
                continue
            q = f'<p class="note">{T(e["qualifier"])}</p>' if e.get("qualifier") else ""
            blocks.append(f'<div class="ex" {self.anchor(e)}><div class="lbl">Product page section</div><h4>{T(e["title"])}</h4>{paras(e["long"])}{q}{self.meta(e)}</div>')
        return (f'<section id="sections"><p class="eyebrow q">Sections</p><h2>The product page, in the operator\'s order</h2>'
                f'<p>Authority, equipment, work, operations, and the audit record. Completion is a control for work with an endpoint.</p>{"".join(blocks)}</section>')

    def entry_points(self) -> str:
        blocks = []
        for e in self.of("entry-points"):
            q = f'<p class="note">{T(e["qualifier"])}</p>' if e.get("qualifier") else ""
            act = f'<span class="action">{T(e["cta"])}</span>' if e.get("cta") else ""
            blocks.append(f'<div class="ex" {self.anchor(e)}><div class="lbl">{T(", ".join(e["audience"]))}</div><h4>{T(e["title"])}</h4>{paras(e["long"])}{act}{q}{self.meta(e)}</div>')
        return (f'<section id="entry-points"><p class="eyebrow q">Entry points</p><h2>Security, finance, and knowledge each get a door</h2>'
                f'<p>Each opens onto the same control plane. The finance door shows recorded cost. The knowledge door keeps context inside the agent\'s permitted scope.</p>{"".join(blocks)}</section>')

    def keys(self) -> str:
        head, model = self.ids["access-keys"], self.ids["access-request-model"]
        rules = "".join(f'<li class="quoted" {self.anchor(e)}><b>{T(e["title"])}</b> {T(e["long"])}</li>' for e in self.of("access", "rule"))
        extra = []
        for e in self.of("access"):
            if e["id"] in ("access-keys", "access-request-model") or e["kind"] == "rule":
                continue
            if e.get("rows"):
                body = "".join(f"<h4{' style=\"margin-top:16px\"' if i else ''}>{T(r['label'])}</h4><p>{T(r['text'])}</p>" for i, r in enumerate(e["rows"]))
            else:
                body = paras(e.get("long", ""))
            extra.append(f'<div class="ex" {self.anchor(e)}><div class="lbl">{T(e["title"])}</div>{body}{self.meta(e)}</div>')
        return f"""<section id="keys"><p class="eyebrow q">Access</p><h2 {self.anchor(head)}>{T(head["title"])}</h2>
<p><b>{T(head["short"])}</b></p>{paras(head["long"])}{self.meta(head)}
<div class="ex" {self.anchor(model)}><div class="lbl">{T(model["title"])}</div>{paras(model["long"])}{self.meta(model)}</div>
<h3 style="margin:26px 0 14px">Writing about access</h3>
<ol class="method">{rules}</ol>
{"".join(extra)}</section>"""

    def proof(self) -> str:
        launch = [e for e in self.of("proof", "proof", "proof-") if e.get("release") == "launch"]
        held = [e for e in self.of("proof", "proof", "proof-") if e.get("release") != "launch"]

        def item(e: dict) -> str:
            q = f' <span class="dim">{T(e["qualifier"])}</span>' if e.get("qualifier") else ""
            return f'<div class="pp" {self.anchor(e)}><p><b>{T(e["title"])}</b> {T(e["long"])}{q}</p>{self.meta(e)}</div>'

        rule = self.ids.get("rule-no-competitors")
        return f"""<section id="proof"><p class="eyebrow q">Proof points</p><h2>Stated so they survive a rebuttal</h2>
<div class="grid g2"><div class="panel"><h3>Released at launch</h3>{"".join(item(e) for e in launch)}</div>
<div class="panel held"><h3>Held for their gate</h3>{"".join(item(e) for e in held)}</div></div>
<p class="note" style="margin-top:20px">{T(rule["long"]) if rule else ""}</p></section>"""

    def buyers(self) -> str:
        panels = "".join(
            f'<div class="panel" {self.anchor(e)}><p class="card-n">Hypothetical, not a testimonial</p><h3>{T(e["title"].split(", ", 1)[-1].capitalize())}</h3><p>{T(e["short"])}</p>{self.meta(e)}</div>'
            for e in self.of("proof", "proof", "buyer-"))
        demo = self.ids["demo-walkthrough"]
        return f"""<section id="buyers"><p class="eyebrow q">Buyers</p><h2>What each reader should be able to say</h2>
<p>These statements are hypothetical. They describe the outcome a reader should reach, and no person or company said them.</p>
<div class="grid g2">{panels}</div>
<div class="ex" {self.anchor(demo)}><div class="lbl">{T(demo["title"])}</div>{paras(demo["long"])}{self.meta(demo)}</div></section>"""

    def cards(self) -> str:
        parts = []
        labels = dict(GROUPS)
        for g in CARD_GROUPS:
            panels = []
            for e in self.of(g):
                if e["kind"] == "glossary":
                    panels.append(f'<div class="panel" {self.anchor(e)}><p class="card-n">Definition</p><h3>{T(e["title"])}</h3>{paras(e["long"])}{self.meta(e)}</div>')
                    continue
                cls = "panel held" if e.get("release") == "held" or e["status"] != "approved" else "panel"
                q = f'<p class="note">{T(e["qualifier"])}</p>' if e.get("qualifier") else ""
                panels.append(f'<div class="{cls}" {self.anchor(e)}><p class="card-n">Card {T(e.get("order", ""))}</p><h3>{T(e["title"])}</h3>'
                              f'<p>{T(e["short"])}</p><details><summary>Long copy</summary>{paras(e["long"])}</details>'
                              f'<p><span class="action">{T(e["cta"])}</span></p>{q}{self.meta(e)}</div>')
            parts.append(f'<h3 class="group" id="cards-{A(g)}">{T(labels[g])}</h3><div class="grid g2">{"".join(panels)}</div>')
        nav = " ".join(f'<a href="#cards-{A(g)}">{T(labels[g])}</a>' for g in CARD_GROUPS)
        return (f'<section id="cards"><p class="eyebrow q">Feature cards</p><h2>Title, short, long, and action for each feature</h2>'
                f'<p>Cards marked held stay off the site until their gate ships. The definition of done cards belong to the bounded-task group only, never a lead. Jump to {nav}.</p>{"".join(parts)}</section>')

    def held(self) -> str:
        rows = "".join(
            f'<tr><td><a href="#m-{A(e["id"])}">{T(e["title"])}</a></td><td>{T(dict(GROUPS).get(e["_group"], e["_group"]))}</td>'
            f'<td class="mono">{T(", ".join(e.get("gate") or []))}</td><td>{T(e["status"])}</td></tr>'
            for e in sorted((e for e in self.entries if e["status"] != "retired" and e.get("release") == "held"),
                            key=lambda e: (",".join(e.get("gate") or []), e["id"])))
        return f"""<section id="held"><p class="eyebrow q">Held</p><h2>Written, and waiting for a capability</h2>
<p>An entry here stays out of the site, ads, and outreach until every capability in its gate ships. Then its release changes to launch and nothing else moves.</p>
<div class="tw"><table><thead><tr><th>Entry</th><th>Group</th><th>Gate</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div></section>"""

    def ads(self) -> str:
        panels = []
        for e in self.of("ads", "ad"):
            img = ""
            if live(e):
                src = f"ads/{e['brand']}-{slug_of(e)}-square-1080x1080-dark.svg"
                img = f'<img class="adthumb" src="{A(src)}" alt="{A(e["title"])}" loading="lazy" width="1080" height="1080">'
            sub = f'<p>{T(e["subline"])}</p>' if e.get("subline") else ""
            small = " / ".join(x for x in (" ".join(e["short_lines"]), e.get("subshort", "")) if x)
            panels.append(f'<div class="panel{"" if live(e) else " held"}" {self.anchor(e)}>{img}<p class="card-n">{T(e["kicker"])}</p>'
                          f'<h3>{T(e["title"])}</h3>{sub}<p class="dim">300x250: {T(small)}</p><p><span class="action">{T(e["cta"])}</span></p>{self.meta(e)}</div>')
        return (f'<section id="ads"><p class="eyebrow q">Ads</p><h2>Each campaign explains one operator decision</h2>'
                f'<p>The art in <span class="mono">ads/</span> is rendered by <span class="mono">build/build.py</span> from the approved, launch-released entries below, in four sizes on ink and on paper. A short form keeps the scope of its long form. A held campaign is listed and not rendered.</p>'
                f'<div class="grid g2">{"".join(panels)}</div></section>')

    def outreach(self) -> str:
        blocks = []
        for e in self.of("outreach"):
            if e["kind"] == "email":
                head = f'<p><b>Subject:</b> {T(e["title"])}</p>'
                label = f"Sales email, {', '.join(e['audience'])}"
            else:
                head, label = "", e["title"]
            act = f'<p><span class="action">{T(e["cta"])}</span></p>' if e.get("cta") else ""
            blocks.append(f'<div class="ex" {self.anchor(e)}><div class="lbl">{T(label)}</div>{head}{paras(e["long"])}{act}{self.meta(e)}</div>')
        return (f'<section id="outreach"><p class="eyebrow q">Outreach</p><h2>Ask a question the reader can answer</h2>'
                f'<p>Outreach opens with a diagnostic question and offers one walkthrough. It never describes the reader\'s setup, and it carries no names.</p>{"".join(blocks)}</section>')

    def voice(self) -> str:
        pairs = "".join(
            f'<div class="pairwrap" {self.anchor(e)}><p class="lbl">{T(e["title"])}</p><div class="pair"><div class="quoted"><b>Before</b>{T(e["before"])}</div>'
            f'<div class="after"><b>After</b>{T(e["after"])}</div></div>{self.meta(e)}</div>'
            for e in self.of("voice", "pair", "pair-"))
        return f"""<section id="voice"><p class="eyebrow q">Voice</p><h2>A senior engineer who has read the logs</h2>
<p>Plain, specific, unhurried, dry, and honest to the record. It states what the record supports and stops. No exclamation points, no em dashes, no semicolons in customer copy, sentence case headings, and the Oxford comma.</p>
{pairs}</section>"""

    def words(self) -> str:
        groups = "".join(f'<p><b>{T(g)}.</b> {T(", ".join(ts))}.</p>' for g, ts in avoid_groups())
        swaps = "".join(f'<tr {self.anchor(e)}><td class="quoted">{T(e["before"])}</td><td>{T(e["after"])}</td></tr>'
                        for e in self.of("voice", "pair", "word-"))
        return f"""<section id="words"><p class="eyebrow q">Words</p><h2>Use these. Avoid those.</h2>
<div class="grid g2">
<div class="panel"><h3>Use</h3><p><b>First contact.</b> run, request, rule, check, cost, agent, operator, workspace.</p><p><b>Detail pages.</b> mandate, clause, frame, seal, export, witness, verdict, dod, each defined where it first appears.</p><p><b>Verbs.</b> ask, request, allow, deny, route, answer, record, read, show.</p><p class="dim">See <a href="#m-rule-first-contact-vocabulary">the first contact rule</a>.</p></div>
<div class="panel quoted"><h3>Avoid</h3>{groups}</div>
</div>
<div class="tw"><table><thead><tr><th>Instead of</th><th>Write</th></tr></thead><tbody>{swaps}</tbody></table></div>
<p class="note">The avoid lists are read from <span class="mono">skills/oxagen-branding/references/words.md</span>, the same lists the check enforces.</p></section>"""

    def examples(self) -> str:
        docs, ui = self.ids["docs-writing-a-rule"], self.ids["ui-strings-access"]
        rows = "".join(f'<tr><td>{T(r["label"])}</td><td class="mono">{T(r["text"])}</td></tr>' for r in ui["rows"])
        return f"""<section id="examples"><p class="eyebrow q">Example prose</p><h2>Finished copy per surface</h2>
<div class="ex" {self.anchor(docs)}><div class="lbl">Docs, writing a rule</div><h4>{T(docs["title"])}</h4>{paras(docs["long"])}{self.meta(docs)}</div>
<div class="ex" {self.anchor(ui)}><div class="lbl">{T(ui["title"])}</div><div class="tw" style="margin:0"><table><tbody>{rows}</tbody></table></div>{self.meta(ui)}</div>
<p class="note" style="margin-top:20px">The pages above are examples, not a script. Product names in them are placeholders.</p></section>"""

    def rules(self) -> str:
        items = []
        for e in self.of("rules", "rule"):
            if e["id"] == PROSPECT_RULE:
                ph = '<span class="dim"> The marker list lives in its YAML file and is not reproduced here.</span>'
            elif e.get("phrases"):
                ph = f'<span class="quoted dim"> Blocked in live copy: {T(" / ".join(e["phrases"]))}.</span>'
            else:
                ph = ""
            items.append(f'<li class="quoted" {self.anchor(e)}><b>{T(e["title"])}</b> {T(e["long"])}{ph}{self.meta(e)}</li>')
        frows = "".join(f'<tr id="finding-{A(f["id"])}"><td class="mono">{T(f["id"])}</td><td>{T(f["priority"])}</td><td>{T(f["title"])}</td><td>{T(f["rule"])}</td></tr>'
                        for f in self.findings)
        return f"""<section id="avoid"><p class="eyebrow q">Rules</p><h2>What not to say, and why</h2>
<ol class="method">{"".join(items)}</ol>
<h3 style="margin:30px 0 6px">The review behind the rules</h3>
<p>The adversarial messaging review of 2026-09-15 found ten problems. Each entry above and in the registry names the findings that shaped it.</p>
<div class="tw"><table><thead><tr><th>Id</th><th>Priority</th><th>Finding</th><th>Rule it imposes</th></tr></thead><tbody>{frows}</tbody></table></div></section>"""

    def retired(self) -> str:
        rows = "".join(
            f'<tr class="quoted" {self.anchor(e)}><td>{T(e["title"])}</td><td>{T(e["kind"])}</td><td>{self.link(e.get("replaced_by"))}</td>'
            f'<td>{", ".join(f"<a href=\"#finding-{A(f)}\">{T(f)}</a>" for f in e["findings"])}</td><td class="dim">{T(e.get("notes", ""))}</td></tr>'
            for e in self.of("retired"))
        return f"""<section id="retired"><p class="eyebrow q">Retired</p><h2>No longer used, and what replaced each line</h2>
<p>The check fails if a retired line reappears in an approved entry. Each row quotes the line as it was, so the table is exempt from the word checks.</p>
<div class="tw"><table><thead><tr><th>Retired line</th><th>Kind</th><th>Replaced by</th><th>Findings</th><th>Notes</th></tr></thead><tbody>{rows}</tbody></table></div></section>"""

    def render(self) -> str:
        body = "\n".join([
            self.hero(), self.claim(), self.lines(), self.pitch(), self.sections(), self.entry_points(), self.keys(),
            self.proof(), self.buyers(), self.cards(), self.held(), self.ads(), self.outreach(), self.voice(),
            self.words(), self.examples(), self.rules(), self.retired(),
        ])
        nav = "".join(f'<a href="#{a}">{T(label)}</a>' for a, label in NAV)
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light">
<title>Oxagen message bank</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap">
<style>
{BANK_CSS}{EXTRA_CSS}</style>
</head>
<body>
<!-- GENERATED by build/messages.py from messages/. Do not edit. -->
<header class="top"><div class="wrap"><div class="bar">{WORDMARK}<span class="tag">message bank &middot; generated from messages/</span></div>
<nav class="sub">{nav}</nav></div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap"><p style="margin:0">Oxagen message bank. Generated by <span class="mono">build/messages.py</span> from <span class="mono">messages/</span>, following the messaging review of 2026-09-15.</p></div></footer>
</body>
</html>
"""


NAV = (("claim", "Claim"), ("lines", "Lines"), ("pitch", "Pitch"), ("sections", "Sections"), ("entry-points", "Entry points"),
       ("keys", "Access"), ("proof", "Proof points"), ("buyers", "Buyers"), ("cards", "Cards"), ("held", "Held"),
       ("ads", "Ads"), ("outreach", "Outreach"), ("voice", "Voice"), ("words", "Words"), ("examples", "Examples"),
       ("avoid", "Rules"), ("retired", "Retired"))

EXTRA_CSS = """
.badge{display:inline-block;font-family:var(--mono);font-size:11px;line-height:1.5;padding:1px 7px;border-radius:6px;border:1px solid var(--border);color:var(--muted);margin:0 6px 6px 0;white-space:nowrap}
.badge.launch{color:var(--st-allowed);border-color:var(--st-allowed)}
.badge.held{color:var(--st-approval);border-color:var(--st-approval)}
.badge.candidate{border-style:dashed;color:var(--fg)}
.badge.retired{color:var(--st-denied);border-color:var(--st-denied)}
.badge.id{color:var(--dim)}
.meta{margin-top:12px;font-size:13px;color:var(--muted)}
.meta details summary{padding:2px 0;font-size:12.5px;font-weight:500;color:var(--muted)}
.meta dl{display:grid;grid-template-columns:minmax(90px,max-content) 1fr;gap:4px 14px;margin:8px 0 0}
.meta dt{color:var(--dim);font-size:12px}
.meta dd{margin:0;color:var(--body);font-size:13px}
.panel.held{border-style:dashed}
.panel details summary{font-size:13.5px;padding:4px 0}
.card-n{font-family:var(--mono);font-size:11px;color:var(--dim);margin:0 0 6px;letter-spacing:.04em}
.dim{color:var(--muted)}
.pp{border-top:1px solid var(--border);padding-top:12px;margin-top:12px}
.pp:first-of-type{border-top:0;padding-top:0}
.pairwrap{margin:22px 0}
.pairwrap .lbl{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);font-weight:600;margin:0 0 4px}
.pairwrap .pair{margin:6px 0 4px}
h3.group{margin:30px 0 14px;font-size:19px}
img.adthumb{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--border);margin-bottom:12px}
ol.method li .meta{margin-top:6px}
@media(max-width:640px){.meta dl{grid-template-columns:1fr}.g2{grid-template-columns:1fr}}
"""

BANK_CSS = r""":root{
  --ink:#10100F; --void:#0A0A09; --panel:#181715; --hl:#201F1C; --border:#292722; --rule:#34322D;
  --fg:#F2EEE5; --body:#DDD8CD; --muted:#9B958A; --dim:#6E6A62;
  --gold:#D6962C; --gold-bright:#F1C364; --gold-deep:#8B5E1A; --accent-text:#D6962C; --on-gold:#10100F;
  --st-allowed:#57A97C; --st-approval:#5B93D6; --st-denied:#C66A4A;
  --st-proven:#3FA2A2; --st-failed:#C0453C; --st-critical:#D6455E;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --font:"Space Grotesk","Helvetica Neue",Arial,sans-serif;
}
@media(prefers-color-scheme:light){:root:not([data-theme="dark"]){
  --ink:#F2EEE5; --void:#E9E3D8; --panel:#F8F5EE; --hl:#EFEAE0; --border:#D8CDBD; --rule:#C9BFAE;
  --fg:#10100F; --body:#2A2823; --muted:#6B665C; --dim:#8C877C; --accent-text:#8B5E1A;
  --st-allowed:#2F7D52; --st-approval:#2E6BA8; --st-denied:#9B4526;
  --st-proven:#1F7676; --st-failed:#992F28; --st-critical:#AE2540;
}}
:root[data-theme="light"]{
  --ink:#F2EEE5; --void:#E9E3D8; --panel:#F8F5EE; --hl:#EFEAE0; --border:#D8CDBD; --rule:#C9BFAE;
  --fg:#10100F; --body:#2A2823; --muted:#6B665C; --dim:#8C877C; --accent-text:#8B5E1A;
  --st-allowed:#2F7D52; --st-approval:#2E6BA8; --st-denied:#9B4526;
  --st-proven:#1F7676; --st-failed:#992F28; --st-critical:#AE2540;
}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--ink);color:var(--body);font-family:var(--font);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
@media(prefers-reduced-motion:reduce){*{animation-duration:.001ms!important;transition-duration:.001ms!important}}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:4px}
a{color:var(--accent-text);text-decoration:none;border-bottom:1px solid transparent}
a:hover{border-bottom-color:currentColor}
h1,h2,h3{margin:0;color:var(--fg);letter-spacing:-.02em;text-wrap:balance}
h1{font-size:clamp(30px,5vw,46px);font-weight:700;line-height:1.05}
h2{font-size:24px;font-weight:600;line-height:1.15}
h3{font-size:16px;font-weight:600}
p{margin:0 0 14px;max-width:70ch}
code{font-family:var(--mono);font-size:.88em;background:var(--hl);padding:1px 5px;border-radius:4px}
pre{font-family:var(--mono);font-size:12.5px;line-height:1.55;background:var(--void);color:var(--body);border:1px solid var(--border);padding:16px 18px;border-radius:12px;overflow:auto;margin:0;tab-size:2}
pre code{background:none;padding:0;font-size:inherit;color:inherit}
.file{font-family:var(--mono);font-size:11.5px;color:var(--dim);margin:18px 0 6px}
.mono{font-family:var(--mono);font-size:.9em}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent-text);font-weight:600;margin:0 0 12px}
.eyebrow.q{color:var(--muted)}
.wrap{max-width:1120px;margin:0 auto;padding-inline:24px}
header.top{border-bottom:1px solid var(--rule);padding-block:26px 0;position:sticky;top:0;background:var(--ink);z-index:5}
header.top .bar{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding-bottom:14px}
header.top svg{height:21px;width:auto;color:var(--fg);display:block}
header.top .tag{margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--dim)}
nav.sub{display:flex;gap:16px;overflow-x:auto;padding-bottom:14px;font-size:13.5px;scrollbar-width:none}
nav.sub::-webkit-scrollbar{display:none}
nav.sub a{color:var(--muted);white-space:nowrap;border-bottom:none}
nav.sub a:hover{color:var(--fg)}
.btn{font-family:var(--font);font-weight:600;font-size:13.5px;border:1px solid var(--border);border-radius:8px;padding:8px 13px;cursor:pointer;white-space:nowrap;color:var(--fg);background:transparent}
.btn:hover{border-color:var(--rule);background:var(--hl)}
.btn.primary{background:var(--gold);color:var(--on-gold);border-color:var(--gold-deep)}
.btn.primary:hover{background:var(--gold-bright)}
.btn[data-done="1"]{background:var(--st-allowed);border-color:var(--st-allowed);color:var(--ink)}
.hero{padding-block:52px 46px}
.hero .lead{font-size:19px;line-height:1.5;color:var(--fg);max-width:60ch;margin-top:18px}
.hero-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}
section{padding-block:44px;border-top:1px solid var(--border)}
.grid{display:grid;gap:16px}
.g3{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:17px 19px}
.panel h3{margin-bottom:9px}
.panel p:last-child{margin-bottom:0}
.tw{overflow-x:auto;border:1px solid var(--border);border-radius:12px;background:var(--panel);margin-block:20px}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:640px}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--border);vertical-align:top}
th{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);font-weight:600;white-space:nowrap;background:var(--hl)}
tr:last-child td{border-bottom:0}
ol.method{counter-reset:m;list-style:none;padding:0;margin:0;display:grid;gap:14px}
ol.method li{counter-increment:m;padding-left:42px;position:relative}
ol.method li::before{content:counter(m);position:absolute;left:0;top:1px;width:27px;height:27px;border-radius:8px;
  background:var(--hl);border:1px solid var(--rule);color:var(--fg);font-family:var(--mono);font-size:12px;
  font-weight:700;display:grid;place-items:center}
ol.method b{color:var(--fg)}
.note{border-left:2px solid var(--rule);padding:3px 0 3px 14px;color:var(--muted);font-size:14px;max-width:66ch}
.loop{display:grid;grid-template-columns:1fr;gap:0;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--panel);margin-top:30px}
.loop div{padding:14px 16px;border-bottom:1px solid var(--border);font-size:14px}
.loop div:last-child{border-bottom:0}
.loop b{display:block;color:var(--fg);font-family:var(--mono);font-size:12px;margin-bottom:3px}
@media(min-width:900px){.loop{grid-template-columns:repeat(5,1fr)}.loop div{border-bottom:0;border-right:1px solid var(--border)}.loop div:last-child{border-right:0}}
.verdicts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:16px}
.verdicts .v{border:1px solid var(--border);border-radius:12px;padding:14px 16px;background:var(--panel)}
.verdicts .v b{display:block;font-family:var(--mono);font-size:13px;color:var(--fg);margin-bottom:6px}
.verdicts .v.held{border-style:double;border-width:3px}
.verdicts .v.signed{border-style:dashed}
.verdicts .v.rejected{border-style:solid}
.phase{border-top:1px solid var(--border);padding:20px 0}
.phase:first-child{border-top:0}
.phase h3{margin-bottom:8px}
.phase .gate{font-size:14.5px;background:var(--hl);border:1px solid var(--border);border-radius:8px;padding:10px 12px;margin-top:10px}
.phase .gate b{color:var(--fg)}
.promptbox{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px}
.promptbox .top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.promptbox pre{max-height:440px}
details summary{cursor:pointer;font-weight:600;padding:10px 0;color:var(--fg)}
footer{border-top:1px solid var(--rule);padding-block:34px 70px;color:var(--muted);font-size:13px}
.toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(20px);background:var(--panel);border:1px solid var(--border);color:var(--fg);padding:10px 16px;border-radius:8px;font-size:13.5px;opacity:0;transition:opacity .2s,transform .2s;pointer-events:none}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
@media(max-width:640px){h1{font-size:27px}.hero .lead{font-size:16.5px}}

.ex{border:1px solid var(--border);border-radius:12px;background:var(--panel);padding:20px 22px;margin:14px 0}
.ex .lbl{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);font-weight:600;margin-bottom:10px}
.ex h4{margin:0 0 8px;font-size:22px;letter-spacing:-.02em;color:var(--fg);line-height:1.1}
.ex p{margin:0 0 8px}.ex p:last-child{margin:0}
.ex .action{display:inline-block;margin-top:8px;font-weight:600;font-size:13.5px;border:1px solid var(--border);border-radius:8px;padding:7px 12px;color:var(--fg)}
.pair{display:grid;grid-template-columns:1fr;gap:12px;margin:12px 0 20px}@media(min-width:760px){.pair{grid-template-columns:1fr 1fr}}
.pair div{border:1px solid var(--border);border-radius:12px;padding:14px 16px;background:var(--panel);font-size:14.5px}
.pair b{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin-bottom:6px}
.pair .after{border-style:double;border-width:3px}
"""
WORDMARK = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 574.244 106.313" role="img" aria-label="oxagen"><g transform="translate(0,0) scale(2.842952)"><path d="M6.300 0.000L12.600 3.320L12.600 9.960L6.300 13.280L0.000 9.960L0.000 3.320ZM1.000 3.885L1.000 9.395L6.300 12.150L11.600 9.395L11.600 3.885L6.300 1.130Z M19.376 0.000L25.676 3.320L25.676 9.960L19.376 13.280L13.076 9.960L13.076 3.320ZM14.076 3.885L14.076 9.395L19.376 12.150L24.676 9.395L24.676 3.885L19.376 1.130Z M12.838 10.240L19.138 13.560L19.138 20.200L12.838 23.520L6.538 20.200L6.538 13.560ZM7.538 14.125L7.538 19.635L12.838 22.390L18.138 19.635L18.138 14.125L12.838 11.370Z M19.376 20.480L25.676 23.800L25.676 30.440L19.376 33.760L13.076 30.440L13.076 23.800ZM14.076 24.365L14.076 29.875L19.376 32.630L24.676 29.875L24.676 24.365L19.376 21.610Z" fill="currentColor"/><path d="M25.914 10.240L32.214 13.560L32.214 20.200L25.914 23.520L19.614 20.200L19.614 13.560Z M6.300 20.480L12.600 23.800L12.600 30.440L6.300 33.760L0.000 30.440L0.000 23.800Z" fill="#D6962C"/></g><g transform="translate(120.376,13.067)"><path d="M33.9083 68.758Q24.1657 68.758 16.4786 64.7737Q8.79142 60.7894 4.39571 53.2965Q0 45.8035 0 35.3862V33.3718Q0 22.9544 4.39571 15.4615Q8.79142 7.96854 16.4786 3.98427Q24.1657 0 33.9083 0Q43.6509 0 51.3381 3.98427Q59.0252 7.96854 63.4209 15.4615Q67.8166 22.9544 67.8166 33.3718V35.3862Q67.8166 45.8035 63.4209 53.2965Q59.0252 60.7894 51.3381 64.7737Q43.6509 68.758 33.9083 68.758ZM33.9083 55.3486Q42.1895 55.3486 47.4689 50.0198Q52.7484 44.691 52.7484 35.0142V33.7437Q52.7484 24.067 47.5233 18.7382Q42.2981 13.4094 33.9083 13.4094Q25.6502 13.4094 20.3592 18.7382Q15.0683 24.067 15.0683 33.7437V35.0142Q15.0683 44.691 20.3592 50.0198Q25.6502 55.3486 33.9083 55.3486Z M176.569 68.758Q169.637 68.758 164.119 66.3453Q158.601 63.9327 155.387 59.2935Q152.173 54.6542 152.173 48.0088Q152.173 41.3403 155.387 36.8558Q158.601 32.3712 164.27 30.1017Q169.94 27.8323 177.174 27.8323H196.047V23.8925Q196.047 18.7316 192.874 15.5274Q189.701 12.3232 182.99 12.3232Q176.411 12.3232 173.049 15.3842Q169.686 18.4452 168.627 23.3593L154.691 18.7315Q156.27 13.6133 159.748 9.39702Q163.225 5.18071 169.049 2.59035Q174.874 0 183.208 0Q195.972 0 203.326 6.42816Q210.681 12.8563 210.681 24.9392V50.4707Q210.681 54.4204 214.368 54.4204H219.795V66.9148H209.197Q204.464 66.9148 201.442 64.5334Q198.42 62.1521 198.42 58.1563V57.8864H196.126Q195.392 59.6967 193.399 62.2985Q191.406 64.9004 187.388 66.8292Q183.369 68.758 176.569 68.758ZM179.05 56.4348Q186.581 56.4348 191.314 52.1592Q196.047 47.8837 196.047 40.6031V39.2405H178.175Q173.175 39.2405 170.208 41.3881Q167.241 43.5358 167.241 47.5513Q167.241 51.5668 170.34 54.0008Q173.439 56.4348 179.05 56.4348Z M227.767 34.6423V32.6279Q227.767 22.3817 231.86 15.0863Q235.953 7.79081 242.768 3.8954Q249.582 0 257.706 0Q266.935 0 271.762 3.33256Q276.589 6.66512 278.81 10.4107H281.042V1.8432H295.801V79.33Q295.801 85.6989 292.104 89.4725Q288.408 93.2462 282.079 93.2462H238.369V80.0541H277.023Q280.779 80.0541 280.779 76.1043V57.2775H278.547Q277.161 59.5683 274.665 61.8904Q272.168 64.2125 268.057 65.7414Q263.946 67.2702 257.706 67.2702Q249.582 67.2702 242.756 63.3748Q235.93 59.4794 231.848 52.1724Q227.767 44.8655 227.767 34.6423ZM261.938 54.0781Q270.151 54.0781 275.573 48.8612Q280.996 43.6443 280.996 34.2704V32.9999Q280.996 23.4943 275.627 18.3432Q270.259 13.1921 261.938 13.1921Q253.749 13.1921 248.315 18.3432Q242.881 23.4943 242.881 32.9999V34.2704Q242.881 43.6443 248.315 48.8612Q253.749 54.0781 261.938 54.0781Z M344.764 68.758Q334.998 68.758 327.583 64.6108Q320.167 60.4636 316.031 52.9048Q311.896 45.346 311.896 35.1689V33.589Q311.896 23.3889 315.977 15.8416Q320.059 8.2944 327.397 4.1472Q334.735 0 344.385 0Q353.881 0 360.956 4.1867Q368.031 8.37341 371.981 15.8515Q375.931 23.3297 375.931 33.2895V38.6974H327.181Q327.468 46.3334 332.587 50.9496Q337.707 55.5658 345.198 55.5658Q352.522 55.5658 356.101 52.3534Q359.681 49.141 361.553 45.0629L373.985 51.4813Q372.119 55.0656 368.63 59.1042Q365.141 63.1428 359.394 65.9504Q353.648 68.758 344.764 68.758ZM327.313 27.2892H360.622Q360.095 20.7986 355.7 16.9954Q351.304 13.1921 344.277 13.1921Q337.055 13.1921 332.691 16.9954Q328.327 20.7986 327.313 27.2892Z M391.548 66.9148V1.8432H406.353V10.9769H408.585Q410.303 7.25429 414.832 3.99908Q419.361 0.743866 428.435 0.743866Q435.956 0.743866 441.695 4.12911Q447.434 7.51435 450.651 13.5903Q453.868 19.6663 453.868 27.9442V66.9148H438.8V29.1226Q438.8 21.1969 434.891 17.3492Q430.983 13.5015 423.9 13.5015Q415.872 13.5015 411.244 18.8237Q406.617 24.146 406.617 33.9445V66.9148Z" fill="currentColor"/><path d="M73.9979 66.9148 98.2261 34.0696 74.3764 1.8432H91.9626L107.9 24.3499H110.131L126.068 1.8432H143.654L119.805 34.0696L144.033 66.9148H126.206L110.131 44.0065H107.9L91.8244 66.9148Z" fill="#D6962C"/></g></svg>"""


def render_index(entries: list[dict], findings: list[dict]) -> str:
    payload = {
        "source": "messages/",
        "generated_by": "build/messages.py",
        "counts": {
            "entries": len(entries),
            "status": dict(sorted(Counter(e["status"] for e in entries).items())),
            "release": dict(sorted(Counter(e.get("release") for e in entries if e["status"] != "retired").items())),
            "group": {g: sum(1 for e in entries if e["_group"] == g) for g, _ in GROUPS},
        },
        "findings": findings,
        "entries": [public(e) for e in sorted(entries, key=lambda e: e["id"])],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------- page checks

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _PageReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.problems: list[str] = []
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.text: list[str] = []
        self.plain: list[str] = []  # text outside .quoted
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href", "").startswith("#"):
            self.hrefs.append(a["href"][1:])
        if tag in VOID:
            return
        quoted = "quoted" in (a.get("class") or "").split()
        self.stack.append((tag, quoted))
        if tag in ("style", "script", "svg"):
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.problems.append(f"unbalanced </{tag}> (open: {self.stack[-1][0] if self.stack else 'nothing'})")
            return
        self.stack.pop()
        if tag in ("style", "script", "svg"):
            self.skip -= 1

    def handle_data(self, data):
        if self.skip:
            return
        self.text.append(data)
        if not any(q for _, q in self.stack):
            self.plain.append(data)


def check_page(page: str, entries: list[dict], rendered: set[str]) -> tuple[list[str], dict]:
    r = _PageReader()
    r.feed(page)
    r.close()
    problems = [f"message-bank.html: {p}" for p in r.problems]
    if r.stack:
        problems.append(f"message-bank.html: unclosed tags {[t for t, _ in r.stack]}")
    dupes = [i for i, n in Counter(r.ids).items() if n > 1]
    if dupes:
        problems.append(f"message-bank.html: duplicate ids {dupes}")
    ids = set(r.ids)
    missing = sorted({h for h in r.hrefs if h not in ids})
    if missing:
        problems.append(f"message-bank.html: anchors that resolve to nothing: {missing}")
    text, plain = " ".join(r.text), " ".join(r.plain)
    for p in prose_problems(text):
        problems.append(f"message-bank.html: page text has {p}")
    terms, _ = avoid_terms()
    flat = plain.replace("’", "'")
    context = Counter()
    for term, qualified, _g in terms:
        n = len(_pattern(term, case=False).findall(flat))
        if n and qualified:
            context[term] += n
        elif n:
            problems.append(f"message-bank.html: page prose uses the avoided word {term!r}")
    claims, prospects = blocklists(entries)
    for ph, rid in claims:
        if phrase_hits(plain, [ph]):
            problems.append(f"message-bank.html: page prose uses {ph!r}, blocked by {rid}")
    for ph in phrase_hits(text, prospects):
        problems.append(f"message-bank.html: page carries a prospect or deal marker ({ph!r})")
    unrendered = sorted(e["id"] for e in entries if e["id"] not in rendered)
    if unrendered:
        problems.append(f"message-bank.html: entries not on the page: {unrendered}")
    stats = {"elements_with_id": len(ids), "anchors": len(r.hrefs), "anchors_unresolved": len(missing),
             "em_en_dashes": len(DASHES.findall(text)), "exclamation_points": text.count("!"),
             "context_words": dict(sorted(context.items()))}
    return problems, stats


# ---------------------------------------------------------------------------- main


def summary(entries: list[dict]) -> str:
    def row(label: str, c: Counter | dict) -> str:
        return f"  {label:<8} " + " · ".join(f"{k} {v}" for k, v in c.items())

    groups = {g: sum(1 for e in entries if e["_group"] == g) for g, _ in GROUPS}
    status = Counter(e["status"] for e in entries)
    release = Counter(e.get("release") for e in entries if e["status"] != "retired")
    camp = ad_campaigns(entries)
    lines = [
        f"registry: {len(entries)} entries in {sum(1 for v in groups.values() if v)} groups",
        row("status", dict(sorted(status.items()))),
        row("release", dict(sorted(release.items()))),
        row("groups", groups),
        "  ads      " + " · ".join(f"{b}: {', '.join(str(c['slug']) for c in camp[b])}" for b in BRANDS),
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate, write nothing")
    ap.add_argument("--verbose", action="store_true", help="list every warning")
    ap.add_argument("--stats", type=Path, help="write the page check statistics as JSON to this path")
    args = ap.parse_args()

    entries, findings = load(), load_findings()
    errors, warnings, context = validate(entries, findings)
    print(summary(entries))
    if errors:
        for e in errors:
            print("problem:", e)
        sys.exit(f"\n{len(errors)} problems in the registry; nothing written")

    page_obj = Page(entries, findings)
    page = page_obj.render()
    index = render_index(entries, findings)
    page_problems, stats = check_page(page, entries, page_obj.rendered)
    problems = list(page_problems)
    if args.stats:
        args.stats.write_text(json.dumps(stats, indent=2) + "\n")

    if args.check:
        if not BANK.exists() or BANK.read_text() != page:
            problems.append("message-bank.html is out of date with messages/; run python3 build/messages.py")
        if not INDEX.exists() or INDEX.read_text() != index:
            problems.append("messages/index.json is out of date with messages/; run python3 build/messages.py")
    elif not page_problems:
        BANK.write_text(page)
        INDEX.write_text(index)
        print(f"wrote {BANK.relative_to(ROOT)} ({len(page) // 1024} KB) and {INDEX.relative_to(ROOT)}")
    problems += check_ads_on_disk(entries)

    context_note = [w for w in warnings if "allows only in context" in w]
    other = [w for w in warnings if w not in context_note]
    for w in other:
        print("warn:", w)
    if context:
        top = ", ".join(f"{k} x{v}" for k, v in context.most_common())
        print(f"warn: {len(context_note)} uses of words words.md allows only in context ({top}); read them in place")
        if args.verbose:
            for w in context_note:
                print("  ", w)
    print(f"page: {stats['elements_with_id']} anchors defined, {stats['anchors']} links, {stats['anchors_unresolved']} unresolved, "
          f"{stats['em_en_dashes']} em or en dashes, {stats['exclamation_points']} exclamation points")
    for p in problems:
        print("problem:", p)
    if problems:
        sys.exit(f"\n{len(problems)} problems")
    print("check: ok" if args.check else "messages: ok")


if __name__ == "__main__":
    main()
