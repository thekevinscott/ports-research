from pathlib import Path

import pytest

from round_trip_experiment.stage_port import stage_port

KEY = "390bf534c55d496b"
RUN_ID = "20260909T001426Z_1c28aa33"


@pytest.fixture
def forward_run(tmp_path: Path) -> Path:
    port = tmp_path / "runs" / RUN_ID / "ported_implementation"
    (port / "src").mkdir(parents=True)
    (port / "src" / "index.ts").write_text("export const f = () => 1;\n")
    (port / "node_modules" / "left-pad").mkdir(parents=True)
    (port / "node_modules" / "left-pad" / "index.js").write_text("module.exports = 1;\n")
    (port / "__pycache__").mkdir()
    (port / "__pycache__" / "m.pyc").write_bytes(b"\x00")
    return port.parent


@pytest.fixture
def derivations(tmp_path: Path) -> Path:
    tests = tmp_path / "gbnf-cache" / KEY / "tests"
    (tests / "python").mkdir(parents=True)
    (tests / "typescript").mkdir(parents=True)
    (tests / "python" / "test_gbnf.py").write_text("def test_it():\n    pass\n")
    return tmp_path / "gbnf-cache"


@pytest.fixture
def staging(tmp_path: Path) -> Path:
    return tmp_path / "staging"


@pytest.fixture
def stage(forward_run, derivations, staging):
    def call() -> Path:
        return stage_port(
            forward_run,
            source_language="typescript",
            derivation_cache_key=KEY,
            derivations_directory=derivations,
            staging_directory=staging,
        )

    return call


def describe_stage_port():
    def it_stages_under_the_forward_run_and_the_derivation_cache_key(stage, staging):
        assert stage() == staging / RUN_ID / KEY

    def it_copies_the_port_in_as_the_reverse_source_language(stage):
        assert (stage() / "source" / "typescript" / "src" / "index.ts").read_text() == "export const f = () => 1;\n"

    def it_leaves_build_artefacts_out(stage):
        staged = stage()
        assert not (staged / "source" / "typescript" / "node_modules").exists()
        assert not (staged / "source" / "typescript" / "__pycache__").exists()

    def it_links_the_real_derivations_test_suites_beside_the_source(stage, derivations):
        staged = stage()
        assert (staged / "tests").is_symlink()
        assert (staged / "tests" / "python" / "test_gbnf.py").read_text() == "def test_it():\n    pass\n"
        assert (staged / "tests").resolve() == (derivations / KEY / "tests").resolve()

    def it_restages_without_failing_on_a_second_call(stage):
        stage()
        staged = stage()
        assert (staged / "source" / "typescript" / "src" / "index.ts").is_file()
        assert (staged / "tests" / "typescript").is_dir()

    def it_fails_when_the_run_has_no_port(stage, forward_run):
        for path in sorted((forward_run / "ported_implementation").rglob("*"), reverse=True):
            path.rmdir() if path.is_dir() else path.unlink()
        (forward_run / "ported_implementation").rmdir()
        with pytest.raises(FileNotFoundError):
            stage()
