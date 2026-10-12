import json
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from measure_api.random_string import random_string

GENERATOR_VERSION = 1
RANDOM_INPUTS = 2


def generate_corpus(*, out: Path, seed: int, count: int) -> None:
    rng = random.Random(seed)
    with tempfile.TemporaryDirectory() as scratch:
        source = Path(scratch)
        # Grammars and their inputs come from measure-behavior's generator, through its CLI.
        subprocess.run(["measure-behavior", "generate", "--out", str(source), "--seed", str(seed), "--count", str(count)], check=True)
        shutil.copytree(source / "grammars", out / "grammars", dirs_exist_ok=True)
        (out / "inputs").mkdir(exist_ok=True)
        for path in sorted((source / "inputs").glob("*.json")):
            drawn = json.loads(path.read_text())
            inputs = list(dict.fromkeys([*drawn, *(random_string(rng) for _ in range(RANDOM_INPUTS))]))
            (out / "inputs" / path.name).write_text(json.dumps(inputs, ensure_ascii=False, indent=1) + "\n")
        upstream = json.loads((source / "manifest.json").read_text())
    manifest = {"seed": seed, "count": count, "generator_version": GENERATOR_VERSION, "measure_behavior": upstream}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
