"""Export light charts and transparent dark SVG siblings."""

FORMATS = {".svg": {}, ".png": {"scale_factor": 2}, ".json": {}}


def write_chart(chart, base):
    base.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix, options in FORMATS.items():
        path = base.with_name(base.name + suffix)
        chart.save(str(path), **options)
        written.append(path)
    written.append(write_dark_svg(chart.to_dict(), base))
    return written


TEXT = "#d8d3ca"
TITLE = "#f3f1ec"
GRID = "#2e2b26"
TICK = "#4c4840"
DARK_BLUE_RAMP = ["#161513", "#14233a", "#123152", "#10345f", "#0d366b"]


def dark_spec(spec, name):
    """Theme a copy of Vega-Lite, leaving data, layout and categorical scales intact."""
    from copy import deepcopy
    import re

    spec = deepcopy(spec)
    colors = {"#000": TEXT, "#000000": TEXT, "black": TEXT,
              "#0b0b0b": TITLE, "#ddd": GRID, "#dddddd": GRID,
              "#888": TICK, "#888888": TICK, "#fcfcfb": GRID}

    def recolor(value, stroke=False):
        mapping = colors | ({"#000": TITLE, "#000000": TITLE, "black": TITLE} if stroke else {})
        if isinstance(value, str):
            return mapping.get(value.lower(), value)
        if isinstance(value, dict) and "expr" in value:
            return {**value, "expr": re.sub(r"(['\"])(#[0-9a-fA-F]{3,6}|black)\1",
                lambda m: m[1] + mapping.get(m[2].lower(), m[2]) + m[1], value["expr"])}
        return value

    def visit(node):
        if isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, dict):
            mark = node.get("mark")
            if isinstance(mark, dict):
                for key in ("color", "stroke"):
                    if key in mark:
                        mark[key] = recolor(mark[key], mark.get("type") != "text")
            for key, value in node.items():
                if key in {"data", "datasets"}:
                    continue
                if key in {"color", "fill", "stroke"} or key.endswith("Color"):
                    node[key] = recolor(value, key == "stroke")
                visit(node[key])
            if name.startswith("port-to-port-matrix-"):
                color = node.get("encoding", {}).get("color", {})
                if color.get("type") == "quantitative":
                    scale = color.setdefault("scale", {})
                    scale.pop("scheme", None)
                    scale["range"] = DARK_BLUE_RAMP.copy()

    visit(spec)
    spec["background"] = "transparent"
    config = spec.setdefault("config", {})
    for section, defaults in {
        "axis": {"labelColor": TEXT, "titleColor": TITLE, "gridColor": GRID, "tickColor": TICK, "domainColor": TICK},
        "legend": {"labelColor": TEXT, "titleColor": TITLE},
        "header": {"labelColor": TEXT, "titleColor": TITLE},
        "title": {"color": TITLE, "subtitleColor": TEXT},
        "text": {"color": TEXT},
        "rule": {"color": TITLE},
        "view": {"stroke": GRID},
    }.items():
        config[section] = defaults | config.get(section, {})
    return spec


def write_dark_svg(spec, base):
    """Render directly from the themed spec, never rewriting an SVG."""
    import vl_convert as vlc

    path = base.with_name(base.name + "-dark.svg")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(vlc.vegalite_to_svg(dark_spec(spec, base.name)))
    return path


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Export dark SVG siblings from saved Vega-Lite JSON.")
    parser.add_argument("specs", type=Path, nargs="+")
    for source in parser.parse_args().specs:
        print(write_dark_svg(json.loads(source.read_text()), source.with_suffix("")))
