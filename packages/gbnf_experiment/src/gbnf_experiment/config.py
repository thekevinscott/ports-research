from pathlib import Path
import hashlib

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_ROOT.parents[1]
CACHE_HOME = Path.home() / ".cache"

# The prepared corpus is rebuildable from a pinned commit and the docker context,
# so it is a cache, not evidence, and does not belong in the tree runs are banked in.
PREPARED_DIRECTORY = CACHE_HOME / "ports" / "gbnf-experiment" / "prepared"
ROOT_DIRECTORY = PACKAGE_ROOT
DOCKER_DIRECTORY = PACKAGE_ROOT / "docker"
PREPARE_DOCKER_DIRECTORY = DOCKER_DIRECTORY / "gbnf-prepare"
# The merge of GBNF PR #81: nearest upstream ancestor of the v0 clone's local commits.
GBNF_COMMIT = "13f1aca495d11e160fffd68c4ba299a2415909d8"
# Blank runs on the host's Claude subscription.
API_KEY = ""


def compute_prepare_cache_key(gbnf_commit: str, docker_directory: Path, rules: str) -> str:
    digests = [
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(docker_directory.rglob("*"))
        if path.is_file()
    ]
    rules_digest = hashlib.sha256(rules.encode()).hexdigest()
    return hashlib.sha256("".join([gbnf_commit, *digests, rules_digest]).encode()).hexdigest()[:16]
