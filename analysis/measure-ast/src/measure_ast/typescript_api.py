from tree_sitter import Node

from measure_ast.function_signature import arity, text
from measure_ast.label import label

FUNCTIONS = frozenset({"function_declaration", "generator_function_declaration", "function_signature"})
FUNCTION_VALUES = frozenset({"arrow_function", "function_expression", "function", "generator_function"})
CLASSES = frozenset({"class_declaration", "abstract_class_declaration", "class"})
VARIABLES = frozenset({"lexical_declaration", "variable_declaration"})
TYPES = frozenset({"interface_declaration", "type_alias_declaration", "enum_declaration"})


def methods(body: Node) -> list[Node]:
    return [m for m in body.named_children if m.type == "method_definition"]


def class_arity(declaration: Node) -> int:
    constructors = [m for m in methods(declaration.child_by_field_name("body")) if text(m.child_by_field_name("name")) == "constructor"]
    return arity(constructors[0]) if constructors else 0


def value_arity(value: Node | None) -> int | None:
    if value is not None and value.type in FUNCTION_VALUES:
        return arity(value)
    if value is not None and value.type in CLASSES:
        return class_arity(value)
    return None


def declared(declaration: Node) -> list[tuple[str, int | None]]:
    if declaration.type in VARIABLES:
        return [
            (text(d.child_by_field_name("name")), value_arity(d.child_by_field_name("value")))
            for d in declaration.named_children
            if d.type == "variable_declarator"
        ]
    name = declaration.child_by_field_name("name")
    if name is None:
        return []
    if declaration.type in FUNCTIONS:
        return [(text(name), arity(declaration))]
    if declaration.type in CLASSES:
        return [(text(name), class_arity(declaration))]
    if declaration.type in TYPES:
        return [(text(name), None)]
    return []


def public_methods(body: Node) -> list[Node]:
    return [
        m
        for m in methods(body)
        if text(m.child_by_field_name("name")) != "constructor"
        and m.child_by_field_name("name").type != "private_property_identifier"
        and not any(c.type == "accessibility_modifier" and text(c) != "public" for c in m.named_children)
    ]


def default_members(value: Node, arities: dict[str, int | None]) -> list[str]:
    if value.type in CLASSES:
        return [label(f"default.{text(m.child_by_field_name('name'))}", arity(m)) for m in public_methods(value.child_by_field_name("body"))]
    if value.type != "object":
        return []
    members = []
    for member in value.named_children:
        if member.type == "method_definition":
            members.append(label(f"default.{text(member.child_by_field_name('name'))}", arity(member)))
        elif member.type == "pair":
            members.append(label(f"default.{text(member.child_by_field_name('key'))}", value_arity(member.child_by_field_name("value"))))
        elif member.type == "shorthand_property_identifier":
            members.append(label(f"default.{text(member)}", arities.get(text(member))))
    return members


def default_export(value: Node, arities: dict[str, int | None]) -> list[str]:
    if value.type == "identifier":
        own = arities.get(text(value))
    elif value.type in FUNCTIONS:
        own = arity(value)
    else:
        own = value_arity(value)
    return [label("default", own), *default_members(value, arities)]


def exports(statement: Node, arities: dict[str, int | None]) -> list[str]:
    declaration = statement.child_by_field_name("declaration")
    if any(child.type == "default" for child in statement.children):
        return default_export(declaration or statement.child_by_field_name("value"), arities)
    if declaration is not None:
        return [label(name, n) for name, n in declared(declaration)]
    clause = next((c for c in statement.named_children if c.type == "export_clause"), None)
    if clause is None:
        return []
    return [
        label(text(s.child_by_field_name("alias") or s.child_by_field_name("name")), arities.get(text(s.child_by_field_name("name"))))
        for s in clause.named_children
        if s.type == "export_specifier"
    ]


def typescript_api(roots: list[Node]) -> set[str]:
    """Export declarations with arity, re-exports resolved by name across files, and the default export's members."""
    statements = [statement for root in roots for statement in root.named_children]
    arities: dict[str, int | None] = {}
    for statement in reversed(statements):
        declaration = statement.child_by_field_name("declaration") if statement.type == "export_statement" else statement
        if declaration is not None:
            arities.update(declared(declaration))
    return {entry for statement in statements if statement.type == "export_statement" for entry in exports(statement, arities)}
