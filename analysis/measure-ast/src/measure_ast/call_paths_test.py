from measure_ast.call_graph import call_graph
from measure_ast.call_paths import call_paths
from measure_ast.languages import PYTHON

REFERENCE = b"""\
def parse(text):
    tokens = tokenize(text)
    tree = build(tokens)
    return check(tree)

def tokenize(text):
    return text.split()

def build(tokens):
    node = Node(tokens)
    node.grow(tokens)
    return node

def check(tree):
    return tree

class Node:
    def __init__(self, tokens):
        self.tokens = tokens

    def grow(self, tokens):
        pass

def unused():
    pass
"""

# build no longer grows the node; parse validates through a new helper.
PORT = b"""\
def parse(text):
    tokens = tokenize(text)
    tree = build(tokens)
    return validate(tree)

def tokenize(text):
    return text.split()

def build(tokens):
    return Node(tokens)

def validate(tree):
    return tree

class Node:
    def __init__(self, tokens):
        self.tokens = tokens

    def grow(self, tokens):
        pass

def leftover():
    pass
"""


def graph(source):
    return call_graph([PYTHON.parsers[".py"].parse(source).root_node], PYTHON)


def run(port=PORT, reference=REFERENCE, shared=("parse/1",)):
    return call_paths(port=graph(port), reference=graph(reference), shared=list(shared))


def describe_call_paths():
    def it_traces_each_entry_point_on_both_sides():
        entry = run()["entry_points"][0]
        assert entry["entry_point"] == "parse"
        assert entry["reference_trace"] == ["parse", "tokenize", "build", "Node.__init__", "Node.grow", "check"]
        assert entry["port_trace"] == ["parse", "tokenize", "build", "Node.__init__", "validate"]
        assert (entry["reachable_reference"], entry["reachable_port"]) == (6, 5)

    def it_measures_trace_edit_distance_over_normalised_names():
        entry = run()["entry_points"][0]
        assert entry["trace_edit_distance"] == 2
        assert entry["trace_normalised"] == 2 / 6

    def it_compares_call_edges_by_normalised_endpoints():
        entry = run()["entry_points"][0]
        assert (entry["reference_edges"], entry["port_edges"]) == (5, 4)
        assert entry["edge_recall"] == 3 / 5
        assert entry["edge_precision"] == 3 / 4
        assert entry["missing_edges"] == ["parse->check", "build->Node.grow"]
        assert entry["extra_edges"] == ["parse->validate"]

    def it_writes_one_explainer_sentence_per_entry_point():
        assert run()["explainer"] == [
            "parse: reference trace of 6 (parse, tokenize, build, Node.__init__, Node.grow, check); "
            "port 5, missing parse->check, build->Node.grow, extra parse->validate"
        ]

    def it_expands_a_shared_class_into_constructor_and_public_methods():
        entries = run(shared=["Node/1"])["entry_points"]
        assert [e["entry_point"] for e in entries] == ["Node.__init__", "Node.grow"]
        assert all(e["edge_recall"] is None and e["trace_edit_distance"] == 0 for e in entries)

    def it_aggregates_over_entry_points():
        report = run(shared=["parse/1", "Node/1"])
        assert report["entry_point_count"] == 3
        assert report["mean_edge_recall"] == 3 / 5
        assert report["median_trace_normalised"] == 0
        assert report["reachable_fraction_reference"] == 6 / 7
        assert report["reachable_fraction_port"] == 6 / 7

    def it_lists_port_functions_reachable_from_no_entry_point():
        assert run()["unreachable_port_only"] == ["Node.grow/2", "leftover/0"]
        assert run(shared=["parse/1", "Node/1"])["unreachable_port_only"] == ["leftover/0"]

    def it_says_none_when_nothing_is_missing_or_extra():
        assert run(port=REFERENCE)["explainer"][0].endswith("port 6, missing none, extra none")

    def it_reports_nones_without_entry_points():
        report = run(shared=[])
        assert report == {
            "entry_point_count": 0,
            "mean_edge_recall": None,
            "median_trace_normalised": None,
            "reachable_fraction_reference": 0,
            "reachable_fraction_port": 0,
            "unreachable_port_only": ["Node.__init__/2", "Node.grow/2", "build/1", "leftover/0", "parse/1", "tokenize/1", "validate/1"],
            "entry_points": [],
            "explainer": [],
        }

    def it_gives_an_entry_point_missing_from_one_side_an_empty_trace_there():
        port = PORT.replace(b"    def grow(self, tokens):\n        pass\n", b"")
        entry = run(port=port, shared=["Node/1"])["entry_points"][1]
        assert (entry["entry_point"], entry["reference_trace"], entry["port_trace"]) == ("Node.grow", ["Node.grow"], [])
        assert entry["trace_normalised"] == 1
