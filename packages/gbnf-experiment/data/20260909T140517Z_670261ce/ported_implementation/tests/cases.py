"""The shared corpus of grammars/inputs used for parity testing.

Each case is ``{"name", "grammar", "initial"?, "adds"?}``. ``fixtures/reference.json``
holds what the reference implementation produces for this corpus (recorded by
``tools/record_reference.py``); ``test_parity.py`` asserts the Python port produces
the same thing.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fuzz import generate_cases

ARITHMETIC = """
root  ::= (expr "=" ws term "\\n")+
expr  ::= term ([-+*/] term)*
term  ::= ident | num | "(" ws expr ")" ws
ident ::= [a-z] [a-z0-9_]* ws
num   ::= [0-9]+ ws
ws    ::= [ \\t\\n]*
"""

JSON_GRAMMAR = """
root   ::= object
value  ::= object | array | string | number | ("true" | "false" | "null") ws
object ::=
  "{" ws (
            string ":" ws value
    ("," ws string ":" ws value)*
  )? "}" ws
array  ::=
  "[" ws (
            value
    ("," ws value)*
  )? "]" ws
string ::=
  "\\"" (
    [^"\\\\] |
    "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
  )* "\\"" ws
number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws
ws ::= ([ \\t\\n] ws)?
"""

CASES: List[Dict[str, Any]] = [
    # --- literals & alternates -------------------------------------------------
    {"name": "single-char", "grammar": 'root ::= "a"', "adds": ["a"]},
    {"name": "literal", "grammar": 'root ::= "foo"', "adds": ["f", "o", "o"]},
    {"name": "literal-whole", "grammar": 'root ::= "foo"', "adds": ["foo"]},
    {"name": "readme-yes-no", "grammar": 'root  ::= "yes" | "no"', "adds": ["y", "es"]},
    {"name": "readme-yes-no-alt", "grammar": 'root  ::= "yes" | "no"', "adds": ["n", "o"]},
    {
        "name": "readme-green-eggs",
        "grammar": 'root  ::= "I like green eggs and ham"',
        "adds": ["I li", "ke gree", "n eggs and ham"],
    },
    {"name": "initial-string", "grammar": 'root ::= "abc"', "initial": "ab", "adds": ["c"]},
    {"name": "initial-code-points", "grammar": 'root ::= "abc"', "initial": [97, 98]},
    {"name": "initial-single-code-point", "grammar": 'root ::= "abc"', "initial": 97},
    {"name": "three-alts", "grammar": 'root ::= "a" | "b" | "c"', "adds": ["b"]},
    {"name": "shared-prefix-alts", "grammar": 'root ::= "ab" | "ac"', "adds": ["a"]},
    # --- character classes -----------------------------------------------------
    {"name": "char-class", "grammar": "root ::= [abc]", "adds": ["b"]},
    {"name": "char-range", "grammar": "root ::= [a-z]", "adds": ["q"]},
    {"name": "char-range-multi", "grammar": "root ::= [a-zA-Z0-9]", "adds": ["G"]},
    {"name": "char-range-and-alts", "grammar": "root ::= [a-z_-]", "adds": ["-"]},
    {"name": "char-not", "grammar": 'root ::= [^abc] "!"', "adds": ["z", "!"]},
    {"name": "char-not-range", "grammar": 'root ::= [^a-z] "!"', "adds": ["Z", "!"]},
    {"name": "char-class-trailing-hyphen", "grammar": "root ::= [a-]", "adds": ["-"]},
    # --- repetition ------------------------------------------------------------
    {"name": "star", "grammar": 'root ::= "a"*', "adds": ["aaa"]},
    {"name": "star-empty", "grammar": 'root ::= "a"*'},
    {"name": "plus", "grammar": 'root ::= "a"+', "adds": ["aa"]},
    {"name": "optional", "grammar": 'root ::= "a"? "b"', "adds": ["b"]},
    {"name": "optional-present", "grammar": 'root ::= "a"? "b"', "adds": ["ab"]},
    {"name": "star-class", "grammar": "root ::= [0-9]*", "adds": ["123"]},
    {"name": "plus-then-literal", "grammar": 'root ::= [0-9]+ "."', "adds": ["12", "."]},
    # --- groups & references ---------------------------------------------------
    {"name": "group", "grammar": 'root ::= ("a" | "b") "c"', "adds": ["a", "c"]},
    {"name": "group-star", "grammar": 'root ::= ("ab")*', "adds": ["abab"]},
    {"name": "group-plus", "grammar": 'root ::= ("ab" | "cd")+', "adds": ["abcd"]},
    {
        "name": "nested-groups",
        "grammar": 'root ::= (("a" | "b") "c")+ "d"',
        "adds": ["ac", "bc", "d"],
    },
    {"name": "rule-ref", "grammar": 'root ::= a b\na ::= "x"\nb ::= "y"', "adds": ["x", "y"]},
    {
        "name": "rule-ref-forward",
        "grammar": 'root ::= greeting "!"\ngreeting ::= "hi" | "yo"',
        "adds": ["yo!"],
    },
    {"name": "recursive", "grammar": 'root ::= "a" root | "b"', "adds": ["aaa", "b"]},
    {
        "name": "mutual-recursion",
        "grammar": 'root ::= a\na ::= "x" b | "x"\nb ::= "y" a',
        "adds": ["xyx"],
    },
    # --- escapes ---------------------------------------------------------------
    {"name": "escape-newline", "grammar": 'root ::= "a\\n"', "adds": ["a\n"]},
    {"name": "escape-tab", "grammar": 'root ::= "a\\t"', "adds": ["a\t"]},
    {"name": "escape-cr", "grammar": 'root ::= "a\\r"', "adds": ["a\r"]},
    {"name": "escape-quote", "grammar": 'root ::= "\\""', "adds": ['"']},
    {"name": "escape-backslash", "grammar": 'root ::= "\\\\"', "adds": ["\\"]},
    {"name": "escape-bracket", "grammar": "root ::= [\\[\\]]", "adds": ["]"]},
    {"name": "escape-hex", "grammar": 'root ::= "\\x41"', "adds": ["A"]},
    {"name": "escape-unicode", "grammar": 'root ::= "\\u00e9"', "adds": ["é"]},
    {"name": "escape-unicode-range", "grammar": "root ::= [\\u0041-\\u005a]", "adds": ["M"]},
    # --- whitespace, comments, formatting --------------------------------------
    {"name": "comment", "grammar": '# a comment\nroot ::= "a" # trailing\n', "adds": ["a"]},
    {"name": "comment-only-leading", "grammar": '#comment\nroot ::= "a"', "adds": ["a"]},
    {"name": "crlf", "grammar": 'root ::= "a"\r\nother ::= "b"\r\n', "adds": ["a"]},
    {"name": "blank-lines", "grammar": '\n\nroot ::= "a"\n\n', "adds": ["a"]},
    {"name": "multiline-rule", "grammar": 'root ::= (\n  "a" |\n  "b"\n)', "adds": ["b"]},
    {"name": "trailing-whitespace", "grammar": 'root ::= "a"   \n', "adds": ["a"]},
    # --- bigger grammars -------------------------------------------------------
    {"name": "arithmetic", "grammar": ARITHMETIC, "adds": ["a", " = ", "12", "\n"]},
    {
        "name": "arithmetic-expression",
        "grammar": ARITHMETIC,
        "adds": ["x +1 = ", "(y)", "\n"],
    },
    {"name": "arithmetic-invalid", "grammar": ARITHMETIC, "adds": ["a = 12 + 3"]},
    {"name": "arithmetic-two-lines", "grammar": ARITHMETIC, "adds": ["a = 1\n", "b = 2\n"]},
    {"name": "json-empty-object", "grammar": JSON_GRAMMAR, "adds": ["{}"]},
    {"name": "json-object", "grammar": JSON_GRAMMAR, "adds": ['{"a"', ": ", "1", "}"]},
    {"name": "json-nested", "grammar": JSON_GRAMMAR, "adds": ['{"a": [1, 2, {"b": null}]}']},
    {"name": "json-escapes", "grammar": JSON_GRAMMAR, "adds": ['{"a\\n\\u0041b": "c"}']},
    {"name": "json-number", "grammar": JSON_GRAMMAR, "adds": ['{"n": -1.5e+10}']},
    # --- grammar errors --------------------------------------------------------
    {"name": "err-empty-grammar", "grammar": ""},
    {"name": "err-whitespace-grammar", "grammar": "   \n  "},
    {"name": "err-undefined-rule", "grammar": "root ::= foo"},
    {"name": "err-undefined-rule-multiline", "grammar": 'root ::= "a" bar\nbaz ::= "c"'},
    {"name": "err-missing-equals", "grammar": 'root "a"'},
    {"name": "err-missing-equals-partial", "grammar": 'root := "a"'},
    {"name": "err-unterminated-string", "grammar": 'root ::= "abc'},
    {"name": "err-unterminated-class", "grammar": "root ::= [abc"},
    {"name": "err-unclosed-paren", "grammar": 'root ::= ("a"'},
    {"name": "err-dangling-star", "grammar": "root ::= *"},
    {"name": "err-invalid-name-char", "grammar": 'root_1 ::= "a"'},
    {"name": "err-unknown-escape", "grammar": 'root ::= "\\q"'},
    {"name": "err-trailing-garbage", "grammar": 'root ::= "a" %'},
    {"name": "err-only-comment", "grammar": "# just a comment"},
    # --- infinitely recursive grammars -----------------------------------------
    # The reference exhausts the Javascript call stack on these; the port raises
    # RecursionError. `test_parity.normalize` treats the two as the same outcome.
    {"name": "err-self-recursive", "grammar": "root ::= root"},
    {"name": "err-nullable-star", "grammar": 'root ::= a*\na ::= "b"?\n', "adds": ["b"]},
    {"name": "err-nullable-plus", "grammar": 'root ::= a+\na ::= "b"*\n', "adds": ["b"]},
    # --- input errors ----------------------------------------------------------
    {"name": "err-input-first-char", "grammar": 'root ::= "abc"', "adds": ["x"]},
    {"name": "err-input-mid", "grammar": 'root ::= "abc"', "adds": ["ax"]},
    {"name": "err-input-after-add", "grammar": 'root ::= "abc"', "adds": ["ab", "z"]},
    {"name": "err-input-past-end", "grammar": 'root ::= "ab"', "adds": ["abc"]},
    {"name": "err-input-excluded", "grammar": "root ::= [^a]", "adds": ["a"]},
    {"name": "err-input-initial", "grammar": 'root ::= "abc"', "initial": "x"},
]

# Seeded random grammars/inputs, to catch divergences the cases above miss.
CASES += generate_cases()
