from contamination_probe.build_rename_map import build_rename_map


def describe_build_rename_map():
    def it_maps_every_unique_name(monkeypatch):
        rename_map = build_rename_map(["Graph", "GraphNode", "Graph"], seed=0)
        assert set(rename_map) == {"Graph", "GraphNode"}

    def it_is_deterministic_for_a_given_seed():
        assert build_rename_map(["Graph", "GraphNode"], seed=0) == build_rename_map(
            ["Graph", "GraphNode"], seed=0
        )

    def it_varies_with_seed():
        assert build_rename_map(["Graph", "GraphNode"], seed=0) != build_rename_map(
            ["Graph", "GraphNode"], seed=1
        )

    def it_never_maps_a_name_to_itself():
        rename_map = build_rename_map(["Graph", "GraphNode", "RootNode"], seed=0)
        for old_name, new_name in rename_map.items():
            assert old_name != new_name

    def it_never_produces_duplicate_replacement_names():
        rename_map = build_rename_map(["Graph", "GraphNode", "RootNode", "Pointers"], seed=0)
        assert len(set(rename_map.values())) == len(rename_map)

    def it_returns_an_empty_map_for_no_names():
        assert build_rename_map([], seed=0) == {}
