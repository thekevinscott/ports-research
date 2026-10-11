from unittest.mock import call, patch

import pytest

from .assemble_whitelist import assemble_whitelist

CASES = {
    "python_none": ("python", False, False, False, ["source"], []),
    "python_unit": ("python", True, False, False, ["unit-tests", "source"], []),
    "python_source-integration": (
        "python", False, True, False, ["integration-tests", "source"], [],
    ),
    "python_target-integration": (
        "python", False, False, True, ["source"], ["integration-tests"],
    ),
    "python_unit_source-integration": (
        "python", True, True, False, ["unit-tests", "integration-tests", "source"], [],
    ),
    "python_unit_target-integration": (
        "python", True, False, True, ["unit-tests", "source"], ["integration-tests"],
    ),
    "python_source-integration_target-integration": (
        "python", False, True, True, ["integration-tests", "source"], ["integration-tests"],
    ),
    "python_all": (
        "python", True, True, True,
        ["unit-tests", "integration-tests", "source"], ["integration-tests"],
    ),
    "javascript_none": ("javascript", False, False, False, ["source"], []),
    "javascript_unit": ("javascript", True, False, False, ["unit-tests", "source"], []),
    "javascript_source-integration": (
        "javascript", False, True, False, ["integration-tests", "source"], [],
    ),
    "javascript_target-integration": (
        "javascript", False, False, True, ["source"], ["integration-tests"],
    ),
    "javascript_unit_source-integration": (
        "javascript", True, True, False, ["unit-tests", "integration-tests", "source"], [],
    ),
    "javascript_unit_target-integration": (
        "javascript", True, False, True, ["unit-tests", "source"], ["integration-tests"],
    ),
    "javascript_source-integration_target-integration": (
        "javascript", False, True, True, ["integration-tests", "source"], ["integration-tests"],
    ),
    "javascript_all": (
        "javascript", True, True, True,
        ["unit-tests", "integration-tests", "source"], ["integration-tests"],
    ),
}
OTHER = {"python": "javascript", "javascript": "python"}


@pytest.fixture
def compose():
    with patch(
        "gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist.compose"
    ) as m:
        m.side_effect = lambda language, names: "".join(f"+ /{language}/{n}\n" for n in names)
        yield m


def describe_assemble_whitelist():
    @pytest.mark.parametrize("case", CASES.values(), ids=list(CASES))
    def it_composes_source_then_target_then_footer(compose, case):
        source, unit, source_integration, target_integration, source_names, target_names = case

        rules = assemble_whitelist(
            source,
            include_unit_tests=unit,
            include_source_integration_tests=source_integration,
            include_target_integration_tests=target_integration,
        )

        assert compose.call_args_list == [
            call(source, source_names),
            call(OTHER[source], target_names),
        ]
        expected = "".join(f"+ /{source}/{n}\n" for n in source_names)
        expected += "".join(f"+ /{OTHER[source]}/{n}\n" for n in target_names)
        assert rules == expected + "\n+ */\n- *\n"
