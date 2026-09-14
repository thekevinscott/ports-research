from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from contamination_probe.symbol_site import SymbolSite


def describe_symbol_site():
    def it_holds_the_path_lineno_and_name(tmp_path):
        site = SymbolSite(path=tmp_path / "graph.py", lineno=37, name="Graph")
        assert site.path == tmp_path / "graph.py"
        assert site.lineno == 37
        assert site.name == "Graph"

    def it_is_frozen():
        site = SymbolSite(path=Path("graph.py"), lineno=1, name="Graph")
        with pytest.raises(FrozenInstanceError):
            site.name = "Other"

    def it_compares_equal_by_value():
        a = SymbolSite(path=Path("graph.py"), lineno=1, name="Graph")
        b = SymbolSite(path=Path("graph.py"), lineno=1, name="Graph")
        assert a == b
