from execute_test_suite import execute_test_suite


def describe_execute_test_suite():
    def describe_a_python_port():
        def it_reports_a_passing_suite(
            derivations_directory, derivation_cache_key, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(42),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
            )
            assert report["success"] is True
            assert report["total"] == 2
            assert report["passed"] == 2
            assert report["failed"] == 0

        def it_reports_a_failing_suite(
            derivations_directory, derivation_cache_key, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(0),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
            )
            assert report["success"] is False
            assert report["total"] == 2
            assert report["failed"] == 2

        def it_runs_only_the_grammar_fixtures_as_the_integration_suite(
            derivations_directory, derivation_cache_key, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(42),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
                suite="integration",
            )
            assert report["suite"] == "integration"
            assert report["total"] == 1

        def it_runs_everything_but_the_grammar_fixtures_as_the_unit_suite(
            derivations_directory, derivation_cache_key, python_target
        ):
            report = execute_test_suite(
                language="python",
                target=python_target(42),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
                suite="unit",
            )
            assert report["suite"] == "unit"
            assert report["total"] == 1

    def describe_a_typescript_port():
        def it_reports_a_passing_suite(
            derivations_directory, derivation_cache_key, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(42),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
            )
            assert report["success"] is True
            assert report["passed"] == 2

        def it_reports_a_failing_suite(
            derivations_directory, derivation_cache_key, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(0),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
            )
            assert report["success"] is False
            assert report["failed"] == 2

        def it_grades_a_port_whose_tsconfig_extends_a_missing_file(
            derivations_directory,
            derivation_cache_key,
            typescript_unresolvable_tsconfig_target,
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_unresolvable_tsconfig_target,
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
            )
            assert report["success"] is True
            assert report["passed"] == 2

        def it_runs_only_the_grammar_spec_as_the_integration_suite(
            derivations_directory, derivation_cache_key, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(42),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
                suite="integration",
            )
            assert report["total"] == 1

        def it_runs_everything_but_the_grammar_spec_as_the_unit_suite(
            derivations_directory, derivation_cache_key, typescript_target
        ):
            report = execute_test_suite(
                language="typescript",
                target=typescript_target(42),
                derivations_directory=derivations_directory,
                derivation_cache_key=derivation_cache_key,
                suite="unit",
            )
            assert report["total"] == 1

    def it_grades_javascript_against_the_same_suite_as_typescript(
        derivations_directory, derivation_cache_key, typescript_target
    ):
        report = execute_test_suite(
            language="javascript",
            target=typescript_target(42),
            derivations_directory=derivations_directory,
            derivation_cache_key=derivation_cache_key,
        )
        assert report["test_suite_directory"] == str(
            derivations_directory / derivation_cache_key / "tests" / "typescript"
        )
        assert report["success"] is True

    def it_never_writes_into_the_derivation_cache(
        derivations_directory, derivation_cache_key, python_target
    ):
        before = sorted(
            p.relative_to(derivations_directory) for p in derivations_directory.rglob("*")
        )
        execute_test_suite(
            language="python",
            target=python_target(42),
            derivations_directory=derivations_directory,
            derivation_cache_key=derivation_cache_key,
        )
        after = sorted(
            p.relative_to(derivations_directory) for p in derivations_directory.rglob("*")
        )
        assert after == before

    def it_never_writes_into_the_target(
        derivations_directory, derivation_cache_key, python_target
    ):
        target = python_target(42)
        before = sorted(p.relative_to(target) for p in target.rglob("*"))
        execute_test_suite(
            language="python",
            target=target,
            derivations_directory=derivations_directory,
            derivation_cache_key=derivation_cache_key,
        )
        after = sorted(p.relative_to(target) for p in target.rglob("*"))
        assert after == before
