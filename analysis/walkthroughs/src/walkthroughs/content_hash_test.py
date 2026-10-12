from walkthroughs.content_hash import content_hash


def describe_content_hash():
    def it_is_stable_for_the_same_prompt_model_effort_and_tag():
        assert content_hash("p", "m", "e", "") == content_hash("p", "m", "e", "")

    def it_changes_with_each_input():
        hashes = {content_hash(*args) for args in [("p", "m", "e", ""), ("q", "m", "e", ""), ("p", "n", "e", ""), ("p", "m", "f", ""), ("p", "m", "e", "a")]}
        assert len(hashes) == 5

    def it_is_sixteen_hex_characters():
        assert len(content_hash("p", "m", "e", "")) == 16
        int(content_hash("p", "m", "e", ""), 16)
