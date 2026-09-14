from measure_embedding.excluded import excluded


def describe_excluded():
    def it_matches_the_whole_relative_path():
        assert excluded("pkg/a.py", ["pkg/a.py"])

    def it_matches_any_single_path_part():
        assert excluded("build/lib/a.py", ["lib"])

    def it_matches_a_glob_against_the_file_name():
        assert excluded("pkg/a_test.py", ["*_test.py"])

    def it_does_not_match_a_pattern_against_a_partial_path():
        assert not excluded("pkg/a.py", ["pkg/a"])

    def it_matches_nothing_with_no_patterns():
        assert not excluded("pkg/a.py", [])
