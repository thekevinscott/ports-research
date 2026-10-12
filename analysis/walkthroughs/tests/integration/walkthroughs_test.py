import json

PYTHON = {"gbnf/__init__.py": "from .grammar import parse_grammar\n", "gbnf/grammar.py": "def parse_grammar(g):\n    return g\n", "gbnf/grammar_test.py": "def test_x():\n    pass\n"}


def tree(root, files):
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text)
    return root


def entry(name, happy=(), errors=(), invariants=()):
    return {"name": name, "happy_path": list(happy), "error_paths": list(errors), "invariants": list(invariants)}


def describe_write():
    def it_writes_one_walkthrough_from_the_source_files_alone_on_the_subscription(run_cli, calls, tmp_path):
        result = run_cli("write", "--implementation", tree(tmp_path / "impl", PYTHON), "--language", "python", "--out", tmp_path / "out")
        assert result.returncode == 0, result.stderr
        written = json.loads((tmp_path / "out" / result.stdout.strip().rsplit("/", 1)[1]).read_text())
        [call] = calls()
        assert written["walkthrough"]["entry_points"][0]["name"] == "parse_grammar"
        assert (written["model"], written["effort"], written["files"]) == ("claude-opus-5-5", "high", ["gbnf/__init__.py", "gbnf/grammar.py"])
        assert written["prompt_chars"] == len(call["prompt"])
        assert written["usage"] == {"input_tokens": len(call["prompt"]) // 4, "output_tokens": 100}
        assert "=== gbnf/grammar.py ===" in call["prompt"] and "grammar_test" not in call["prompt"]
        assert not call["api_key"]
        assert call["argv"][call["argv"].index("--tools") + 1] == ""

    def it_skips_a_walkthrough_already_written_and_repeats_one_under_a_new_tag(run_cli, calls, tmp_path):
        implementation = tree(tmp_path / "impl", PYTHON)
        paths = [run_cli("write", "--implementation", implementation, "--language", "python", "--out", tmp_path / "out", *tag).stdout for tag in ([], [], ["--tag", "b"])]
        assert len(calls()) == 2
        assert paths[0] == paths[1] != paths[2]
        assert calls()[0]["prompt"] == calls()[1]["prompt"]


def describe_compare():
    def it_aligns_steps_by_embedding_similarity_from_the_server(run_cli, make_walkthrough, embeddings_url):
        reference = make_walkthrough("reference", [entry("parse_grammar", ["split the rules", "build the graph", "return the parser"]), entry("only_here")])
        port = make_walkthrough("port", [entry("parseGrammar", ["build the graph", "split the rules", "log a line"]), entry("onlyThere")])
        result = run_cli("compare", "--reference", reference, "--port", port, "--embeddings-url", embeddings_url)
        assert result.returncode == 0, result.stderr
        compared = json.loads(result.stdout)
        [pair] = compared["entry_points"]
        assert (compared["similarity"], compared["threshold"]) == ("embeddings", 0.8)
        assert [round(s["threshold"], 2) for s in compared["sweep"]] == [0.7, 0.75, 0.8, 0.85, 0.9]
        assert compared["sweep"][2]["mean_coverage"] == compared["mean_coverage"]
        assert compared["embeddings"]["url"] == embeddings_url
        assert compared["embeddings"]["model"] == compared["embeddings"]["server"]["id"] == "qwen3-embedding-0.6b-q8_0"
        assert compared["embeddings"]["server"]["status"]["args"][1:3] == ["--pooling", "last"]
        assert pair["happy_path"]["coverage"] == compared["mean_coverage"] == 2 / 3
        assert pair["happy_path"]["order_agreement"] == 0.5
        assert pair["happy_path"]["missing_steps"] == ["return the parser"]
        assert pair["happy_path"]["extra_steps"] == ["log a line"]
        assert (compared["entry_points_matched"], compared["entry_points_reference_only"], compared["entry_points_port_only"]) == (1, ["only_here"], ["onlyThere"])
        assert {r["input"] for r in embeddings_url.requests} >= {"split the rules", "build the graph", "log a line"}

    def it_falls_back_to_word_overlap_without_embeddings(run_cli, make_walkthrough):
        reference = make_walkthrough("reference", [entry("f", ["parse the grammar text"])])
        port = make_walkthrough("port", [entry("f", ["parse grammar text"])])
        result = run_cli("compare", "--reference", reference, "--port", port, "--no-embeddings")
        assert result.returncode == 0, result.stderr
        compared = json.loads(result.stdout)
        assert (compared["similarity"], compared["threshold"], compared["mean_coverage"], compared["embeddings"]) == ("jaccard", 0.5, 1.0, None)

    def it_refuses_without_a_url_or_the_fallback(run_cli, make_walkthrough):
        reference = make_walkthrough("reference", [])
        result = run_cli("compare", "--reference", reference, "--port", reference)
        assert result.returncode != 0
        assert "--embeddings-url" in result.stderr


def describe_reference_lines():
    def it_explains_each_pinned_reference_twice_and_writes_the_noise_floor_and_baseline(run_cli, calls, embeddings_url, tmp_path):
        result = run_cli("reference-lines", "--out", tmp_path / "out", "--embeddings-url", embeddings_url)
        assert result.returncode == 0, result.stderr
        lines = json.loads((tmp_path / "out" / "reference-lines.json").read_text())
        assert json.loads(result.stdout) == lines
        prompts = [call["prompt"] for call in calls()]
        assert len(prompts) == 4
        assert sum("=== gbnf/GBNF.py ===" in p for p in prompts) == sum("=== src/gbnf.ts ===" in p for p in prompts) == 2
        assert all("_test.py ===" not in p and ".test.ts ===" not in p and "=== src/builder/" not in p for p in prompts)
        assert len({p.name for p in (tmp_path / "out").glob("*.json")} - {"reference-lines.json"}) == 4
        assert set(lines["noise_floor"]) == {"python", "javascript"}
        assert set(lines["baseline"]) == {"python_to_javascript", "javascript_to_python"}
        assert all(c["mean_coverage"] == 1.0 for group in ("noise_floor", "baseline") for c in lines[group].values())
        assert all(len(c["sweep"]) == 5 for group in ("noise_floor", "baseline") for c in lines[group].values())
        assert all(c["embeddings"]["server"]["id"] == "qwen3-embedding-0.6b-q8_0" for group in ("noise_floor", "baseline") for c in lines[group].values())
