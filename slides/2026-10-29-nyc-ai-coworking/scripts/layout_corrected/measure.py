import json, subprocess, sys
REF = "/home/duncan/.cache/ports/analysis/codebases/reference/13f1aca495d11e160fffd68c4ba299a2415909d8/packages/gbnf"
RT = "/home/duncan/work/code/research/ports/.worktrees/notebook-v2-rerun/analysis/round-trip-experiment"
EXCLUDE = ["node_modules","__pycache__",".venv",".pytest_cache","dist","dev-deps","tests","test","integration-tests","conftest.py","*_test.py","test_*.py","*.test.ts","*.spec.ts","*_test.ts"]
EXC = {"python": EXCLUDE, "javascript": [*EXCLUDE, "builder", "dev"]}
DRIVERS = {"python": "python", "javascript": "typescript"}
def cmd(lang, port):
    args = ["uv","run","--frozen","measure-code-distance","git-diff","--language",DRIVERS[lang],"--a",f"{REF}/{lang}","--b",str(port)]
    for p in EXC[lang]: args += ["--exclude", p]
    return args
def measure(lang, port):
    p = subprocess.run(cmd(lang, port), cwd=RT, capture_output=True, text=True, env={**__import__("os").environ, "UV_NO_CONFIG": "1"})
    try: return json.loads(p.stdout)["similarity_pct"]
    except Exception: raise RuntimeError(p.stderr[-2000:])
if __name__ == "__main__":
    print(measure(sys.argv[1], sys.argv[2]))
