from hashlib import sha256

SEED = 0


def replicate_items(items: list[dict], fraction: float) -> list[dict]:
    """The items to judge a second time: none at fraction 0, otherwise every baseline and each item whose seeded hash of its id falls below the fraction."""

    def below(item_id: str) -> bool:
        return int(sha256(f"{SEED}\nreplicate\n{item_id}".encode()).hexdigest()[:8], 16) / 16**8 < fraction

    return [item for item in items if fraction > 0 and (item["entry"]["baseline"] or below(item["id"]))]
