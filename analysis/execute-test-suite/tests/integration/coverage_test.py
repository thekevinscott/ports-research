COVERAGE_KEYS = {"line_pct", "branch_pct", "covered_lines", "total_lines"}


def describe_coverage():
    def describe_a_python_port():
        def it_measures_the_port_while_the_suite_still_passes(grade, python_target):
            report = grade("python", python_target(42), "unit", "--coverage")
            assert report["success"] is True
            assert report["passed"] == 2
            assert set(report["coverage"]) == COVERAGE_KEYS
            assert report["coverage"]["total_lines"] > 0
            assert report["coverage"]["line_pct"] == 100

        def it_counts_a_module_the_suite_never_imported_against_the_port(
            grade, python_partial_target
        ):
            report = grade("python", python_partial_target, "integration", "--coverage")
            assert report["coverage"]["covered_lines"] < report["coverage"]["total_lines"]

        def it_measures_only_the_ports_source_under_the_unit_suite(grade, python_target):
            target = python_target(42)
            unit = grade("python", target, "unit", "--coverage")
            integration = grade("python", target, "integration", "--coverage")
            assert unit["passed"] == 2
            assert unit["coverage"]["total_lines"] == integration["coverage"]["total_lines"]

        def it_measures_a_port_whose_unit_tests_do_not_collect(grade, python_flat_target):
            report = grade("python", python_flat_target, "unit", "--coverage")
            assert report["errors"] == 2
            assert report["coverage"]["total_lines"] > 0

        def it_reports_zero_for_a_port_the_suite_never_ran(grade, python_nested_target):
            report = grade("python", python_nested_target, "integration", "--adapt", "--coverage")
            assert report["passed"] == 0
            assert report["coverage"]["covered_lines"] == 0
            assert report["coverage"]["line_pct"] == 0.0

        def it_reports_coverage_and_the_fired_rules_together(grade, python_flat_target):
            report = grade("python", python_flat_target, "integration", "--adapt", "--coverage")
            assert report["passed"] == 2
            assert report["adapt"]["rules_fired"] == ["flat_module", "state_add", "exception_eq"]
            assert report["coverage"]["total_lines"] > 0

    def describe_a_typescript_port():
        def it_measures_the_port_while_the_suite_still_passes(grade, typescript_target):
            report = grade("typescript", typescript_target(42), "integration", "--coverage")
            assert report["success"] is True
            assert report["passed"] == 2
            assert set(report["coverage"]) == COVERAGE_KEYS
            assert report["coverage"]["line_pct"] == 100

        def it_counts_an_export_the_suite_never_called_against_the_port(
            grade, typescript_partial_target
        ):
            report = grade("typescript", typescript_partial_target, "integration", "--coverage")
            assert report["success"] is True
            assert report["coverage"]["covered_lines"] < report["coverage"]["total_lines"]

        def it_measures_a_failing_port(grade, typescript_target):
            report = grade("typescript", typescript_target(0), "integration", "--coverage")
            assert report["failed"] == 2
            assert report["coverage"]["total_lines"] > 0

        def it_reports_zero_for_a_port_the_suite_never_ran(grade, typescript_nested_target):
            report = grade(
                "typescript", typescript_nested_target, "integration", "--adapt", "--coverage"
            )
            assert report["passed"] == 0
            assert report["coverage"]["covered_lines"] == 0
            assert report["coverage"]["line_pct"] == 0.0

        def it_measures_only_the_ports_source_under_the_unit_suite(grade, typescript_target):
            target = typescript_target(42)
            unit = grade("typescript", target, "unit", "--coverage")
            integration = grade("typescript", target, "integration", "--coverage")
            assert unit["passed"] == 1
            assert unit["coverage"]["total_lines"] == integration["coverage"]["total_lines"]

        def it_reports_coverage_and_the_fired_rules_together(grade, typescript_named_target):
            report = grade(
                "typescript", typescript_named_target, "integration", "--adapt", "--coverage"
            )
            assert report["passed"] == 2
            assert report["adapt"]["rules_fired"] == ["default_export"]
            assert report["coverage"]["total_lines"] > 0

    def it_adds_only_the_coverage_section_to_the_report(grade, python_target):
        target = python_target(42)
        strict = grade("python", target, "integration")
        measured = grade("python", target, "integration", "--coverage")
        assert set(measured) == set(strict) | {"coverage"}
        assert {key: measured[key] for key in strict} == strict
