import json

from execute_test_suite.read_adapt_report import read_adapt_report


def describe_read_adapt_report():
    def it_returns_the_fired_rules_as_a_tuple(tmp_path):
        path = tmp_path / "adapt.json"
        path.write_text(json.dumps({"rules_fired": ["flat_module", "state_add"]}))
        assert read_adapt_report(path) == ("flat_module", "state_add")

    def it_returns_an_empty_tuple_when_the_shim_never_wrote_a_report(tmp_path):
        assert read_adapt_report(tmp_path / "adapt.json") == ()
