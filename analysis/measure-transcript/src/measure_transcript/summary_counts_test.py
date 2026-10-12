from measure_transcript.summary_counts import summary_counts


def describe_summary_counts():
    def it_reads_pytest_summaries():
        assert summary_counts("===== 3 failed, 770 passed in 1.23s =====") == [{"passed": 770, "failed": 3}]
        assert summary_counts("773 passed, 2 warnings in 0.50s") == [{"passed": 773, "failed": 0}]
        assert summary_counts("1 failed, 2 passed, 1 error in 61.02s (0:01:01)") == [{"passed": 2, "failed": 1}]

    def it_skips_summaries_without_pass_or_fail_counts():
        assert summary_counts("no tests ran in 0.01s\n5 errors in 0.2s") == []

    def it_reads_vitest_summaries_and_ignores_test_files():
        text = " Test Files  1 failed | 5 passed (6)\n      Tests  1 failed | 772 passed (773)\n"
        assert summary_counts(text) == [{"passed": 772, "failed": 1}]

    def it_strips_ansi_colors():
        assert summary_counts("\x1b[2m      Tests \x1b[22m \x1b[1m\x1b[32m773 passed\x1b[39m\x1b[22m (773)") == [{"passed": 773, "failed": 0}]

    def it_reads_jest_summaries():
        assert summary_counts("Tests:       1 failed, 2 passed, 3 total") == [{"passed": 2, "failed": 1}]

    def it_reads_node_test_summaries():
        assert summary_counts("# tests 6\n# pass 5\n# fail 1\n") == [{"passed": 5, "failed": 1}]
        assert summary_counts("ℹ pass 5\nℹ fail 0\n") == [{"passed": 5, "failed": 0}]

    def it_keeps_the_order_the_summaries_appear_in():
        text = "      Tests  10 passed (10)\n2 failed, 1 passed in 0.1s\n"
        assert summary_counts(text) == [{"passed": 10, "failed": 0}, {"passed": 1, "failed": 2}]
