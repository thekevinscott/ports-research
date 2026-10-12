from hashlib import sha256

SEED = 0


def item_id(content: str) -> str:
    """An opaque id from a seeded hash of the item's content."""
    return "item-" + sha256(f"{SEED}\n{content}".encode()).hexdigest()[:8]
