from measure_ast.levenshtein import levenshtein


def describe_levenshtein():
    def it_is_zero_between_equal_sequences():
        assert levenshtein(["a", "b"], ["a", "b"]) == 0

    def it_counts_an_insert_a_delete_and_a_substitution():
        assert levenshtein(["a", "b", "c"], ["a", "c", "d"]) == 2
        assert levenshtein(["a", "b"], ["x", "b"]) == 1

    def it_is_the_other_length_against_an_empty_sequence():
        assert levenshtein([], ["a", "b", "c"]) == 3
        assert levenshtein(["a"], []) == 1
