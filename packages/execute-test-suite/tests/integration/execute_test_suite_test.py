from execute_test_suite import execute_test_suite


def describe_execute_test_suite():
    def describe_a_python_port():
        def it_reports_a_passing_suite(
            test_suites_directory, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(42),
                test_suites_directory=test_suites_directory,
            )
            assert report["success"] is True
            assert report["total"] == 2
            assert report["passed"] == 2
            assert report["failed"] == 0

        def it_reports_a_failing_suite(
            test_suites_directory, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(0),
                test_suites_directory=test_suites_directory,
            )
            assert report["success"] is False
            assert report["total"] == 2
            assert report["failed"] == 2

        def it_runs_only_the_grammar_fixtures_as_the_integration_suite(
            test_suites_directory, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(42),
                test_suites_directory=test_suites_directory,
                suite="integration",
            )
            assert report["suite"] == "integration"
            assert report["total"] == 1

        def it_runs_everything_but_the_grammar_fixtures_as_the_unit_suite(
            test_suites_directory, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(42),
                test_suites_directory=test_suites_directory,
                suite="unit",
            )
            assert report["suite"] == "unit"
            assert report["total"] == 1

    def describe_a_typescript_port():
        def it_reports_a_passing_suite(
            test_suites_directory, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(42),
                test_suites_directory=test_suites_directory,
            )
            assert report["success"] is True
            assert report["passed"] == 2

        def it_reports_a_failing_suite(
            test_suites_directory, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(0),
                test_suites_directory=test_suites_directory,
            )
            assert report["success"] is False
            assert report["failed"] == 2

        def it_grades_a_port_whose_tsconfig_extends_a_missing_file(
            test_suites_directory,
            typescript_unresolvable_tsconfig_target,
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_unresolvable_tsconfig_target,
                test_suites_directory=test_suites_directory,
            )
            assert report["success"] is True
            assert report["passed"] == 2

        def it_runs_only_the_grammar_spec_as_the_integration_suite(
            test_suites_directory, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(42),
                test_suites_directory=test_suites_directory,
                suite="integration",
            )
            assert report["total"] == 1

        def it_runs_everything_but_the_grammar_spec_as_the_unit_suite(
            test_suites_directory, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(42),
                test_suites_directory=test_suites_directory,
                suite="unit",
            )
            assert report["total"] == 1

    def it_grades_javascript_against_the_same_suite_as_typescript(
        test_suites_directory, typescript_target
    ):
        report = execute_test_suite(
            language="javascript",
            target=typescript_target(42),
            test_suites_directory=test_suites_directory,
        )
        assert report["test_suite_directory"] == str(
            test_suites_directory / "typescript"
        )
        assert report["success"] is True

    def it_never_writes_into_the_suite(
        test_suites_directory, python_target
    ):
        before = sorted(
            p.relative_to(test_suites_directory) for p in test_suites_directory.rglob("*")
        )
        execute_test_suite(
            language="python",
            target=python_target(42),
            test_suites_directory=test_suites_directory,
        )
        after = sorted(
            p.relative_to(test_suites_directory) for p in test_suites_directory.rglob("*")
        )
        assert after == before

    def it_never_writes_into_the_target(
        test_suites_directory, python_target
    ):
        target = python_target(42)
        before = sorted(p.relative_to(target) for p in target.rglob("*"))
        execute_test_suite(
            language="python",
            target=target,
            test_suites_directory=test_suites_directory,
        )
        after = sorted(p.relative_to(target) for p in target.rglob("*"))
        assert after == before
