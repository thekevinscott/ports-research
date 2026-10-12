import re

PATH = re.compile(r"(?<![\w.:/~-])/[\w.@+-]+(?:/[\w.@+-]+)*")


def absolute_paths(text: str) -> list[str]:
    """Every absolute path written out in `text`, in order."""
    return PATH.findall(text)
