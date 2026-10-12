from walkthroughs.longest_increasing import longest_increasing


def describe_longest_increasing():
    def it_is_zero_for_nothing():
        assert longest_increasing([]) == 0

    def it_is_the_whole_length_when_already_in_order():
        assert longest_increasing([0, 2, 3, 7]) == 4

    def it_is_one_when_fully_reversed():
        assert longest_increasing([3, 2, 1, 0]) == 1

    def it_skips_the_values_out_of_order():
        assert longest_increasing([0, 4, 1, 2, 3]) == 4

    def it_counts_strictly_increasing_only():
        assert longest_increasing([1, 1, 1]) == 1
