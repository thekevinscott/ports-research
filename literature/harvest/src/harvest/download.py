import pathlib
import urllib.request


def download(arxiv_id: str, dest: pathlib.Path) -> bool:
    """Fetch an arxiv PDF to dest. False if it is not retrievable as a PDF."""
    req = urllib.request.Request(
        f"https://arxiv.org/pdf/{arxiv_id}", headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except Exception:
        return False
    if not data.startswith(b"%PDF"):
        return False
    dest.write_bytes(data)
    return True
