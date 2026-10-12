import json
from hashlib import sha256


def content_hash(prompt: str, model: str, effort: str, tag: str) -> str:
    """What a walkthrough is keyed by: the exact prompt, the model, the effort and the tag that asks for a repeat."""
    return sha256(json.dumps([prompt, model, effort, tag]).encode()).hexdigest()[:16]
