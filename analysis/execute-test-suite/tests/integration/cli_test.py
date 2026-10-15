def describe_cli():
    def it_exits_zero_and_reports_success_for_a_passing_port(invoke, python_target):
        result = invoke("python", python_target(42), "integration")
        assert result.exit_code == 0
        assert '"success": true' in result.output

    def it_exits_nonzero_and_reports_failure_for_a_failing_port(invoke, python_target):
        result = invoke("python", python_target(0), "integration")
        assert result.exit_code == 1
        assert '"success": false' in result.output

    def it_prints_no_adapt_or_coverage_section_without_the_flags(grade, python_target):
        report = grade("python", python_target(42), "unit")
        assert "adapt" not in report
        assert "coverage" not in report

    def it_reports_which_prepared_tree_it_ran(grade, python_target, prepared_directory):
        report = grade("python", python_target(42), "unit")
        assert report["suite"] == "unit"
        assert report["test_suite_directory"].startswith(str(prepared_directory))
        assert report["test_suite_directory"].endswith("/python")
