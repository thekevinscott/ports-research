from measure_transcript.suite_class import suite_class

TARGET_COPY = {"/target/tests/generated": "/input/javascript/integration-tests/generated"}


def describe_suite_class():
    def it_names_a_run_inside_a_shipped_suite():
        assert suite_class(["/input/python/tests/generated"], "python", {}, []) == "source_tests"
        assert suite_class(["/input/python/gbnf"], "python", {}, []) == "source_tests"
        assert suite_class(["/target/tests/generated/x.test.ts"], "python", TARGET_COPY, []) == "target_tests"

    def it_names_a_directory_that_holds_only_a_copied_suite():
        assert suite_class(["/target"], "python", TARGET_COPY, []) == "target_tests"

    def it_names_the_agents_own_tests():
        assert suite_class(["/target/src"], "python", TARGET_COPY, ["/target/src/a.test.ts"]) == "own_tests"

    def it_is_unknown_when_a_directory_mixes_suites():
        assert suite_class(["/target"], "python", TARGET_COPY, ["/target/src/a.test.ts"]) == "unknown"
        assert suite_class(["/input"], "python", {}, []) == "unknown"

    def it_names_anything_the_reference_did_not_reach_the_agents_own():
        assert suite_class(["/target/src"], "python", {}, []) == "own_tests"
        assert suite_class(["/target/src/x.test.ts"], "python", {"/target/src/x.test.ts": "/tmp/x.test.ts"}, []) == "own_tests"
        assert suite_class(["/tmp/x"], "python", {}, []) == "own_tests"

    def it_ignores_copied_config_files():
        copies = {**TARGET_COPY, "/target/pyproject.toml": "/input/python/pyproject.toml", "/target/Makefile": "/input/python/Makefile"}
        assert suite_class(["/target"], "python", copies, []) == "target_tests"

    def it_is_unknown_when_paths_reach_different_suites():
        assert suite_class(["/input/python/tests", "/tmp/x"], "python", {}, []) == "unknown"
