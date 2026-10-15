def snapshot(directory):
    return {p: p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def describe_the_integration_suite():
    def it_runs_every_generated_integration_test(grade, python_target):
        report = grade("python", python_target(42), "integration")
        assert report["success"] is True
        assert report["total"] == 2
        assert report["passed"] == 2

    def it_reports_a_failing_python_port(grade, python_target):
        report = grade("python", python_target(0), "integration")
        assert report["success"] is False
        assert report["failed"] == 2

    def it_runs_every_generated_typescript_integration_test(grade, typescript_target):
        report = grade("typescript", typescript_target(42), "integration")
        assert report["success"] is True
        assert report["passed"] == 2

    def it_reports_a_failing_typescript_port(grade, typescript_target):
        report = grade("typescript", typescript_target(0), "integration")
        assert report["success"] is False
        assert report["failed"] == 2

    def it_grades_a_port_whose_tsconfig_extends_a_missing_file(
        grade, typescript_unresolvable_tsconfig_target
    ):
        report = grade("typescript", typescript_unresolvable_tsconfig_target, "integration")
        assert report["success"] is True
        assert report["passed"] == 2


def describe_the_unit_suite():
    def it_runs_the_reference_unit_tests_inside_the_port(grade, python_target):
        report = grade("python", python_target(42), "unit")
        assert report["success"] is True
        assert report["total"] == 2

    def it_grades_the_port_and_not_the_reference_source(grade, python_target):
        report = grade("python", python_target(0), "unit")
        assert report["failed"] == 2

    def it_overwrites_the_ports_own_copy_of_a_reference_test(grade, python_target):
        target = python_target(42)
        (target / "gbnf" / "gbnf_test.py").write_text("def test_port_copy():\n    assert False\n")
        report = grade("python", target, "unit")
        assert report["success"] is True
        assert report["total"] == 2

    def it_counts_a_port_laid_out_differently_as_errors(grade, python_flat_target):
        report = grade("python", python_flat_target, "unit")
        assert report["success"] is False
        assert report["passed"] == 0
        assert report["errors"] == 2

    def it_still_runs_the_tests_that_import_beside_ones_that_do_not(
        grade, python_unsplit_target
    ):
        report = grade("python", python_unsplit_target, "unit")
        assert report["passed"] == 1
        assert report["errors"] == 1

    def it_runs_the_reference_unit_tests_inside_a_typescript_port(grade, typescript_target):
        report = grade("typescript", typescript_target(42), "unit")
        assert report["success"] is True
        assert report["total"] == 1

    def it_grades_the_typescript_port_and_not_the_reference_source(grade, typescript_target):
        report = grade("typescript", typescript_target(0), "unit")
        assert report["failed"] == 1

    def it_counts_a_typescript_port_laid_out_differently_as_errors(
        grade, typescript_relocated_target
    ):
        report = grade("typescript", typescript_relocated_target, "unit")
        assert report["success"] is False
        assert report["total"] == 1
        assert report["errors"] == 1


def it_grades_javascript_and_typescript_against_the_javascript_tree(
    grade, typescript_target, prepared_directory
):
    javascript = grade("javascript", typescript_target(42), "integration")
    typescript = grade("typescript", typescript_target(42), "integration")
    assert javascript["success"] is True
    assert javascript["test_suite_directory"] == typescript["test_suite_directory"]
    assert javascript["test_suite_directory"].endswith("/javascript")


def it_never_writes_into_the_target_or_the_prepared_tree(
    grade, python_target, prepared_directory
):
    target = python_target(42)
    (target / "gbnf" / "gbnf_test.py").write_text("# the port's own copy\n")
    before = snapshot(target), snapshot(prepared_directory)
    grade("python", target, "unit", "--adapt", "--coverage")
    grade("python", target, "integration", "--adapt", "--coverage")
    assert (snapshot(target), snapshot(prepared_directory)) == before


def it_never_writes_into_a_typescript_target_or_the_prepared_tree(
    grade, typescript_target, prepared_directory
):
    target = typescript_target(42)
    before = snapshot(target), snapshot(prepared_directory)
    grade("typescript", target, "unit", "--adapt", "--coverage")
    assert (snapshot(target), snapshot(prepared_directory)) == before
