from measure_ast.languages import PYTHON, TYPESCRIPT
from measure_ast.measure_tree import measure_tree

PYTHON_BRANCHES = b"""\
def f(a):
    if a:
        pass
    elif a:
        pass
    for x in a:
        pass
    while a:
        break
    try:
        pass
    except ValueError:
        pass
    match a:
        case 1:
            pass
    y = 1 if a else 2
    z = a and a
    w = [i for i in a if i]
"""

PYTHON_NESTED = b"""\
def outer(a):
    def inner(b):
        return b and a
    return inner if a else None
"""

PYTHON_DECORATED_ASYNC = b"""\
@dec
async def f():
    pass

def g():
    pass
"""

TYPESCRIPT_BRANCHES = b"""\
function f(a: number) {
  if (a) {}
  for (let i = 0; i < a; i++) {}
  for (const x of []) {}
  while (a) {}
  do {} while (a);
  try {} catch (e) {}
  switch (a) { case 1: break; default: break; }
  const t = a ? 1 : 2;
  const u = (a && a) || (a ?? a);
}
"""

TYPESCRIPT_KINDS = b"""\
function a() {}
function* b() {}
class C { m() {} }
const d = () => 1;
const e = function () {};
"""

TYPESCRIPT_NESTED = b"""\
class C {
  m(a: number) {
    const g = (b: number) => b && a;
    return a ? g : null;
  }
}
"""


def measure(spec, suffix, source):
    return measure_tree(spec.parsers[suffix].parse(source).root_node, spec)


def describe_measure_tree():
    def it_counts_named_nodes():
        assert measure(PYTHON, ".py", b"x = 1\n")["node_count"] == 5

    def it_reports_the_deepest_named_node_with_the_root_at_zero():
        assert measure(PYTHON, ".py", b"x = 1\n")["max_depth"] == 3

    def it_reports_a_lone_root_for_an_empty_file():
        report = measure(PYTHON, ".py", b"")
        assert (report["node_count"], report["max_depth"]) == (1, 0)

    def it_has_no_functions_for_a_bare_assignment():
        assert measure(PYTHON, ".py", b"x = 1\n")["functions"] == []


def describe_python_functions():
    def it_measures_lines_from_def_to_the_last_body_row():
        functions = measure(PYTHON, ".py", b"def f():\n    return 1\n")["functions"]
        assert functions == [{"lines": 2, "cyclomatic": 1}]

    def it_adds_one_per_branch_node():
        functions = measure(PYTHON, ".py", PYTHON_BRANCHES)["functions"]
        assert [fn["cyclomatic"] for fn in functions] == [10]

    def it_leaves_nested_function_branches_out_of_the_outer_function():
        functions = measure(PYTHON, ".py", PYTHON_NESTED)["functions"]
        assert functions == [{"lines": 4, "cyclomatic": 2}, {"lines": 2, "cyclomatic": 2}]

    def it_counts_decorated_and_async_definitions_from_their_def_line():
        functions = measure(PYTHON, ".py", PYTHON_DECORATED_ASYNC)["functions"]
        assert [fn["lines"] for fn in functions] == [2, 2]

    def it_does_not_count_lambdas():
        assert measure(PYTHON, ".py", b"f = lambda a: a\n")["functions"] == []


def describe_typescript_functions():
    def it_counts_declarations_generators_methods_arrows_and_function_expressions():
        functions = measure(TYPESCRIPT, ".ts", TYPESCRIPT_KINDS)["functions"]
        assert [fn["cyclomatic"] for fn in functions] == [1, 1, 1, 1, 1]

    def it_does_not_count_bodiless_signatures():
        assert measure(TYPESCRIPT, ".ts", b"interface I { m(): void; }\n")["functions"] == []

    def it_adds_one_per_branch_node():
        functions = measure(TYPESCRIPT, ".ts", TYPESCRIPT_BRANCHES)["functions"]
        assert [fn["cyclomatic"] for fn in functions] == [12]

    def it_leaves_nested_arrow_branches_out_of_the_enclosing_method():
        functions = measure(TYPESCRIPT, ".ts", TYPESCRIPT_NESTED)["functions"]
        assert functions == [{"lines": 4, "cyclomatic": 2}, {"lines": 1, "cyclomatic": 2}]

    def it_parses_tsx_with_the_tsx_grammar():
        report = measure(TYPESCRIPT, ".tsx", b"const x = <div />;\n")
        assert report["node_count"] > 1
