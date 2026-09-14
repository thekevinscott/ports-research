import json

from contamination_probe.write_rename_manifest import write_rename_manifest


def describe_write_rename_manifest():
    def it_writes_the_library_name_and_symbol_rename_map_as_json(tmp_path):
        manifest_path = tmp_path / "rename-manifest.json"

        write_rename_manifest(
            manifest_path,
            library_name={"old": "gbnf", "new": "moraine_quarry"},
            symbol_rename_map={"GBNF": "HollowInlet", "RuleChar": "CinderMarsh"},
        )

        manifest = json.loads(manifest_path.read_text())
        assert manifest["library_name"] == {"old": "gbnf", "new": "moraine_quarry"}
        assert manifest["symbols"] == {"GBNF": "HollowInlet", "RuleChar": "CinderMarsh"}
