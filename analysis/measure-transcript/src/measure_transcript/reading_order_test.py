from measure_transcript.reading_order import reading_order

INIT = "/input/python/gbnf/__init__.py"
GRAPH = "/input/python/gbnf/graph.py"
TEST = "/input/python/tests/a_test.py"


def describe_reading_order():
    def it_names_the_first_read_and_its_class():
        result = reading_order([(TEST, "source_tests", 0), (INIT, "source", 0)], 0, 0, "python")
        assert (result["first_read_path"], result["first_read_class"]) == (TEST, "source_tests")

    def it_lists_source_paths_in_order_of_first_read():
        reads = [(GRAPH, "source", 0), (TEST, "source_tests", 0), (INIT, "source", 0), (GRAPH, "source", 1)]
        assert reading_order(reads, 1, 0, "python")["read_order"] == [GRAPH, INIT]

    def it_checks_the_first_source_read_against_the_entry_point():
        assert reading_order([(TEST, "source_tests", 0), (INIT, "source", 0)], 0, 0, "python")["first_read_is_entry_point"] is True
        assert reading_order([(GRAPH, "source", 0), (INIT, "source", 0)], 0, 0, "python")["first_read_is_entry_point"] is False
        index = "/input/javascript/src/index.ts"
        assert reading_order([(index, "source", 0)], 0, 0, "javascript")["first_read_is_entry_point"] is True
        assert reading_order([(TEST, "source_tests", 0)], 0, 0, "python")["first_read_is_entry_point"] is None

    def it_skips_files_that_are_not_code_and_unexpanded_paths_for_the_entry_point():
        reads = [("/input/python/README.md", "source", 0), ("/input/python/gbnf/$f", "source", 0), ("/input/python/gbnf/*.py", "source", 0), (INIT, "source", 0)]
        assert reading_order(reads, 0, 0, "python")["first_read_is_entry_point"] is True
        assert reading_order(reads[:3], 0, 0, "python")["first_read_is_entry_point"] is None

    def it_counts_distinct_files_read_before_the_first_write():
        reads = [(GRAPH, "source", 0), (GRAPH, "source", 0), (TEST, "source_tests", 0), (INIT, "source", 1)]
        result = reading_order(reads, 2, 0, "python")
        assert (result["files_read_before_first_write"], result["source_files_read_before_first_write"]) == (2, 1)

    def it_counts_rereads_and_the_most_reread_file():
        reads = [(GRAPH, "source", 0), (INIT, "source", 0), (GRAPH, "source", 0), (INIT, "source", 0), (GRAPH, "source", 1)]
        result = reading_order(reads, 1, 0, "python")
        assert (result["reread_count"], result["max_rereads_of_one_file"], result["max_rereads_path"]) == (3, 2, GRAPH)

    def it_divides_search_calls_by_distinct_files_read():
        assert reading_order([(GRAPH, "source", 0), (GRAPH, "source", 0), (INIT, "source", 0)], 0, 3, "python")["search_calls_per_file_read"] == 1.5

    def it_counts_reads_after_the_last_write():
        reads = [(GRAPH, "source", 0), (INIT, "source", 1), (GRAPH, "source", 2), (TEST, "source_tests", 2)]
        assert reading_order(reads, 2, 0, "python")["reads_after_last_write"] == 2

    def it_leaves_measures_null_without_reads_or_writes():
        assert reading_order([], 0, 2, "python") == {
            "first_read_path": None,
            "first_read_class": None,
            "first_read_is_entry_point": None,
            "files_read_before_first_write": None,
            "source_files_read_before_first_write": None,
            "reread_count": 0,
            "max_rereads_of_one_file": 0,
            "max_rereads_path": None,
            "search_calls_per_file_read": None,
            "read_order": [],
            "reads_after_last_write": None,
        }
