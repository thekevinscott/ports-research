import json
from pathlib import Path
import xml.etree.ElementTree as ET

import altair as alt
import pytest

from copy import deepcopy

from src.chart_export import (
    DARK_BLUE_RAMP,
    TITLE,
    align_panel_titles,
    dark_spec,
    fit_pair,
    share_y_domains,
    write_chart,
)

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
    assert exported_spec["config"]["axisX"]["labelAngle"] == -37.5
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
            assert dark_color["scale"]["range"] == DARK_BLUE_RAMP
        elif light_color.get("type") == "nominal":
            # Category colours survive; only the ink (the reference swatch) lifts.
            assert dark_color["scale"]["range"] == [
                TITLE if colour == "#0b0b0b" else colour
                for colour in light_color["scale"]["range"]
            ]


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


def test_dark_spec_recolors_ink_in_categorical_scale_ranges():
    """The matrix's reference swatch is ink; on a dark page it must not stay dark."""
    spec = {
        "data": {"values": []},
        "mark": "rect",
        "encoding": {
            "color": {"field": "c", "scale": {"domain": ["a", "b"], "range": ["#2a78d6", "#0b0b0b"]}}
        },
        "config": {"axis": {}},
    }
    dark = dark_spec(spec, "size-python-to-typescript")
    assert dark["encoding"]["color"]["scale"]["range"] == ["#2a78d6", TITLE]


def test_dark_ramp_floors_above_the_page_background():
    """The lowest stop must read as data, not as the empty triangle, on a near-black page."""
    floor = DARK_BLUE_RAMP[0].lstrip("#")
    brightness = sum(int(floor[i : i + 2], 16) for i in (0, 2, 4))
    assert brightness > 120  # the old floor #161513 scored 61 and vanished


def test_align_panel_titles_moves_panel_titles_onto_their_plots():
    """Panel titles anchor to the panel's left edge; they belong over the plot area."""
    spec = {
        "title": {"text": "chart"},
        "concat": [
            {"title": {"text": "a"}, "width": 100},
            {"title": {"text": "b"}, "width": 100},
        ],
    }

    def fake_positions(s):
        plots = [40.0, 205.0]
        titles = [base + unit["title"].get("dx", 0)
                  for base, unit in zip((6.2, 190.0), s["concat"])]
        if s.get("title"):
            titles.append(5.2)  # the chart title renders after the panel titles
        return plots, titles

    aligned = align_panel_titles(spec, measure=fake_positions)
    assert [unit["title"]["dx"] for unit in aligned["concat"]] == [33.8, 15.0]
    assert "dx" not in spec["concat"][0]["title"]  # the input is never mutated
    assert align_panel_titles(aligned, measure=fake_positions) == aligned  # idempotent


def _size_like(panel_rows):
    return {
        "datasets": {f"d{i}": rows for i, rows in enumerate(panel_rows)},
        "concat": [
            {
                "data": {"name": f"d{i}"},
                "layer": [
                    {"encoding": {"y": {"field": "value", "scale": {"zero": False}}}},
                    {"encoding": {"y": {"field": "reference", "scale": {"zero": False}}}},
                ],
            }
            for i in range(2)
        ],
    }


def test_share_y_domains_gives_a_pair_one_domain_per_panel():
    a = _size_like([[{"value": 30, "reference": 28}], [{"value": 1000, "reference": 900}]])
    b = _size_like([[{"value": 150, "reference": 140}], [{"value": 2000, "reference": 2100}]])
    shared = share_y_domains([a, b])
    domains = [
        [unit["layer"][0]["encoding"]["y"]["scale"]["domain"] for unit in spec["concat"]]
        for spec in shared
    ]
    assert domains[0] == domains[1]
    assert domains[0][0] == [28 - 122 * 0.08, 150 + 122 * 0.08]  # 8% pad on the union span
    assert domains[0][1] == [900 - 1200 * 0.08, 2100 + 1200 * 0.08]
    # every y encoding carries the domain, and the inputs are never mutated
    assert shared[0]["concat"][0]["layer"][1]["encoding"]["y"]["scale"]["domain"] == domains[0][0]
    assert a["concat"][0]["layer"][0]["encoding"]["y"]["scale"] == {"zero": False}


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


def test_matrix_axes_drop_the_empty_column_and_row():
    # Cells exist only above the diagonal, so the first column and last row are blank.
    for direction in ("python-to-typescript", "typescript-to-python"):
        spec = json.loads(
            (CHARTS / f"statistical-analysis/port-to-port-matrix-{direction}.json").read_text()
        )
        cells, header, sidebar = spec["layer"][:3]
        x_blocks, y_blocks = spec["layer"][-4:-2]
        x_items = cells["encoding"]["x"]["scale"]["domain"]
        y_items = cells["encoding"]["y"]["scale"]["domain"]
        # Exactly one item differs each way: x keeps the reference, y keeps the first port.
        assert [p for p in x_items if p not in y_items] == [x_items[-1]]
        assert [p for p in y_items if p not in x_items] == [y_items[0]]
        rows = lambda layer: [r["port"] for r in spec["datasets"][layer["data"]["name"]]]
        assert rows(header) == [p for p in x_items if p != "reference"]
        assert rows(sidebar) == y_items
        # The reference block boxes the reference column on x but has no row on y.
        assert len(rows(y_blocks)) == len(rows(x_blocks)) - 1


def test_matrix_names_the_reference_and_keeps_the_strips_to_conditions():
    """The reference is the point of the chart: it earns an axis label, not a swatch."""
    for direction in ("python-to-typescript", "typescript-to-python"):
        spec = json.loads(
            (CHARTS / f"statistical-analysis/port-to-port-matrix-{direction}.json").read_text()
        )
        cells, header, sidebar = spec["layer"][:3]
        assert cells["encoding"]["x"]["scale"]["domain"][-1] == "reference"
        for axis in ("x", "y"):
            expr = cells["encoding"][axis]["axis"]["labelColor"]["expr"]
            assert "datum.label === 'reference'" in expr
        assert "" not in {value for rows in spec["datasets"].values()
                          for row in rows for value in row.values()}
        for strip in (header, sidebar):
            scale = strip["encoding"]["color"]["scale"]
            assert "reference" not in scale["domain"]
            assert len(scale["range"]) == len(scale["domain"]) == 4
        assert not [r for r in spec["datasets"][header["data"]["name"]]
                    if r["condition"] == "reference"]


def test_matrix_prints_the_reference_columns_values_only():
    """A reader should not have to eyeball the reference column off the ramp."""
    for direction in ("python-to-typescript", "typescript-to-python"):
        spec = json.loads(
            (CHARTS / f"statistical-analysis/port-to-port-matrix-{direction}.json").read_text()
        )
        cells = spec["layer"][0]
        text = [layer for layer in spec["layer"] if layer["mark"]["type"] == "text"]
        printed = []
        for layer in text:
            rows = spec["datasets"][layer["data"]["name"]]
            assert rows  # an empty half is left out, not carried as a dead layer
            printed += rows
            # Ink on the pale half of the ramp, surface on the dark half.
            pale = layer["mark"]["color"] == "#0b0b0b"
            assert all((row["similarity_pct"] < 55) == pale for row in rows)
            assert layer["encoding"]["text"]["format"] == ".0f"
            assert layer["mark"]["fontSize"] == 10
            for axis in ("x", "y"):
                assert layer["encoding"][axis]["scale"] == cells["encoding"][axis]["scale"]
        assert {row["port_a"] for row in printed} == {"reference"}
        assert sorted(row["port_b"] for row in printed) == sorted(
            row["port_b"]
            for row in spec["datasets"][cells["data"]["name"]]
            if row["port_a"] == "reference"
        )
