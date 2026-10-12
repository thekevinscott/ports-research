from judge.replicate_items import replicate_items

ITEMS = [{"id": f"item-{n:08x}", "entry": {"baseline": n < 2}} for n in range(1000)]


def ids(items):
    return [item["id"] for item in items]


def describe_replicate_items():
    def it_replicates_nothing_at_zero_not_even_the_baselines():
        assert replicate_items(ITEMS, 0) == []

    def it_always_replicates_the_baselines():
        assert ids(replicate_items(ITEMS, 1e-9)) == ["item-00000000", "item-00000001"]

    def it_replicates_every_item_at_one():
        assert replicate_items(ITEMS, 1) == ITEMS

    def it_replicates_about_the_fraction_asked():
        assert 70 <= len(replicate_items(ITEMS, 0.1)) <= 130

    def it_picks_an_item_whatever_other_items_come_with_it():
        picked = set(ids(replicate_items(ITEMS, 0.1)))
        assert set(ids(replicate_items(ITEMS[500:], 0.1))) == {i for i in picked if i in ids(ITEMS[500:])}

    def it_keeps_the_order_items_arrive_in():
        assert ids(replicate_items(list(reversed(ITEMS)), 0.5)) == list(reversed(ids(replicate_items(ITEMS, 0.5))))

    def it_is_pinned_to_seed_zero():
        assert [i[-2:] for i in ids(replicate_items(ITEMS[2:22], 0.5))] == ["02", "03", "04", "05", "06", "07", "08", "09", "0a", "0c", "0d", "0f", "11", "14", "15"]
