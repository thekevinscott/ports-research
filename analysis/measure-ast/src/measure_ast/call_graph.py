import math
from collections import defaultdict
from dataclasses import dataclass

from tree_sitter import Node

from measure_ast.function_signature import NOT_PARAMETERS, arity, function_name, text
from measure_ast.languages import LanguageSpec
from measure_ast.pair_functions import normalise_name

CLASSES = frozenset({"class_definition", "class_declaration", "abstract_class_declaration", "class"})
CONSTRUCTORS = frozenset({"__init__", "constructor"})
CALLS = {"call": "function", "call_expression": "function", "new_expression": "constructor"}
MEMBERS = {"attribute": "attribute", "member_expression": "property"}
OPTIONAL = frozenset({"default_parameter", "typed_default_parameter", "optional_parameter"})
REST = frozenset({"list_splat_pattern", "dictionary_splat_pattern"})
SPREAD = frozenset({"list_splat", "dictionary_splat", "keyword_argument", "spread_element"})


@dataclass(frozen=True)
class Function:
    name: str
    key: str
    own: str
    arity: int
    lowest: int
    highest: float
    method: bool
    public: bool


def enclosing_class(function: Node) -> Node | None:
    """The class whose body declares the function directly, through a decorator or a field."""
    parent = function.parent
    if parent.type in ("decorated_definition", "public_field_definition"):
        parent = parent.parent
    if parent is not None and parent.type in ("block", "class_body") and parent.parent.type in CLASSES:
        return parent.parent
    return None


def is_public(function: Node, own: str) -> bool:
    if own in CONSTRUCTORS:
        return True
    holder = function.parent if function.parent.type == "public_field_definition" else function
    modifiers = [text(c) for c in holder.named_children if c.type == "accessibility_modifier"]
    return not own.startswith(("_", "#")) and all(m == "public" for m in modifiers)


def bounds(function: Node, method: bool) -> tuple[int, float]:
    """Positional arguments the function accepts, a method's bound self or cls excluded."""
    parameters = function.child_by_field_name("parameters")
    if parameters is None:
        lowest, highest = (1, 1) if function.child_by_field_name("parameter") is not None else (0, 0)
    else:
        lowest, highest = 0, 0
        for p in parameters.named_children:
            if p.type in NOT_PARAMETERS:
                continue
            if p.type in REST or any(c.type in REST or c.type == "rest_pattern" for c in p.named_children):
                highest = math.inf
            elif p.type in OPTIONAL or p.child_by_field_name("value") is not None:
                highest += 1
            else:
                lowest, highest = lowest + 1, highest + 1
    decorators = function.parent.named_children if function.parent.type == "decorated_definition" else []
    bound = method and function.type == "function_definition" and not any(text(d) == "@staticmethod" for d in decorators)
    return (max(lowest - 1, 0), highest - 1) if bound else (lowest, highest)


def calls(function: Node, spec: LanguageSpec) -> list[Node]:
    """Call sites in source order, anonymous callbacks included, nested named functions excluded."""
    found, stack = [], list(reversed(function.named_children))
    while stack:
        node = stack.pop()
        if node.type in spec.functions and function_name(node) is not None:
            continue
        if node.type in CALLS:
            found.append(node)
        stack.extend(reversed(node.named_children))
    return found


def is_super(receiver: Node | None) -> bool:
    if receiver is None:
        return False
    if receiver.type == "call":
        receiver = receiver.child_by_field_name("function")
    return receiver.type == "super" or (receiver.type == "identifier" and text(receiver) == "super")


def callee(call: Node) -> tuple[str, bool] | None:
    """The called name and whether it was reached through an object."""
    target = call.child_by_field_name(CALLS[call.type])
    if target is not None and target.type in MEMBERS:
        if is_super(target.child_by_field_name("object")):
            return None
        target, through_object = target.child_by_field_name(MEMBERS[target.type]), True
    else:
        through_object = False
    if target is None or target.type not in ("identifier", "property_identifier", "private_property_identifier", "type_identifier"):
        return None
    return text(target), through_object


def argument_count(call: Node) -> int | None:
    """Positional arguments, None when a spread or keyword argument makes the count unknowable."""
    arguments = call.child_by_field_name("arguments")
    if arguments is None:
        return 0
    if arguments.type == "generator_expression":
        return 1
    if arguments.type not in ("argument_list", "arguments"):
        return None
    given = [a for a in arguments.named_children if a.type != "comment"]
    return None if any(a.type in SPREAD for a in given) else len(given)


@dataclass
class CallGraph:
    functions: list[Function]
    edges: list[list[int]]
    classes: dict[str, list[int]]

    def trace(self, start: int) -> list[int]:
        """Depth-first preorder from start, callees in call-site order, each function once."""
        visited, order, stack = set(), [], [start]
        while stack:
            index = stack.pop()
            if index in visited:
                continue
            visited.add(index)
            order.append(index)
            stack.extend(reversed([j for j in self.edges[index] if j not in visited]))
        return order

    def entry_points(self, entry: str) -> list[int]:
        """A function by name and arity, else a class's constructor and public methods."""
        name, _, given = entry.partition("/")
        for i, fn in enumerate(self.functions):
            if not fn.method and fn.name == name and (not given or fn.arity == int(given)):
                return [i]
        members = self.classes.get(name, [])
        constructors = [i for i in members if self.functions[i].own in CONSTRUCTORS]
        return constructors + [i for i in members if self.functions[i].public and i not in constructors]


def call_graph(roots: list[Node], spec: LanguageSpec) -> CallGraph:
    functions, sites, classes = [], [], defaultdict(list)
    for root in roots:
        stack = [root]
        while stack:
            node = stack.pop()
            stack.extend(reversed(node.named_children))
            own = function_name(node) if node.type in spec.functions else None
            if own is None:
                continue
            owner = enclosing_class(node)
            owner_name = text(owner.child_by_field_name("name")) if owner and owner.child_by_field_name("name") else None
            method = owner_name is not None
            if method:
                classes[owner_name].append(len(functions))
            qualified = f"{owner_name}.{own}" if method else own
            key = f"{normalise_name(owner_name)}.{normalise_name(own)}" if method else normalise_name(own)
            functions.append(
                Function(qualified, key, own, arity(node), *bounds(node, method), method=method, public=is_public(node, own))
            )
            sites.append(calls(node, spec))
    by_name, by_bare_name, constructors = defaultdict(list), defaultdict(list), defaultdict(list)
    for i, fn in enumerate(functions):
        by_name[normalise_name(fn.own)].append(i)
        if not fn.method:
            by_bare_name[normalise_name(fn.own)].append(i)
    for owner_name, members in classes.items():
        constructors[normalise_name(owner_name)].extend(i for i in members if functions[i].own in CONSTRUCTORS)
    edges = []
    for site_list in sites:
        callees = []
        for call in site_list:
            resolved = callee(call)
            if resolved is None:
                continue
            name, through_object = resolved
            key = normalise_name(name)
            count = argument_count(call)
            candidates = constructors[key] if call.type == "new_expression" else (
                (by_name if through_object else by_bare_name)[key] + constructors[key]
            )
            for j in candidates:
                fits = count is None or functions[j].lowest <= count <= functions[j].highest
                if fits and j not in callees:
                    callees.append(j)
        edges.append(callees)
    return CallGraph(functions, edges, dict(classes))
