from measure_ast.extract_functions import extract_functions
from measure_ast.languages import PYTHON, TYPESCRIPT

PYTHON_SOURCE = b"""\
def f(a):
    if a:
        return 1
    return 2

def g():
    return 1
"""


def extract(spec, suffix, source):
    return extract_functions(spec.parsers[suffix].parse(source).root_node, spec)


def describe_extract_functions():
    def it_records_name_arity_lines_and_cyclomatic_per_function():
        records = extract(PYTHON, ".py", PYTHON_SOURCE)
        assert [(r.name, r.arity, r.lines, r.cyclomatic) for r in records] == [("f", 1, 4, 2), ("g", 0, 2, 1)]

    def it_records_the_abstracted_subtree_and_its_size():
        record = extract(PYTHON, ".py", b"def g():\n    return 1\n")[0]
        assert record.tree == (
            "function_definition",
            (("identifier", ()), ("parameters", ()), ("block", (("return_statement", (("integer", ()),)),))),
        )
        assert record.size == 6

    def it_gives_renamed_functions_the_same_tree():
        before = extract(PYTHON, ".py", b"def f(a):\n    return a\n")[0]
        after = extract(PYTHON, ".py", b"def h(b):\n    return b\n")[0]
        assert (before.tree, after.name) == (after.tree, "h")

    def it_records_unnamed_typescript_callbacks_with_no_name():
        records = extract(TYPESCRIPT, ".ts", b"const f = (xs) => xs.map((x) => x);\n")
        assert [(r.name, r.arity) for r in records] == [("f", 1), (None, 1)]
