def describe_adapt():
    def it_reports_a_python_port_needing_no_adaptation_identically_either_way(
        grade, python_target
    ):
        target = python_target(42)
        strict = grade("python", target, "integration")
        adapted = grade("python", target, "integration", "--adapt")
        assert adapted == {**strict, "adapt": {"rules_fired": []}}
        assert strict["passed"] == 2

    def it_reports_a_typescript_port_needing_no_adaptation_identically_either_way(
        grade, typescript_target
    ):
        target = typescript_target(42)
        strict = grade("typescript", target, "integration")
        adapted = grade("typescript", target, "integration", "--adapt")
        assert adapted == {**strict, "adapt": {"rules_fired": []}}
        assert strict["passed"] == 2

    def describe_a_typescript_port_with_only_a_named_gbnf():
        def it_fails_every_test_strictly(grade, typescript_named_target):
            report = grade("typescript", typescript_named_target, "integration")
            assert report["success"] is False
            assert report["passed"] == 0

        def it_passes_through_the_default_export_rule(grade, typescript_named_target):
            report = grade("typescript", typescript_named_target, "integration", "--adapt")
            assert report["success"] is True
            assert report["passed"] == 2
            assert report["adapt"] == {"rules_fired": ["default_export"]}

    def describe_a_flat_python_port():
        def it_errors_at_collection_strictly(grade, python_flat_target):
            report = grade("python", python_flat_target, "integration")
            assert report["success"] is False
            assert report["passed"] == 0
            assert report["errors"] > 0

        def it_passes_through_all_three_python_rules(grade, python_flat_target):
            report = grade("python", python_flat_target, "integration", "--adapt")
            assert report["success"] is True
            assert report["passed"] == 2
            assert report["adapt"] == {
                "rules_fired": ["flat_module", "state_add", "exception_eq"]
            }
