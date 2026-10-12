from measure_ast.abstract_tree import abstract
from measure_ast.languages import PYTHON, TYPESCRIPT


def tree(spec, suffix, source):
    return abstract(spec.parsers[suffix].parse(source).root_node, spec)


def describe_abstract():
    def it_labels_each_named_node_with_its_type():
        assert tree(PYTHON, ".py", b"x = y\n") == (
            "module",
            (("expression_statement", (("assignment", (("identifier", ()), ("identifier", ()))),)),),
        )

    def it_makes_renaming_free():
        assert tree(PYTHON, ".py", b"def f(a):\n    return a\n") == tree(PYTHON, ".py", b"def g(b):\n    return b\n")

    def it_collapses_a_literal_to_a_leaf_of_its_type():
        assert tree(PYTHON, ".py", b"x = 'a\\n'\n") == tree(PYTHON, ".py", b"x = 'abc'\n")

    def it_collapses_a_typescript_template_string():
        assert tree(TYPESCRIPT, ".ts", b"x = `a${b}`;\n") == tree(TYPESCRIPT, ".ts", b"x = `c`;\n")

    def it_drops_comments():
        assert tree(PYTHON, ".py", b"# note\nx = 1  # more\n") == tree(PYTHON, ".py", b"x = 2\n")

    def it_keeps_structural_differences():
        assert tree(PYTHON, ".py", b"x = a\n") != tree(PYTHON, ".py", b"x = a.b\n")
