import json
from pathlib import Path

import pytest

from execute_test_suite.adapt_typescript import RULES, adapt_typescript

PORT_ENTRY = Path("/data/run/ported_implementation/src/index.ts")
REPORT_PATH = Path("/scratch/adapt.json")


@pytest.fixture
def shim(tmp_path):
    return adapt_typescript(tmp_path / "shim", port_entry=PORT_ENTRY, report_path=REPORT_PATH)


def describe_adapt_typescript():
    def it_names_the_one_typescript_rule():
        assert RULES == ("default_export",)

    def it_writes_an_index_ts_into_the_directory(shim, tmp_path):
        assert shim == tmp_path / "shim" / "index.ts"
        assert shim.is_file()

    def it_re_exports_everything_from_the_port_entry(shim):
        assert f"export * from {json.dumps(str(PORT_ENTRY))};" in shim.read_text()

    def it_falls_back_to_the_named_gbnf_as_the_default_export(shim):
        text = shim.read_text()
        assert "export default" in text
        assert "GBNF" in text

    def it_records_the_default_export_rule_at_the_report_path(shim):
        text = shim.read_text()
        assert json.dumps(str(REPORT_PATH)) in text
        assert '"default_export"' in text

    def it_creates_the_directory(tmp_path):
        adapt_typescript(tmp_path / "a" / "b", port_entry=PORT_ENTRY, report_path=REPORT_PATH)
        assert (tmp_path / "a" / "b" / "index.ts").is_file()
