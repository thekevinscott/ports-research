import json

from measure_behavior.generate_corpus import GENERATOR_VERSION, generate_corpus


def tree(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def describe_generate_corpus():
    def it_writes_a_manifest_with_seed_count_and_generator_version(tmp_path):
        generate_corpus(out=tmp_path, seed=3, count=5)
        assert json.loads((tmp_path / "manifest.json").read_text()) == {
            "seed": 3,
            "count": 5,
            "generator_version": GENERATOR_VERSION,
        }

    def it_writes_one_grammar_and_one_input_list_per_id(tmp_path):
        generate_corpus(out=tmp_path, seed=3, count=5)
        grammars = sorted(p.stem for p in (tmp_path / "grammars").glob("*.gbnf"))
        inputs = sorted(p.stem for p in (tmp_path / "inputs").glob("*.json"))
        assert grammars == inputs == ["g0000", "g0001", "g0002", "g0003", "g0004"]
        for stem in inputs:
            listed = json.loads((tmp_path / "inputs" / f"{stem}.json").read_text())
            assert listed and all(isinstance(text, str) for text in listed)

    def it_is_byte_identical_for_the_same_seed(tmp_path):
        generate_corpus(out=tmp_path / "a", seed=1, count=20)
        generate_corpus(out=tmp_path / "b", seed=1, count=20)
        assert tree(tmp_path / "a") == tree(tmp_path / "b")

    def it_differs_across_seeds(tmp_path):
        generate_corpus(out=tmp_path / "a", seed=1, count=20)
        generate_corpus(out=tmp_path / "b", seed=2, count=20)
        assert tree(tmp_path / "a") != tree(tmp_path / "b")

    def it_includes_malformed_grammars(tmp_path):
        generate_corpus(out=tmp_path, seed=0, count=40)
        texts = [p.read_text() for p in (tmp_path / "grammars").glob("*.gbnf")]
        assert any("extra ::=" in text or "root ::=" not in text or "::=" not in text.split("\n")[0] for text in texts)
