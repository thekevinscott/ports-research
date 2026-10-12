import re

from judge.item_id import item_id


def describe_item_id():
    def it_is_item_dash_eight_hex():
        assert re.fullmatch(r"item-[0-9a-f]{8}", item_id("content"))

    def it_is_the_same_for_the_same_content():
        assert item_id("content") == item_id("content")

    def it_differs_for_different_content():
        assert item_id("content") != item_id("contents")

    def it_is_pinned_to_seed_zero():
        assert item_id("content") == "item-4005cb9a"
