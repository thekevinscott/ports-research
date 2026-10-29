import json, os, shutil, sys, csv, statistics
sys.path.insert(0,"/tmp/claude/followups-786")
from measure import measure, cmd
R="/home/duncan/work/code/research/ports/experiments/v2-models-effort/runs"
S="/tmp/claude/followups-786/relocated"
SKIP={"node_modules","__pycache__",".venv",".pytest_cache","dist",".git"}
plan=json.load(open("/tmp/claude/followups-786/plan.json"))
rows=[]; skipped=[]
for o in plan:
    src=f"{R}/{o['run_id']}/ported_implementation"
    pkg,target=o["plan"]
    tops=[x for x in os.listdir(src) if x not in SKIP]
    wrapper=tops[0] if len(tops)==1 and tops[0] in ("python","typescript") and pkg.startswith(tops[0]+"/") else None
    dest=f"{S}/{o['run_id']}"
    if os.path.exists(dest): shutil.rmtree(dest)
    seen=set(); collide=[]
    for d,dn,fn in os.walk(src):
        dn[:]=[x for x in dn if x not in SKIP]
        for f in fn:
            rel=os.path.relpath(os.path.join(d,f),src)
            if rel==pkg or rel.startswith(pkg+"/"): new=target+rel[len(pkg):]
            elif wrapper and rel.startswith(wrapper+"/"): new=rel[len(wrapper)+1:]
            else: new=rel
            if new in seen: collide.append(new); continue
            seen.add(new)
            os.makedirs(os.path.dirname(f"{dest}/{new}"),exist_ok=True)
            shutil.copy2(os.path.join(d,f),f"{dest}/{new}")
    reloc=f"{pkg} → {target}"+(f"; {wrapper}/* → ." if wrapper else "")+(f"; {o['note']}" if o['note'] else "")
    if collide:
        skipped.append((o["run_id"],f"path collisions {collide[:5]}")); continue
    try: after=measure(o["lang"],dest)
    except Exception as e:
        skipped.append((o["run_id"],f"measure failed: {e}")); continue
    rows.append(dict(run_id=o["run_id"],model=o["model"],effort=o["effort"],direction=o["direction"],relocation=reloc,similarity_before=o["before"],similarity_after=round(after,3)))
    print(len(rows),o["run_id"],o["before"],round(after,3),reloc,flush=True)
with open("/tmp/claude/followups-786/layout-corrected.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump(skipped,open("/tmp/claude/followups-786/skipped.json","w"),indent=1)
print("SKIPPED",skipped)
