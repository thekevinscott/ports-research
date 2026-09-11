"""The kind of a rule in the grammar graph.

Rules are modelled as classes (see ``grammar_graph_types.py``), and each one
carries its kind as a ``type`` field so that rules remain easy to discriminate,
serialize and compare.
"""


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"
