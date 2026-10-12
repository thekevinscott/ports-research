from measure_transcript.reference_path import reference_path

COPIES = {"/target/t": "/input/python/tests", "/target/t/generated": "/input/javascript/integration-tests/generated"}


def describe_reference_path():
    def it_maps_a_path_under_a_copy_back_to_its_origin():
        assert reference_path("/target/t/a_test.py", COPIES) == "/input/python/tests/a_test.py"

    def it_uses_the_longest_matching_copy():
        assert reference_path("/target/t/generated/x.ts", COPIES) == "/input/javascript/integration-tests/generated/x.ts"

    def it_maps_the_copy_root_itself():
        assert reference_path("/target/t", COPIES) == "/input/python/tests"

    def it_matches_whole_path_components_only():
        assert reference_path("/target/tests", COPIES) == "/target/tests"
