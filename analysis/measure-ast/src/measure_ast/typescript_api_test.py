from measure_ast.languages import TYPESCRIPT
from measure_ast.typescript_api import typescript_api


def roots(*sources):
    return [TYPESCRIPT.parsers[".ts"].parse(source).root_node for source in sources]


def describe_typescript_api():
    def it_lists_exported_functions_and_function_valued_constants_with_arity():
        source = b"export function f(a, b) {}\nexport const g = (a) => a;\nexport const h = function () {};\n"
        assert typescript_api(roots(source)) == {"f/2", "g/1", "h/0"}

    def it_lists_exported_values_and_types_without_arity():
        source = b"export const X = 1;\nexport type T = number;\nexport interface I {}\nexport enum E { A }\n"
        assert typescript_api(roots(source)) == {"X", "T", "I", "E"}

    def it_gives_an_exported_class_its_constructor_arity():
        source = b"export class C { constructor(a, b) {} }\nexport class D {}\n"
        assert typescript_api(roots(source)) == {"C/2", "D/0"}

    def it_leaves_out_declarations_that_are_not_exported():
        assert typescript_api(roots(b"function f(a) {}\nconst g = 1;\n")) == set()

    def it_lists_re_exports_under_their_exported_name_with_arity_resolved_across_files():
        index = b"export { parse, Thing as Renamed, Missing } from './parse';\n"
        module = b"const parse = (a, b) => a;\nclass Thing { constructor(a) {} }\n"
        assert typescript_api(roots(index, module)) == {"parse/2", "Renamed/1", "Missing"}

    def it_lists_a_default_re_export():
        index = b"export { GBNF as default } from './gbnf';\n"
        module = b"export const GBNF = (input, initial) => input;\n"
        assert typescript_api(roots(index, module)) == {"default/2", "GBNF/2"}

    def it_lists_the_members_of_a_default_exported_object():
        source = b"const s = (a) => a;\nexport default { m(a, b) {}, k: () => 1, v: 2, s };\n"
        assert typescript_api(roots(source)) == {"default", "default.m/2", "default.k/0", "default.v", "default.s/1"}

    def it_lists_the_public_methods_of_a_default_exported_class():
        source = b"export default class C {\n  constructor(a) {}\n  m(b) {}\n  private p() {}\n  #q() {}\n}\n"
        assert typescript_api(roots(source)) == {"default/1", "default.m/1"}

    def it_resolves_the_arity_of_a_default_exported_identifier():
        assert typescript_api(roots(b"const f = (a) => a;\nexport default f;\n")) == {"default/1"}

    def it_does_not_follow_star_exports():
        assert typescript_api(roots(b"export * from './other';\n")) == set()
