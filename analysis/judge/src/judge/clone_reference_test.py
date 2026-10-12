from unittest.mock import patch

import pytest

from judge.clone_reference import clone_reference

GBNF_COMMIT = "13f1aca495d11e160fffd68c4ba299a2415909d8"


@pytest.fixture
def run_function():
    with patch("judge.clone_reference.subprocess.run", autospec=True) as m:
        yield m


def describe_clone_reference():
    def it_fetches_the_pin_checks_it_out_and_applies_the_experiment_patches(run_function, tmp_path):
        clone_reference(tmp_path)
        commands = [c.args[0] for c in run_function.call_args_list]
        assert commands[0] == ["git", "-C", str(tmp_path), "init", "-q"]
        assert commands[1] == ["git", "-C", str(tmp_path), "fetch", "-q", "--depth", "1", "https://github.com/thekevinscott/gbnf", GBNF_COMMIT]
        assert commands[2] == ["git", "-C", str(tmp_path), "checkout", "-q", "FETCH_HEAD"]
        assert commands[3][:4] == ["git", "-C", str(tmp_path), "apply"]
        patches = commands[3][4:]
        assert patches and all(p.endswith(".patch") and "gbnf-prepare/patches" in p for p in patches)
        assert patches == sorted(patches)
        assert all(c.kwargs["check"] for c in run_function.call_args_list)

    def it_returns_the_gbnf_package_directory(run_function, tmp_path):
        assert clone_reference(tmp_path) == tmp_path / "packages" / "gbnf"
