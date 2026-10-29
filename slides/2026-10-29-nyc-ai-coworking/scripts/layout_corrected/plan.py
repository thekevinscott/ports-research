import csv, os, json
R="/home/duncan/work/code/research/ports/experiments/v2-models-effort/runs"
C="/home/duncan/work/code/research/ports/.worktrees/talk-2026-10-29/slides/2026-10-29-nyc-ai-coworking/public/models-effort-runs.csv"
SKIP={"node_modules","__pycache__",".venv",".pytest_cache","dist",".git"}
def walk(p):
    for d,dn,fn in os.walk(p):
        dn[:]=sorted(x for x in dn if x not in SKIP)
        yield os.path.relpath(d,p), dn, fn
out=[]
for r in csv.DictReader(open(C)):
    p=f"{R}/{r['run_id']}/ported_implementation"
    lang="python" if r["direction"]=="javascript→python" else "javascript"
    plan=None; note=""
    if lang=="python":
        if os.path.isdir(f"{p}/gbnf"): continue
        c=[d for d,dn,fn in walk(p) if os.path.basename(d)=="gbnf" and "__init__.py" in fn]
        c.sort(key=lambda d:d.count("/"))
        if c and (len(c)==1 or c[0].count("/")<c[1].count("/")): plan=(c[0],"gbnf")
        else: note=f"candidates {c}"
    else:
        if os.path.isfile(f"{p}/src/index.ts"): continue
        c=[d for d,dn,fn in walk(p) if ("index.ts" in fn or "gbnf.ts" in fn) and "test" not in d]
        c.sort(key=lambda d:d.count("/"))
        if c and c[0]=="." and "gbnf" in c:
            plan=("gbnf","src"); note="root index.ts re-export left in place"
        elif c and c[0]!="." and (len(c)==1 or c[0].count("/")<c[1].count("/")): plan=(c[0],"src")
        else: note=f"candidates {c}"
    out.append(dict(run_id=r["run_id"],model=r["model"],effort=r["effort"],direction=r["direction"],lang=lang,before=r["reference_diff_similarity_pct"],plan=plan,note=note))
json.dump(out,open("/tmp/claude/followups-786/plan.json","w"),indent=1)
import collections
print(collections.Counter((o["lang"],str(o["plan"])) for o in out))
for o in out:
    if not o["plan"]: print(o)
