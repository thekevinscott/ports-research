from measure_ast.call_graph import call_graph
from measure_ast.languages import PYTHON, TYPESCRIPT


def python(*sources):
    return call_graph([PYTHON.parsers[".py"].parse(s).root_node for s in sources], PYTHON)


def typescript(*sources):
    return call_graph([TYPESCRIPT.parsers[".ts"].parse(s).root_node for s in sources], TYPESCRIPT)


def adjacency(graph):
    return {fn.name: [graph.functions[j].name for j in callees] for fn, callees in zip(graph.functions, graph.edges)}


def names(graph, indices):
    return [graph.functions[i].name for i in indices]


def describe_python_call_graph():
    def it_links_a_bare_call_to_the_function_of_that_name_across_files_and_drops_external_calls():
        graph = python(b"def f(x):\n    print(x)\n    return g(x)\n", b"def g(x):\n    return len(x)\n")
        assert adjacency(graph) == {"f": ["g"], "g": []}

    def it_matches_names_after_normalisation():
        graph = python(b"def f():\n    return _parse_rule()\n\ndef parseRule():\n    pass\n")
        assert adjacency(graph)["f"] == ["parseRule"]

    def it_resolves_a_method_call_through_any_object_by_name_only():
        graph = python(
            b"class A:\n    def add(self, x):\n        pass\n\n"
            b"class B:\n    def add(self, x):\n        pass\n\n"
            b"def f(thing):\n    thing.add(1)\n"
        )
        assert adjacency(graph)["f"] == ["A.add", "B.add"]

    def it_does_not_resolve_a_bare_call_to_a_method():
        graph = python(b"class A:\n    def g(self):\n        pass\n\ndef f():\n    g()\n")
        assert adjacency(graph)["f"] == []

    def it_drops_calls_through_super():
        graph = python(
            b"class A:\n    def __init__(self, x):\n        pass\n\n"
            b"class B(A):\n    def __init__(self, x):\n        super().__init__(x)\n"
        )
        assert adjacency(graph)["B.__init__"] == []

    def it_resolves_an_instantiation_to_the_constructor():
        graph = python(b"class Node:\n    def __init__(self, value):\n        pass\n\ndef f():\n    return Node(1)\n")
        assert adjacency(graph)["f"] == ["Node.__init__"]

    def it_requires_the_argument_count_to_fit_the_parameters_without_self():
        graph = python(
            b"def two(a, b):\n    pass\n\n"
            b"def defaults(a, b=1):\n    pass\n\n"
            b"def rest(a, *b):\n    pass\n\n"
            b"class C:\n    def m(self, a):\n        pass\n\n"
            b"    @staticmethod\n    def s(a):\n        pass\n\n"
            b"def f(c):\n    two(1)\n    defaults(1)\n    rest(1, 2, 3)\n    c.m(1)\n    c.s(1)\n"
        )
        assert adjacency(graph)["f"] == ["defaults", "rest", "C.m", "C.s"]

    def it_ignores_arity_when_the_call_has_keyword_or_splat_arguments():
        graph = python(b"def two(a, b):\n    pass\n\ndef f(xs):\n    two(*xs)\n    two(a=1)\n")
        assert adjacency(graph)["f"] == ["two"]

    def it_charges_calls_in_an_anonymous_callback_to_the_enclosing_function():
        graph = python(b"def g(x):\n    pass\n\ndef f(xs):\n    return map(lambda x: g(x), xs)\n")
        assert adjacency(graph)["f"] == ["g"]

    def it_charges_calls_in_a_nested_named_function_to_that_function():
        graph = python(b"def g():\n    pass\n\ndef f():\n    def inner():\n        g()\n    return inner()\n")
        assert adjacency(graph) == {"g": [], "f": ["inner"], "inner": ["g"]}

    def it_does_not_link_a_function_passed_as_a_value():
        graph = python(b"def g(x):\n    pass\n\ndef f(xs):\n    return map(g, xs)\n")
        assert adjacency(graph)["f"] == []

    def it_does_not_resolve_a_method_call_on_a_receiver_bound_to_a_builtin():
        graph = python(
            b"class A:\n    def add(self, x):\n        pass\n\n    def get(self, x):\n        pass\n\n"
            b"def f(registry, cache: dict[str, int]):\n    seen = set()\n    out = []\n    other = registry.list()\n"
            b"    seen.add(1)\n    cache.get(1)\n    out.add(1)\n    {}.get(1)\n    other.add(1)\n"
        )
        assert adjacency(graph)["f"] == ["A.add"]

    def it_does_not_resolve_a_method_call_on_an_attribute_the_class_binds_to_a_builtin():
        graph = python(
            b"class A:\n    def __init__(self):\n        self.seen = set()\n        self.child = B()\n\n"
            b"    def run(self):\n        self.seen.add(1)\n        self.child.put(1)\n\n"
            b"class B:\n    def __init__(self):\n        pass\n\n    def add(self, x):\n        pass\n\n    def put(self, x):\n        pass\n"
        )
        assert adjacency(graph)["A.run"] == ["B.put"]


def describe_typescript_call_graph():
    def it_links_bare_member_and_new_calls():
        graph = typescript(
            b"class Graph {\n  constructor(rules: number[]) {}\n  add(input: string) { return this.#walk(input); }\n"
            b"  #walk(input: string) { return input; }\n}\n"
            b"export const parse = (src: string) => {\n  const graph = new Graph(tokenize(src));\n  return graph.add(src);\n};\n"
            b"function tokenize(src: string) { return src.split(''); }\n"
        )
        assert adjacency(graph) == {
            "Graph.constructor": [],
            "Graph.add": ["Graph.#walk"],
            "Graph.#walk": [],
            "parse": ["Graph.constructor", "tokenize", "Graph.add"],
            "tokenize": [],
        }

    def it_drops_calls_through_super():
        graph = typescript(
            b"class A {\n  run() {}\n}\nclass B extends A {\n  constructor() { super(); }\n  run() { super.run(); }\n}\n"
        )
        assert (adjacency(graph)["B.constructor"], adjacency(graph)["B.run"]) == ([], [])

    def it_counts_optional_default_and_rest_parameters():
        graph = typescript(
            b"function opt(a: number, b?: number) {}\nfunction def(a: number, b = 1) {}\nfunction rest(...a: number[]) {}\n"
            b"function two(a: number, b: number) {}\n"
            b"function f(xs: number[]) { opt(1); def(1); rest(1, 2); two(1); two(...xs); }\n"
        )
        assert adjacency(graph)["f"] == ["opt", "def", "rest", "two"]

    def it_charges_calls_in_an_arrow_callback_to_the_enclosing_function():
        graph = typescript(b"const g = (x: number) => x;\nfunction f(xs: number[]) { return xs.map(x => g(x)); }\n")
        assert adjacency(graph)["f"] == ["g"]

    def it_does_not_resolve_a_method_call_on_a_receiver_bound_to_a_builtin():
        graph = typescript(
            b"class Graph {\n  private cache = new Map<string, number>();\n  private next: Graph;\n"
            b"  has(x: string) { return this.cache.get(x) || this.next.has(x); }\n  get(x: string) { return x; }\n}\n"
            b"function f(graph: Graph, names: string[], index: Set<string>) {\n"
            b"  const seen = new Set<string>();\n  seen.get('a');\n  names.get('a');\n  index.get('a');\n  graph.has('a');\n}\n"
        )
        assert (adjacency(graph)["Graph.has"], adjacency(graph)["f"]) == (["Graph.has"], ["Graph.has"])


def describe_trace():
    def it_walks_depth_first_in_call_site_order_visiting_each_function_once():
        graph = python(
            b"def a():\n    b()\n    c()\n    b()\n\n"
            b"def b():\n    d()\n\n"
            b"def c():\n    d()\n    a()\n\n"
            b"def d():\n    pass\n"
        )
        assert names(graph, graph.trace(0)) == ["a", "b", "d", "c"]


def describe_entry_points():
    SOURCE = (
        b"def parse(text):\n    pass\n\n"
        b"class Parser:\n    def __init__(self, text):\n        pass\n\n"
        b"    def run(self):\n        pass\n\n"
        b"    def _step(self):\n        pass\n"
    )

    def it_finds_a_function_by_name_and_arity():
        graph = python(SOURCE)
        assert names(graph, graph.entry_points("parse/1")) == ["parse"]
        assert graph.entry_points("parse/2") == []

    def it_expands_a_class_to_its_constructor_and_public_methods():
        assert names(python(SOURCE), python(SOURCE).entry_points("Parser/1")) == ["Parser.__init__", "Parser.run"]

    def it_skips_entries_that_are_not_functions_or_classes():
        assert python(b"X = 1\n").entry_points("X") == []

    def it_expands_a_typescript_class_without_its_private_methods():
        graph = typescript(
            b"export class P {\n  constructor() {}\n  run() {}\n  private hidden() {}\n  #secret() {}\n}\n"
        )
        assert names(graph, graph.entry_points("P/0")) == ["P.constructor", "P.run"]
