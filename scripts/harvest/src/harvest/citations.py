"""Harvest arxiv-cited papers from the 54 seed papers.

For each seed paper (papers/<slug>/paper.md), slice the References section, extract inline
arXiv IDs, and download each cited paper to papers/<arxiv-id>/paper.pdf with
metadata.json {"source": "<citing-slug>"}. Arxiv-only: an inline arXiv id is, by definition,
on arxiv. References without an inline id (cited by venue only) are skipped.
"""
import json
import pathlib
import re
import time

from harvest.download import download

# arxiv ids of the 54 seeds (so we don't re-download a seed under an id-named dir).
SEED_IDS = {
    "2505.07425","2602.09944","2512.06902","2604.07341","2504.09691","2511.21878","2411.13990",
    "2509.12087","2404.18852","2412.17744","2504.15254","2605.14634","2510.07604","2605.02195",
    "2501.16050","2602.22518","2602.15761","2502.12466","2506.04019","2505.04852","2412.04590",
    "2407.07472","2501.06972","2308.03109","2507.21954","2509.00256","2507.16037","2510.15004",
    "2601.06497","2006.03511","2110.06773","2505.10708","2405.18574","2501.18460","2602.18534",
    "2509.22202","2604.20202","2605.17535","2603.14054","2602.09930","2604.03986","2411.14971",
    "2505.13004","2406.06864","2507.00057","2603.24774","2411.06145","2606.17683","2605.08247",
    "2310.11476","2602.16106","2510.09898","2509.06504","2508.11468",
}

NEW_ID = re.compile(r"arxiv[:\s/]*?(\d{4}\.\d{4,5})", re.I)
OLD_ID = re.compile(r"arxiv[:\s/]*?([a-z\-]+(?:\.[A-Z]{2})?/\d{7})", re.I)
REF_HEADING = re.compile(r"(?im)^\s*#*\s*(references|bibliography)\s*$")


def references_section(md: str) -> str:
    matches = list(REF_HEADING.finditer(md))
    return md[matches[-1].end():] if matches else md


def ids_in(md: str) -> set[str]:
    refs = references_section(md)
    out = set()
    for m in NEW_ID.finditer(refs):
        out.add(m.group(1))
    for m in OLD_ID.finditer(refs):
        out.add(m.group(1))
    return out


def harvest(papers: pathlib.Path) -> None:
    seeds = sorted(d for d in papers.iterdir() if d.is_dir() and (d / "paper.md").exists())
    have = set(SEED_IDS) | {d.name for d in papers.iterdir() if d.is_dir()}
    downloaded = skipped_have = failed = 0
    for d in seeds:
        cited = ids_in((d / "paper.md").read_text(errors="ignore"))
        cited = {c for c in cited if c not in SEED_IDS}
        for cid in sorted(cited):
            target = papers / cid
            if cid in have or target.exists():
                skipped_have += 1
                continue
            target.mkdir(parents=True, exist_ok=True)
            if download(cid, target / "paper.pdf"):
                (target / "metadata.json").write_text(json.dumps({"source": d.name}) + "\n")
                have.add(cid)
                downloaded += 1
            else:
                # not retrievable as a PDF -> not (usefully) on arxiv; leave no trace
                try:
                    target.rmdir()
                except OSError:
                    pass
                failed += 1
            time.sleep(0.5)  # be polite to arxiv
        print(f"[{d.name}] cited_arxiv={len(cited)}  running_total={downloaded}", flush=True)
    print(f"DONE downloaded={downloaded} already_had={skipped_have} not_found={failed}")
