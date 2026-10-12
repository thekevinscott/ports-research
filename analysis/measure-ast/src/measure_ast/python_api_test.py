from measure_ast.languages import PYTHON
from measure_ast.python_api import python_api


def roots(*sources):
    return [PYTHON.parsers[".py"].parse(source).root_node for source in sources]


def describe_python_api():
    def it_lists_public_top_level_functions_with_arity():
        assert python_api(roots(b"def f(a, b):\n    pass\ndef _g():\n    pass\n")) == {"f/2"}

    def it_lists_a_decorated_function():
        assert python_api(roots(b"@cache\ndef f(a):\n    pass\n")) == {"f/1"}

    def it_leaves_out_methods_and_nested_functions():
        source = b"class C:\n    def m(self):\n        def inner():\n            pass\n"
        assert python_api(roots(source)) == {"C/0"}

    def it_gives_a_class_the_arity_of_its_init_without_self():
        assert python_api(roots(b"class C:\n    def __init__(self, a, b):\n        pass\n")) == {"C/2"}

    def it_gives_a_dataclass_the_count_of_its_annotated_fields():
        source = b"@dataclass\nclass C:\n    a: int\n    b: str = ''\n    c = 1\n"
        assert python_api(roots(source)) == {"C/2"}

    def it_leaves_out_private_classes():
        assert python_api(roots(b"class _C:\n    pass\n")) == set()

    def it_adds_names_from_dunder_all_with_arity_resolved_across_files():
        init = b"from .a import _hidden, Thing\n__all__ = ['_hidden', 'Thing', 'CONSTANT']\n"
        module = b"def _hidden(a):\n    pass\nclass Thing:\n    pass\nCONSTANT = 1\n"
        assert python_api(roots(init, module)) == {"_hidden/1", "Thing/0", "CONSTANT"}

    def it_keeps_one_entry_per_name_and_arity():
        assert python_api(roots(b"def f(a):\n    pass\n", b"def f(a):\n    pass\n", b"def f():\n    pass\n")) == {"f/1", "f/0"}
