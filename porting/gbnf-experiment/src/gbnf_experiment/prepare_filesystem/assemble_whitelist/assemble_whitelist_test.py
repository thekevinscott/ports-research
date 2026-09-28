from itertools import product

import pytest

from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import (
    assemble_whitelist,
)

LANGUAGES = ("python", "javascript")
OTHER = {"python": "javascript", "javascript": "python"}

# One line from each rule file, so a test reads the real files and not a copy.
UNIT_INCLUDE = {
    "python": "+ /python/gbnf/**_test.py\n",
    "javascript": "+ /javascript/src/**.test.ts\n",
}
INTEGRATION_INCLUDE = {
    "python": "+ /python/tests/***\n",
    "javascript": "+ /javascript/integration-tests/***\n",
}
TEST_EXCLUSION = {
    "python": "- /python/**_test.py\n",
    "javascript": "- /javascript/**.test.ts\n",
}
SOURCE_INCLUDE = {
    "python": "+ /python/gbnf/**.py\n",
    "javascript": "+ /javascript/src/**.ts\n",
}
RUNNER_INCLUDE = {
    "python": "+ /python/Makefile\n",
    "javascript": "+ /javascript/vitest.config.integration.ts\n",
}

CONDITIONS = {
    f"source-{source}_unit-{unit}_source-integration-{source_integration}"
    f"_target-integration-{target_integration}": (
        source,
        unit,
        source_integration,
        target_integration,
    )
    for source, unit, source_integration, target_integration in product(
        LANGUAGES, (False, True), (False, True), (False, True)
    )
}


@pytest.fixture(params=CONDITIONS, ids=list(CONDITIONS))
def condition(request):
    return CONDITIONS[request.param]


@pytest.fixture
def rules(condition):
    source, unit, source_integration, target_integration = condition
    return assemble_whitelist(
        source,
        include_unit_tests=unit,
        include_source_integration_tests=source_integration,
        include_target_integration_tests=target_integration,
    )


def lines(rules):
    return [line for line in rules.splitlines() if line and not line.startswith("#")]


def describe_assemble_whitelist():
    def describe_for_each_of_the_sixteen_conditions():
        def it_ends_with_the_traversal_and_the_catch_all_exclusion(rules):
            assert lines(rules)[-2:] == ["+ */", "- *"]

        def it_anchors_every_pattern_to_a_language_directory(rules):
            for line in lines(rules)[:-2]:
                assert line.split(" ", 1)[1].startswith(("/python/", "/javascript/")), line

        def it_whitelists_the_source(condition, rules):
            assert SOURCE_INCLUDE[condition[0]] in rules

        def it_includes_unit_tests_only_when_asked(condition, rules):
            source, unit, _, _ = condition
            assert (UNIT_INCLUDE[source] in rules) is unit

        def it_includes_the_source_integration_suite_only_when_asked(condition, rules):
            source, _, source_integration, _ = condition
            assert (INTEGRATION_INCLUDE[source] in rules) is source_integration

        def it_puts_every_test_include_ahead_of_the_exclusion(condition, rules):
            source = condition[0]
            exclusion = rules.index(TEST_EXCLUSION[source])
            for include in (UNIT_INCLUDE[source], INTEGRATION_INCLUDE[source]):
                if include in rules:
                    assert rules.index(include) < exclusion

        def it_names_the_target_only_when_asked(condition, rules):
            source, _, _, target_integration = condition
            target = OTHER[source]
            assert (f"/{target}/" in rules) is target_integration

        def it_gives_the_target_its_suite_and_runner_and_no_source(condition, rules):
            source, _, _, target_integration = condition
            if not target_integration:
                return
            target = OTHER[source]
            assert INTEGRATION_INCLUDE[target] in rules
            assert RUNNER_INCLUDE[target] in rules
            assert SOURCE_INCLUDE[target] not in rules
            assert UNIT_INCLUDE[target] not in rules
