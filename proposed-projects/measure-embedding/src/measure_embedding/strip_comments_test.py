from measure_embedding.strip_comments import strip_comments

PYTHON = (
    b"# leading\n"
    b"def f(x):\n"
    b'    label = "# not a comment"\n'
    b"    return x  # trailing\n"
)
PYTHON_STRIPPED = (
    b"\n"
    b"def f(x):\n"
    b'    label = "# not a comment"\n'
    b"    return x  \n"
)
TYPESCRIPT = (
    b"// leading\n"
    b"/* block\n"
    b"   comment */\n"
    b"export function f(x: number): string {\n"
    b'  const url = "https://example.com"; // trailing\n'
    b"  return `${x}`; /* inline */\n"
    b"}\n"
)
TYPESCRIPT_STRIPPED = (
    b"\n"
    b"\n"
    b"export function f(x: number): string {\n"
    b'  const url = "https://example.com"; \n'
    b"  return `${x}`; \n"
    b"}\n"
)


def describe_strip_comments():
    def it_removes_python_comments_and_leaves_every_other_byte_in_place():
        assert strip_comments(PYTHON, "python") == PYTHON_STRIPPED

    def it_removes_typescript_line_and_block_comments():
        assert strip_comments(TYPESCRIPT, "typescript") == TYPESCRIPT_STRIPPED

    def it_keeps_a_hash_inside_a_python_string():
        assert strip_comments(b'x = "a # b"\n', "python") == b'x = "a # b"\n'

    def it_keeps_a_double_slash_inside_a_typescript_string():
        assert strip_comments(b'const u = "a // b";\n', "typescript") == b'const u = "a // b";\n'

    def it_returns_source_without_comments_unchanged():
        assert strip_comments(b"a = 1\n\nb = 2\n", "python") == b"a = 1\n\nb = 2\n"

    def it_keeps_a_python_docstring():
        source = b'def f():\n    """doc"""\n    return 1\n'
        assert strip_comments(source, "python") == source
