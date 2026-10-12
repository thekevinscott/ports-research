from measure_transcript.expand_glob import expand_glob

FILES = {"/input/python/gbnf/__init__.py", "/input/python/gbnf/GBNF.py", "/input/python/gbnf/a/b.py", "/input/python/gbnf/.hidden.py", "/input/python/README.md"}


def describe_expand_glob():
    def it_lists_the_files_a_glob_names_in_sorted_order():
        assert expand_glob("/input/python/gbnf/*.py", FILES) == ["/input/python/gbnf/GBNF.py", "/input/python/gbnf/__init__.py"]

    def it_matches_one_directory_level_per_component():
        assert expand_glob("/input/python/*/*/*.py", FILES) == ["/input/python/gbnf/a/b.py"]
        assert expand_glob("/input/python/gbnf/?/[ab].py", FILES) == ["/input/python/gbnf/a/b.py"]

    def it_keeps_hidden_files_out_unless_the_pattern_starts_with_a_dot():
        assert expand_glob("/input/python/gbnf/.*.py", FILES) == ["/input/python/gbnf/.hidden.py"]

    def it_leaves_a_path_without_a_glob_or_without_a_match_as_it_is():
        assert expand_glob("/input/python/gbnf/__init__.py", FILES) == ["/input/python/gbnf/__init__.py"]
        assert expand_glob("/target/src/*.ts", FILES) == ["/target/src/*.ts"]
