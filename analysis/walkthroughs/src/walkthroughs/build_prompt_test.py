import re
from pathlib import Path

import pytest

from walkthroughs.build_prompt import PROMPT, build_prompt

TREE = {
    "gbnf/__init__.py": "from .grammar import parse\n",
    "gbnf/grammar.py": "def parse(g):\n    return g\n",
    "gbnf/grammar_test.py": "def test_parse():\n    pass\n",
    "src/index.ts": "export const parse = (g: string) => g;\n",
    "src/index.test.ts": "test('x', () => {});\n",
    "src/builder/build.ts": "build();\n",
    "README.md": "# gbnf\n",
}


@pytest.fixture
def tree(tmp_path):
    for relative, text in TREE.items():
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_text(text)
    return tmp_path


def describe_build_prompt():
    def it_is_the_fixed_prompt_then_each_source_file_of_the_language_under_its_path(tree):
        prompt, files = build_prompt(tree, "python")
        assert files == ["gbnf/__init__.py", "gbnf/grammar.py"]
        assert prompt == (
            PROMPT
            + "\n---\n\n"
            + "=== gbnf/__init__.py ===\nfrom .grammar import parse\n\n"
            + "=== gbnf/grammar.py ===\ndef parse(g):\n    return g\n"
        )

    def it_leaves_out_tests_and_build_tooling_for_typescript(tree):
        _, files = build_prompt(tree, "typescript")
        assert files == ["src/index.ts"]

    def it_names_neither_a_language_nor_a_port():
        words = set(re.findall(r"\w+", PROMPT.lower()))
        assert not words & {"python", "typescript", "javascript", "port", "ported", "translation", "translated", "original", "source"}

    def it_reads_the_prompt_from_the_prompts_directory():
        assert PROMPT == (Path(__file__).resolve().parents[2] / "prompts" / "walkthrough.md").read_text()
