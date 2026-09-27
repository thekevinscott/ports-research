from itertools import product

import pytest

from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import (
    assemble_whitelist,
)

LANGUAGES = ("python", "javascript")
OTHER = {"python": "javascript", "javascript": "python"}

# One line from each rule file, so a test reads the real files and not a copy.
UNIT_INCLUDE = {"python": "+ /gbnf/**_test.py\n", "javascript": "+ /src/**.test.ts\n"}
INTEGRATION_INCLUDE = {"python": "+ /tests/***\n", "javascript": "+ /integration-tests/***\n"}
TEST_EXCLUSION = {"python": "- *_test.py\n", "javascript": "- *.test.ts\n"}
SOURCE_INCLUDE = {"python": "+ /gbnf/**.py\n", "javascript": "+ /src/**.ts\n"}
HARNESS_INCLUDE = {"python": "+ /Makefile\n", "javascript": "+ /vitest.config.integration.ts\n"}

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
def whitelist(condition):
    source, unit, source_integration, target_integration = condition
    return assemble_whitelist(
        source,
        include_unit_tests=unit,
        include_source_integration_tests=source_integration,
        include_target_integration_tests=target_integration,
    )


def describe_assemble_whitelist():
    def describe_for_each_of_the_sixteen_conditions():
        def it_names_the_source_and_the_other_language_as_target(condition, whitelist):
            source = condition[0]
            assert whitelist.source_language == source
            assert whitelist.target_language == OTHER[source]

        def it_ends_the_source_rules_with_the_whitelist(condition, whitelist):
            source = condition[0]
            assert SOURCE_INCLUDE[source] in whitelist.source_rules
            assert whitelist.source_rules.endswith("- *\n")

        def it_includes_unit_tests_only_when_asked(condition, whitelist):
            source, unit, _, _ = condition
            assert (UNIT_INCLUDE[source] in whitelist.source_rules) is unit

        def it_includes_the_source_integration_suite_only_when_asked(condition, whitelist):
            source, _, source_integration, _ = condition
            assert (INTEGRATION_INCLUDE[source] in whitelist.source_rules) is source_integration

        def it_puts_every_test_include_ahead_of_the_exclusion(condition, whitelist):
            source = condition[0]
            rules = whitelist.source_rules
            exclusion = rules.index(TEST_EXCLUSION[source])
            for include in (UNIT_INCLUDE[source], INTEGRATION_INCLUDE[source]):
                if include in rules:
                    assert rules.index(include) < exclusion

        def it_has_target_rules_only_when_asked(condition, whitelist):
            _, _, _, target_integration = condition
            assert bool(whitelist.target_rules) is target_integration

        def it_gives_the_target_its_suite_and_harness_and_no_source(condition, whitelist):
            source, _, _, target_integration = condition
            if not target_integration:
                return
            target = OTHER[source]
            assert INTEGRATION_INCLUDE[target] in whitelist.target_rules
            assert HARNESS_INCLUDE[target] in whitelist.target_rules
            assert SOURCE_INCLUDE[target] not in whitelist.target_rules
            assert UNIT_INCLUDE[target] not in whitelist.target_rules

        def it_exposes_the_four_build_args(whitelist):
            assert whitelist.build_args == {
                "SOURCE_LANGUAGE": whitelist.source_language,
                "SOURCE_RULES": whitelist.source_rules,
                "TARGET_LANGUAGE": whitelist.target_language,
                "TARGET_RULES": whitelist.target_rules,
            }
