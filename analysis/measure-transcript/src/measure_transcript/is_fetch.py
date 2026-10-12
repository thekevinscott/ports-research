import posixpath

from measure_transcript.command_word import command_word


def is_fetch(words: list[str]) -> bool:
    """curl, wget, `pip install` (also as `pip3`, `python -m pip`, `uv pip`) or `npm install`."""
    i = command_word(words)
    program, rest = posixpath.basename(words[i]) if i < len(words) else "", words[i + 1:]
    if program.startswith("python") and rest[:1] == ["-m"]:
        program, rest = rest[1] if len(rest) > 1 else "", rest[2:]
    if program == "uv" and rest[:1] == ["pip"]:
        program, rest = "pip", rest[1:]
    return (
        program in {"curl", "wget"}
        or (program in {"pip", "pip3"} and rest[:1] == ["install"])
        or (program == "npm" and rest[:1] in (["install"], ["i"]))
    )
