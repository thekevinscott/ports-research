import csv, os, shutil, sys, fnmatch, statistics as st, collections
sys.path.insert(0,"/tmp/claude/followups-786")
from measure import measure
B="/tmp/claude/followups-786"
rows=list(csv.DictReader(open(f"{B}/layout-corrected.csv")))
issues=[]
for r in rows:
    r["similarity_renamed"]=""
    if r["direction"]!="python→javascript" or float(r["similarity_after"])-float(r["similarity_before"])>=2: continue
    src=f"{B}/relocated/{r['run_id']}"; dst=f"{B}/relocated-renamed/{r['run_id']}"
    if os.path.exists(dst): shutil.rmtree(dst)
    seen={}; dirs=set(); files=0; kept=[]
    for d,dn,fn in os.walk(src):
        for f in fn:
            rel=os.path.relpath(os.path.join(d,f),src)
            if rel.startswith("src/"):
                parts=rel.split("/")
                if fnmatch.fnmatch(parts[-1],"*_test.ts"): kept.append(rel); newf=parts[-1]
                else: newf=parts[-1].lower().replace("_","-")
                newd=[p.lower().replace("_","-") for p in parts[1:-1]]
                for o,n in zip(parts[1:-1],newd):
                    if o!=n: dirs.add(o)
                if newf!=parts[-1]: files+=1
                new="/".join(["src",*newd,newf])
            else: new=rel
            if new in seen: issues.append((r["run_id"],f"collision {seen[new]} / {rel}")); continue
            seen[new]=rel
            os.makedirs(os.path.dirname(f"{dst}/{new}"),exist_ok=True)
            shutil.copy2(os.path.join(d,f),f"{dst}/{new}")
    if kept: issues.append((r["run_id"],f"{len(kept)} *_test.ts names kept so the exclude still applies"))
    r["similarity_renamed"]=round(measure("javascript",dst),3)
    r["relocation"]+=f"; renamed under src/ to kebab-case: {len(dirs)} dir names ({', '.join(sorted(dirs))}), {files} files"
    print(r["run_id"],r["model"],r["similarity_before"],r["similarity_after"],r["similarity_renamed"],flush=True)
with open(f"{B}/layout-corrected.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
g=collections.defaultdict(list)
for r in rows:
    if r["similarity_renamed"]!="": g[r["model"]].append(r)
print("ISSUES",issues)
for m,v in sorted(g.items()):
    print("MED",m,len(v),*[round(st.median(float(x[k]) for x in v),3) for k in ("similarity_before","similarity_after","similarity_renamed")])
