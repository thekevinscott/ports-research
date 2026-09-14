from execute_test_suite import execute_test_suite

STRICT_REPORT_KEYS = {
    "language",
    "suite",
    "target",
    "test_suite_directory",
    "total",
    "passed",
    "failed",
    "errors",
    "skipped",
    "success",
}


def grade(language, target, derivations_directory, derivation_cache_key, **kwargs):
    return execute_test_suite(
        language=language,
        target=target,
        derivations_directory=derivations_directory,
        derivation_cache_key=derivation_cache_key,
        **kwargs,
    )


def describe_adapt():
    def describe_strict_path():
        def it_keeps_the_report_shape_it_had_before_adapt_existed(
            derivations_directory, derivation_cache_key, python_target
        ):
            report = grade("python", python_target(42), derivations_directory, derivation_cache_key)
            assert set(report) == STRICT_REPORT_KEYS

        def it_reports_a_python_port_needing_no_adaptation_identically_either_way(
            derivations_directory, derivation_cache_key, python_target
        ):
            target = python_target(42)
            strict = grade("python", target, derivations_directory, derivation_cache_key)
            adapted = grade(
                "python", target, derivations_directory, derivation_cache_key, adapt=True
            )
            assert adapted == {**strict, "adapt": {"rules_fired": []}}
            assert strict["passed"] == 2

        def it_reports_a_typescript_port_needing_no_adaptation_identically_either_way(
            derivations_directory, derivation_cache_key, typescript_target
        ):
            target = typescript_target(42)
            strict = grade("typescript", target, derivations_directory, derivation_cache_key)
            adapted = grade(
                "typescript", target, derivations_directory, derivation_cache_key, adapt=True
            )
            assert adapted == {**strict, "adapt": {"rules_fired": []}}
            assert strict["passed"] == 2

    def describe_a_typescript_port_with_only_a_named_gbnf():
        def it_fails_every_test_strictly(
            derivations_directory, derivation_cache_key, typescript_named_target
        ):
            report = grade(
                "typescript", typescript_named_target, derivations_directory, derivation_cache_key
            )
            assert report["success"] is False
            assert report["passed"] == 0

        def it_passes_through_the_default_export_rule(
            derivations_directory, derivation_cache_key, typescript_named_target
        ):
            report = grade(
                "typescript",
                typescript_named_target,
                derivations_directory,
                derivation_cache_key,
                adapt=True,
            )
            assert report["success"] is True
            assert report["passed"] == 2
            assert report["adapt"] == {"rules_fired": ["default_export"]}

    def describe_a_flat_python_port():
        def it_errors_at_collection_strictly(
            derivations_directory, derivation_cache_key, python_flat_target
        ):
            report = grade("python", python_flat_target, derivations_directory, derivation_cache_key)
            assert report["success"] is False
            assert report["passed"] == 0
            assert report["errors"] > 0

        def it_passes_through_all_three_python_rules(
            derivations_directory, derivation_cache_key, python_flat_target
        ):
            report = grade(
                "python", python_flat_target, derivations_directory, derivation_cache_key, adapt=True
            )
            assert report["success"] is True
            assert report["passed"] == 2
            assert report["adapt"] == {
                "rules_fired": ["flat_module", "state_add", "exception_eq"]
            }

        def it_narrows_to_the_integration_suite_under_adapt(
            derivations_directory, derivation_cache_key, python_flat_target
        ):
            report = grade(
                "python",
                python_flat_target,
                derivations_directory,
                derivation_cache_key,
                suite="integration",
                adapt=True,
            )
            assert report["suite"] == "integration"
            assert report["total"] == 1
            assert report["passed"] == 1

    def it_never_writes_into_the_target(
        derivations_directory, derivation_cache_key, python_flat_target
    ):
        before = sorted(p.relative_to(python_flat_target) for p in python_flat_target.rglob("*"))
        grade("python", python_flat_target, derivations_directory, derivation_cache_key, adapt=True)
        after = sorted(p.relative_to(python_flat_target) for p in python_flat_target.rglob("*"))
        assert after == before

    def it_never_writes_into_the_derivation_cache(
        derivations_directory, derivation_cache_key, typescript_named_target
    ):
        before = sorted(
            p.relative_to(derivations_directory) for p in derivations_directory.rglob("*")
        )
        grade(
            "typescript",
            typescript_named_target,
            derivations_directory,
            derivation_cache_key,
            adapt=True,
        )
        after = sorted(
            p.relative_to(derivations_directory) for p in derivations_directory.rglob("*")
        )
        assert after == before
