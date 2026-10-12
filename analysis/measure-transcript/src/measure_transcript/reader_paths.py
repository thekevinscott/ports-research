READERS = {"cat", "head", "tail", "less", "grep", "sed", "awk"}
# Options whose value is the next word.
VALUE_OPTIONS = {
    "head": {"-n", "-c"},
    "tail": {"-n", "-c"},
    "grep": {"-e", "-f", "-A", "-B", "-C", "-m"},
    "sed": {"-e", "-f"},
    "awk": {"-F", "-f", "-v"},
}
# grep's, sed's and awk's first operand is a pattern or a script, unless one is given by -e or -f.
SCRIPT_FIRST = {"grep", "sed", "awk"}
SCRIPT_OPTIONS = {"-e", "-f"}


def reader_paths(program: str, args: list[str]) -> list[str] | None:
    """The file operands of a reading command, `args` being the words after its program; None for a command that reads no file.

    The readers are `cat`, `head`, `tail`, `less`, `grep`, `awk`, and `sed -n`.
    """
    if program not in READERS or (program == "sed" and "-n" not in args):
        return None
    operands, script_given, value_next = [], False, False
    for word in args:
        if value_next:
            value_next = False
        elif word in VALUE_OPTIONS.get(program, ()):
            value_next = True
            script_given = script_given or word in SCRIPT_OPTIONS
        elif not word.startswith("-"):
            operands.append(word)
    return operands[1:] if program in SCRIPT_FIRST and not script_given else operands
