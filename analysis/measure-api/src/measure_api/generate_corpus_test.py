import json

from measure_api.generate_corpus import GENERATOR_VERSION, RANDOM_INPUTS, generate_corpus


def tree(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def describe_generate_corpus():
    def it_writes_a_manifest_with_seed_count_and_both_generator_versions(tmp_path):
        generate_corpus(out=tmp_path, seed=3, count=5)
        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert manifest["seed"] == 3
        assert manifest["count"] == 5
        assert manifest["generator_version"] == GENERATOR_VERSION
        assert manifest["measure_behavior"]["seed"] == 3

    def it_writes_one_grammar_and_one_input_list_per_id(tmp_path):
        generate_corpus(out=tmp_path, seed=3, count=5)
        grammars = sorted(p.stem for p in (tmp_path / "grammars").glob("*.gbnf"))
        inputs = sorted(p.stem for p in (tmp_path / "inputs").glob("*.json"))
        assert grammars == inputs == ["g0000", "g0001", "g0002", "g0003", "g0004"]

    def it_extends_measure_behaviors_inputs_with_random_strings(tmp_path):
        generate_corpus(out=tmp_path, seed=3, count=5)
        for path in (tmp_path / "inputs").glob("*.json"):
            listed = json.loads(path.read_text())
            assert listed[0] == ""
            assert all(isinstance(text, str) for text in listed)
            assert len(listed) > RANDOM_INPUTS

    def it_is_byte_identical_for_the_same_seed(tmp_path):
        generate_corpus(out=tmp_path / "a", seed=1, count=10)
        generate_corpus(out=tmp_path / "b", seed=1, count=10)
        assert tree(tmp_path / "a") == tree(tmp_path / "b")

    def it_differs_across_seeds(tmp_path):
        generate_corpus(out=tmp_path / "a", seed=1, count=10)
        generate_corpus(out=tmp_path / "b", seed=2, count=10)
        assert tree(tmp_path / "a") != tree(tmp_path / "b")
