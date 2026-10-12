import json

import pytest

DIRECTORIES = {"python": "python", "typescript": "javascript"}


@pytest.mark.parametrize("language", ["python", "typescript"])
def describe_reference():
    def it_reproduces_the_committed_reference_outcomes(run_cli, reference_checkout, corpus, tmp_path, language):
        out = tmp_path / "outcomes.jsonl"
        result = run_cli("run", "--corpus", corpus, "--implementation", reference_checkout / DIRECTORIES[language], "--language", language, "--out", out)
        assert result.returncode == 0, result.stderr
        run_cli("compare", "--reference", corpus / f"reference-{language}.jsonl", "--port", out, "--out", tmp_path / "c.json")
        assert json.loads((tmp_path / "c.json").read_text())["agreement_rate"] == 1.0
