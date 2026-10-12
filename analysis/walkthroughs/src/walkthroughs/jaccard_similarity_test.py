from walkthroughs.jaccard_similarity import jaccard_similarity


def describe_jaccard_similarity():
    def it_scores_shared_lowercased_words_over_all_words():
        assert jaccard_similarity(["Parse the Grammar."], ["parse a grammar", "parse the grammar"]) == [[0.5, 1.0]]

    def it_scores_zero_when_either_side_has_no_words():
        assert jaccard_similarity(["..."], ["x"]) == [[0.0]]
