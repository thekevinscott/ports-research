from datetime import UTC, datetime
from secrets import token_hex

TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"
TOKEN_BYTES = 4


def run_directory_name(timestamp: datetime) -> str:
    """Name one run's output directory.

    Basic-format UTC so the name sorts lexically in chronological order and
    carries no colons, which are not portable in filenames. The random tail
    separates two runs inside the same second.
    """
    stamp = timestamp.astimezone(UTC).strftime(TIMESTAMP_FORMAT)
    return f"{stamp}_{token_hex(TOKEN_BYTES)}"
