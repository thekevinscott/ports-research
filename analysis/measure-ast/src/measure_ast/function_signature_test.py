from measure_ast.function_signature import arity, function_name
from measure_ast.languages import PYTHON, TYPESCRIPT


def functions(spec, suffix, source):
    stack = [spec.parsers[suffix].parse(source).root_node]
    found = []
    while stack:
        node = stack.pop()
        if node.type in spec.functions:
            found.append(node)
        stack.extend(reversed(node.named_children))
    return found


def signatures(spec, suffix, source):
    return [(function_name(fn), arity(fn)) for fn in functions(spec, suffix, source)]


def describe_python_signatures():
    def it_reads_name_and_parameter_count():
        assert signatures(PYTHON, ".py", b"def f(a, b=1, *c, **d):\n    pass\n") == [("f", 4)]

    def it_counts_self_on_a_method():
        assert signatures(PYTHON, ".py", b"class C:\n    def m(self, a):\n        pass\n") == [("m", 2)]

    def it_does_not_count_the_keyword_and_positional_separators():
        assert signatures(PYTHON, ".py", b"def f(a, /, b, *, c):\n    pass\n") == [("f", 3)]

    def it_does_not_count_comments_between_parameters():
        assert signatures(PYTHON, ".py", b"def f(\n    a,  # first\n    b,\n):\n    pass\n") == [("f", 2)]


def describe_typescript_signatures():
    def it_reads_a_function_declaration():
        assert signatures(TYPESCRIPT, ".ts", b"function f(a: number, b?: string, ...c: number[]) {}\n") == [("f", 3)]

    def it_reads_a_method_and_a_private_method():
        assert signatures(TYPESCRIPT, ".ts", b"class C { m(a) {} #p() {} }\n") == [("m", 1), ("#p", 0)]

    def it_names_an_arrow_function_after_its_variable():
        assert signatures(TYPESCRIPT, ".ts", b"const f = (a, b) => a;\n") == [("f", 2)]

    def it_counts_a_bare_arrow_parameter():
        assert signatures(TYPESCRIPT, ".ts", b"const f = a => a;\n") == [("f", 1)]

    def it_names_a_function_expression_after_its_object_key():
        assert signatures(TYPESCRIPT, ".ts", b"const o = { k: function () {} };\n") == [("k", 0)]

    def it_names_a_class_field_arrow_after_the_field():
        assert signatures(TYPESCRIPT, ".ts", b"class C { f = (a) => a; }\n") == [("f", 1)]

    def it_names_an_assigned_arrow_after_the_assigned_property():
        assert signatures(TYPESCRIPT, ".ts", b"this.f = () => 1;\n") == [("f", 0)]

    def it_leaves_a_callback_unnamed():
        assert signatures(TYPESCRIPT, ".ts", b"xs.map((x) => x);\n") == [(None, 1)]
