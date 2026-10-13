from export_embedding_pairs import pair_chart


def describe_pair_chart():
    def it_draws_no_chart_when_there_are_no_comparisons():
        # An altair chart over zero rows renders in marimo as a canvas 3.4e38 px tall,
        # which pushes every later cell out of the page.
        assert pair_chart([], "python", "typescript") is None

    def it_draws_a_chart_when_there_are_comparisons():
        row = {
            "source_language": "python", "target_language": "typescript",
            "comparison": "port-to-reference", "chamfer_distance": 0.02,
            "include_python_tests_a": False, "include_typescript_tests_a": False,
            "include_python_tests_b": False, "include_typescript_tests_b": False,
        }
        assert pair_chart([row], "python", "typescript") is not None
