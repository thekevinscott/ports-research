from judge.shuffle_items import shuffle_items

ITEMS = [{"id": f"item-{n:08x}"} for n in range(10)]


def describe_shuffle_items():
    def it_orders_the_same_items_the_same_way_whatever_order_they_arrive_in():
        assert shuffle_items(ITEMS) == shuffle_items(list(reversed(ITEMS)))

    def it_keeps_every_item():
        assert sorted(shuffle_items(ITEMS), key=lambda item: item["id"]) == ITEMS

    def it_is_pinned_to_seed_zero():
        assert [item["id"][-1] for item in shuffle_items(ITEMS)] == list("7815342096")
