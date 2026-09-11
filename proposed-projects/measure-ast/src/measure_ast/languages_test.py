from measure_ast.languages import LANGUAGES, PYTHON, TYPESCRIPT


def nodes(spec, suffix, source):
    stack = [spec.parsers[suffix].parse(source).root_node]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(node.named_children)


def branch_count(spec, suffix, source):
    return sum(spec.is_branch(node) for node in nodes(spec, suffix, source))


def describe_languages():
    def it_covers_python_and_typescript():
        assert set(LANGUAGES) == {"python", "typescript"}

    def it_parses_py_files_as_python():
        assert set(PYTHON.parsers) == {".py"}

    def it_parses_ts_and_tsx_files_as_typescript():
        assert set(TYPESCRIPT.parsers) == {".ts", ".tsx"}


def describe_is_branch():
    def it_counts_a_python_boolean_operator():
        assert branch_count(PYTHON, ".py", b"x = a and b\n") == 1

    def it_does_not_count_a_python_arithmetic_operator():
        assert branch_count(PYTHON, ".py", b"x = a + b\n") == 0

    def it_counts_a_python_if_statement():
        assert branch_count(PYTHON, ".py", b"if a:\n    pass\n") == 1

    def it_counts_typescript_logical_operators():
        assert branch_count(TYPESCRIPT, ".ts", b"x = (a && b) || (c ?? d);\n") == 3

    def it_does_not_count_typescript_arithmetic_or_comparison_operators():
        assert branch_count(TYPESCRIPT, ".ts", b"x = a + b < c;\n") == 0

    def it_counts_a_typescript_if_statement():
        assert branch_count(TYPESCRIPT, ".ts", b"if (a) {}\n") == 1
