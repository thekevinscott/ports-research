from execute_test_suite import execute_test_suite

COVERAGE_KEYS = {"line_pct", "branch_pct", "covered_lines", "total_lines"}


def grade(language, target, test_suites_directory, **kwargs):
    return execute_test_suite(
        language=language,
        target=target,
        test_suites_directory=test_suites_directory,
        **kwargs,
    )


def describe_coverage():
    def describe_a_python_port():
        def it_measures_the_port_while_the_suite_still_passes(
            test_suites_directory, python_target
        ):
            report = grade(
                "python",
                python_target(42),
                test_suites_directory,
                coverage=True,
            )
            assert report["success"] is True
            assert report["passed"] == 2
            assert set(report["coverage"]) == COVERAGE_KEYS
            assert report["coverage"]["total_lines"] > 0
            assert report["coverage"]["line_pct"] == 100

        def it_counts_a_module_the_suite_never_imported_against_the_port(
            test_suites_directory, python_partial_target
        ):
            report = grade(
                "python",
                python_partial_target,
                test_suites_directory,
                coverage=True,
            )
            assert report["coverage"]["line_pct"] < 100
            assert report["coverage"]["covered_lines"] < report["coverage"]["total_lines"]

        def it_measures_only_the_narrowed_suite(
            test_suites_directory, python_target
        ):
            report = grade(
                "python",
                python_target(42),
                test_suites_directory,
                suite="integration",
                coverage=True,
            )
            assert report["total"] == 1
            assert report["coverage"]["total_lines"] > 0

        def it_reports_coverage_and_the_fired_rules_together(
            test_suites_directory, python_flat_target
        ):
            report = grade(
                "python",
                python_flat_target,
                test_suites_directory,
                adapt=True,
                coverage=True,
            )
            assert report["passed"] == 2
            assert report["adapt"]["rules_fired"] == [
                "flat_module",
                "state_add",
                "exception_eq",
            ]
            assert report["coverage"]["total_lines"] > 0

    def describe_a_typescript_port():
        def it_measures_the_port_while_the_suite_still_passes(
            test_suites_directory, typescript_target
        ):
            report = grade(
                "typescript",
                typescript_target(42),
                test_suites_directory,
                coverage=True,
            )
            assert report["success"] is True
            assert report["passed"] == 2
            assert set(report["coverage"]) == COVERAGE_KEYS
            assert report["coverage"]["total_lines"] > 0
            assert report["coverage"]["line_pct"] == 100

        def it_counts_an_export_the_suite_never_called_against_the_port(
            test_suites_directory, typescript_partial_target
        ):
            report = grade(
                "typescript",
                typescript_partial_target,
                test_suites_directory,
                coverage=True,
            )
            assert report["success"] is True
            assert report["coverage"]["line_pct"] < 100
            assert report["coverage"]["covered_lines"] < report["coverage"]["total_lines"]

        def it_reports_coverage_and_the_fired_rules_together(
            test_suites_directory, typescript_named_target
        ):
            report = grade(
                "typescript",
                typescript_named_target,
                test_suites_directory,
                adapt=True,
                coverage=True,
            )
            assert report["passed"] == 2
            assert report["adapt"]["rules_fired"] == ["default_export"]
            assert report["coverage"]["total_lines"] > 0

    def it_adds_only_the_coverage_section_to_the_report(
        test_suites_directory, python_target
    ):
        target = python_target(42)
        strict = grade("python", target, test_suites_directory)
        measured = grade(
            "python", target, test_suites_directory, coverage=True
        )
        assert set(measured) == set(strict) | {"coverage"}
        assert {key: measured[key] for key in strict} == strict

    def it_never_writes_into_the_target(
        test_suites_directory, python_target
    ):
        target = python_target(42)
        before = sorted(p.relative_to(target) for p in target.rglob("*"))
        grade("python", target, test_suites_directory, coverage=True)
        after = sorted(p.relative_to(target) for p in target.rglob("*"))
        assert after == before

    def it_never_writes_into_the_suite(
        test_suites_directory, typescript_target
    ):
        before = sorted(
            p.relative_to(test_suites_directory) for p in test_suites_directory.rglob("*")
        )
        grade(
            "typescript",
            typescript_target(42),
            test_suites_directory,
            coverage=True,
        )
        after = sorted(
            p.relative_to(test_suites_directory) for p in test_suites_directory.rglob("*")
        )
        assert after == before
