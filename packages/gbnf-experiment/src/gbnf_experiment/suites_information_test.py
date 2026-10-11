from gbnf_experiment.suites_information import suites_information


def describe_suites_information():
    def describe_when_no_suite_was_included():
        def it_says_nothing_at_all():
            assert str(
                suites_information(include_javascript_tests=False, include_python_tests=False)
            ) == ""

    def describe_when_one_suite_was_included():
        def it_names_that_suite(): 
            rendered = str(
                suites_information(include_javascript_tests=False, include_python_tests=True)
            )

            assert "/input/tests/python" in rendered

        def it_names_no_other(): 
            rendered = str(
                suites_information(include_javascript_tests=False, include_python_tests=True)
            )

            assert "javascript" not in rendered

    def describe_when_both_suites_were_included():
        def it_names_both(): 
            rendered = str(
                suites_information(include_javascript_tests=True, include_python_tests=True)
            )

            assert "/input/tests/javascript" in rendered
            assert "/input/tests/python" in rendered

        def it_gives_them_a_line_each(): 
            rendered = str(
                suites_information(include_javascript_tests=True, include_python_tests=True)
            )

            assert "/input/tests/javascript, written in javascript.\n- /input/tests/python" in rendered

    def describe_the_text_it_renders():
        def it_leaves_no_placeholder_behind():
            rendered = str(
                suites_information(include_javascript_tests=True, include_python_tests=True)
            )

            assert "{" not in rendered

        def it_says_nothing_about_iterating_to_green():
            rendered = str(
                suites_information(include_javascript_tests=True, include_python_tests=True)
            )

            assert "green" not in rendered
            assert "iterate" not in rendered
