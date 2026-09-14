#!/usr/bin/env python3
"""Phase 2: (A) title-resolve references in the 54 seeds that lacked an inline arxiv id,
then (B) convert every harvested PDF to markdown.

Precision guard for title resolution: query the arxiv API with the reference text, and accept
a result ONLY if its title (normalized) appears as a substring of the reference (normalized).
That makes false positives near-zero regardless of how noisy the query is.
"""
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

PAPERS = pathlib.Path(__file__).resolve().parent / "papers"
SEEDS = {d.name for d in PAPERS.iterdir() if d.is_dir() and (d / "paper.md").exists()}

INLINE_ID = re.compile(r"arxiv[:\s/]*?(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})", re.I)
REF_HEADING = re.compile(r"(?im)^\s*#*\s*(references|bibliography)\s*$")
ENTRY_START = re.compile(r"^\s*(?:[-*]|\[\d+\]|\d+\.)\s+")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def references_section(md: str) -> str:
    m = list(REF_HEADING.finditer(md))
    return md[m[-1].end():] if m else ""


def split_entries(section: str) -> list[str]:
    lines = [ln for ln in section.splitlines()]
    entries, cur = [], ""
    started = False
    for ln in lines:
        if ENTRY_START.match(ln):
            if cur.strip():
                entries.append(cur.strip())
            cur = ln
            started = True
        elif started:
            cur += " " + ln.strip()
    if cur.strip():
        entries.append(cur.strip())
    # fallback: if no markers found, one entry per non-empty line
    if not entries:
        entries = [ln.strip() for ln in lines if ln.strip()]
    return [e for e in entries if len(e) > 30]


def arxiv_query(ref: str) -> str | None:
    q = re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9 ]", " ", ref)).strip()[:250]
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": f"all:{q}", "max_results": 5}
    )
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            xml = r.read()
    except Exception:
        return None
    nref = norm(ref)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None
    for entry in root.findall("a:entry", ns):
        title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
        idurl = (entry.findtext("a:id", default="", namespaces=ns) or "")
        m = re.search(r"arxiv\.org/abs/([^v\s]+)", idurl)
        if not m or len(norm(title)) < 15:
            continue
        if norm(title) in nref:
            return m.group(1)
    return None


def download(arxiv_id: str, dest: pathlib.Path) -> bool:
    req = urllib.request.Request(f"https://arxiv.org/pdf/{arxiv_id}", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except Exception:
        return False
    if not data.startswith(b"%PDF"):
        return False
    dest.write_bytes(data)
    return True


def phase_a_resolve() -> None:
    have = {d.name for d in PAPERS.iterdir() if d.is_dir()}
    added = checked = 0
    for slug in sorted(SEEDS):
        md = (PAPERS / slug / "paper.md").read_text(errors="ignore")
        for ref in split_entries(references_section(md)):
            if INLINE_ID.search(ref):
                continue  # already handled in phase 1
            checked += 1
            time.sleep(2.0)  # polite to arxiv API
            aid = arxiv_query(ref)
            if not aid or aid in have:
                continue
            target = PAPERS / aid
            target.mkdir(exist_ok=True)
            if download(aid, target / "paper.pdf"):
                (target / "metadata.json").write_text(json.dumps({"source": slug}) + "\n")
                have.add(aid)
                added += 1
            else:
                try:
                    target.rmdir()
                except OSError:
                    pass
        print(f"[A {slug}] checked~{checked} added={added}", flush=True)
    print(f"PHASE A done: title-resolved added={added}, refs_checked={checked}")


def phase_b_convert() -> None:
    import pymupdf4llm
    todo = [d for d in sorted(PAPERS.iterdir()) if d.is_dir() and (d / "paper.pdf").exists() and not (d / "paper.md").exists()]
    ok = fail = 0
    for d in todo:
        try:
            md = pymupdf4llm.to_markdown(str(d / "paper.pdf"), show_progress=False)
            (d / "paper.md").write_text(md)
            ok += 1
        except Exception as e:
            fail += 1
            print("CONVERT FAIL", d.name, repr(e)[:80], flush=True)
        if ok % 25 == 0:
            print(f"  converted {ok}/{len(todo)}", flush=True)
    print(f"PHASE B done: converted={ok} fail={fail} of {len(todo)}")


if __name__ == "__main__":
    phase_a_resolve()
    phase_b_convert()
