import json
from pathlib import Path
import xml.etree.ElementTree as ET

import altair as alt
import pytest

from copy import deepcopy

from src.chart_export import dark_spec, fit_pair, write_chart

CHARTS = Path(__file__).resolve().parents[1] / "charts"


@pytest.mark.parametrize("source", sorted(p for p in CHARTS.rglob("*.json")
    if p.name.startswith(("size-", "ladder-ref-ratio-", "port-to-port-matrix-"))))
def test_exports_transparent_dark_sibling_with_same_geometry_and_data(tmp_path, source):
    """Blog dark mode must not display an opaque white chart slab."""
    spec = json.loads(source.read_text())
    chart = alt.Chart.from_dict(spec)
    before = chart.to_dict()
    paths = write_chart(chart, tmp_path / source.stem)
    dark_path = tmp_path / (source.stem + "-dark.svg")
    assert dark_path in paths
    exported_spec = json.loads((tmp_path / (source.stem + ".json")).read_text())
    assert exported_spec["config"]["axis"]["labelAngle"] == -45
    light = ET.parse(tmp_path / (source.stem + ".svg")).getroot()
    dark = ET.parse(dark_path).getroot()
    assert light.attrib == dark.attrib
    # Every label and mark keeps its geometry; Vega omits a transparent background.
    light_nodes = [n for n in light.iter() if not (n.tag.endswith('rect') and n.get('fill') == 'white')]
    dark_nodes = list(dark.iter())
    assert len(light_nodes) == len(dark_nodes)
    for a, b in zip(light_nodes, dark_nodes):
        assert a.tag == b.tag and a.text == b.text
        assert {k: v for k, v in a.attrib.items() if k not in {'fill', 'stroke', 'stop-color', 'id'}} == {k: v for k, v in b.attrib.items() if k not in {'fill', 'stroke', 'stop-color', 'id'}}
    svg = dark_path.read_text()
    assert 'fill="white"' not in svg
    for color in ('#d8d3ca', '#f3f1ec', '#2e2b26'):
        assert color in svg
    assert chart.to_dict() == before


def test_matrix_dark_scale_preserves_domain_data_and_categorical_palette():
    spec = json.loads((CHARTS / "statistical-analysis/port-to-port-matrix-python-to-typescript.json").read_text())
    dark = dark_spec(spec, "port-to-port-matrix-python-to-typescript")
    assert dark["datasets"] == spec["datasets"]
    for light_layer, dark_layer in zip(spec["layer"], dark["layer"]):
        light_color = light_layer.get("encoding", {}).get("color", {})
        dark_color = dark_layer.get("encoding", {}).get("color", {})
        if light_color.get("type") == "quantitative":
            assert dark_color["scale"]["domain"] == light_color["scale"]["domain"]
            assert dark_color["scale"]["range"][0] == "#161513"
            assert dark_color["scale"]["range"][-1] == "#256abf"
        elif light_color.get("type") == "nominal":
            assert dark_color == light_color


def test_future_grid_charts_export_both_variants(tmp_path):
    chart = alt.Chart(alt.Data(values=[{"x": 1, "y": 2}])).mark_point().encode(x="x:Q", y="y:Q")
    paths = write_chart(chart, tmp_path / "port-to-port-grid-python-to-typescript")
    assert {p.name for p in paths} >= {
        "port-to-port-grid-python-to-typescript.svg",
        "port-to-port-grid-python-to-typescript-dark.svg",
    }


def fake_geometry(spec):
    """Deterministic stand-in for rendered_geometry: totals from widths and paddings."""

    def pad(unit, channel):
        extra = 0
        for layer in unit.get("layer", [unit]):
            enc = layer.get("encoding", {}).get(channel, {})
            extra = max(extra, enc.get("axis", {}).get("labelPadding", 2) - 2)
        return extra

    units = spec.get("concat", [spec])
    padding = spec.get("padding", 5)
    right = padding.get("right", 5) if isinstance(padding, dict) else padding
    left = 30 + pad(units[0], "y")
    width = left + sum(unit.get("width", 100) for unit in units) + (right - 5) + 7
    height = 50 + 200 + pad(units[0], "x")
    return (width, height, left, 50)


def layered(width, left_pad=2, bottom_pad=2):
    """A two-panel concat in the size chart's shape."""
    return {
        "data": {"values": []},
        "concat": [
            {
                "width": width,
                "layer": [
                    {
                        "encoding": {
                            "x": {"field": "c", "axis": {"labelPadding": bottom_pad}},
                            "y": {"field": "v", "axis": {"labelPadding": left_pad}},
                        }
                    }
                ],
            }
            for _ in range(2)
        ],
    }


def test_fit_pair_aligns_slot_geometry():
    """A blog slot pair shares one width, one left margin and one height."""
    short_left = layered(131.25, bottom_pad=4)  # 30px left margin, 252px tall
    wide_left = layered(131.25, left_pad=8)  # 36px left margin, 250px tall
    originals = [deepcopy(short_left), deepcopy(wide_left)]
    fitted = fit_pair([short_left, wide_left], 370.5, measure=fake_geometry)
    assert [fake_geometry(spec) for spec in fitted] == [(370.5, 252, 36, 50)] * 2
    assert [short_left, wide_left] == originals  # inputs are never mutated


def test_fit_pair_grows_single_view_plots_and_keeps_matrices_square():
    single = {"data": {"values": []}, "width": 290, "height": 300,
              "layer": [{"encoding": {"x": {"field": "c"}, "y": {"field": "v"}}}]}
    matrix = {"data": {"values": []}, "width": 630, "height": 630,
              "layer": [{"encoding": {"x": {"field": "a"}, "y": {"field": "b"}}}]}
    (fitted,) = fit_pair([single], 370.5, measure=fake_geometry)
    assert fake_geometry(fitted) == (370.5, 250, 30, 50)
    assert fitted["width"] > 290  # the plot itself grew; padding only closes the rest
    (fitted_matrix,) = fit_pair([matrix], 757, measure=fake_geometry)
    assert fake_geometry(fitted_matrix)[0] == 757
    assert fitted_matrix["width"] == fitted_matrix["height"]
