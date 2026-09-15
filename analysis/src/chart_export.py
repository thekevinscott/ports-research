"""Export light charts and transparent dark SVG siblings."""

import json
import re
from copy import deepcopy

FORMATS = (".svg", ".png", ".json")


def write_chart(chart, base):
    """Light SVG, PNG and JSON, plus the transparent dark SVG sibling."""
    spec = _light_spec(chart)
    base.parent.mkdir(parents=True, exist_ok=True)
    import vl_convert as vlc

    written = []
    for suffix in FORMATS:
        path = base.with_name(base.name + suffix)
        if suffix == ".json":
            path.write_text(json.dumps(spec, indent=2) + "\n")
        elif suffix == ".svg":
            path.write_text(vlc.vegalite_to_svg(spec))
        else:
            path.write_bytes(vlc.vegalite_to_png(spec, scale=2))
        written.append(path)
    written.append(write_dark_svg(spec, base))
    return written


# X labels sit 7.5 degrees more horizontal than the shared -45; the axisX entry
# overrides the axis one for x axes only, so y tick labels keep the steeper angle.
X_LABEL_ANGLE = -37.5


def _light_spec(chart):
    """A spec dict from a chart object or a spec, with the blog's label rotation."""
    if hasattr(chart, "to_dict"):
        spec = chart.configure_axis(labelAngle=-45).to_dict()
    else:
        spec = deepcopy(chart)
        spec.setdefault("config", {}).setdefault("axis", {})["labelAngle"] = -45
    spec["config"]["axisX"] = {**spec["config"].get("axisX", {}), "labelAngle": X_LABEL_ANGLE}
    return spec


# --- Blog slot fitting -----------------------------------------------------

# Band scales snap plot geometry to a couple of pixels; padding is continuous, so
# plots shrink to just under the slot and padding closes the rest.
QUANTUM = 2.5
DEFAULT_LABEL_PADDING = 2
DEFAULT_VIEW_PADDING = 5


def rendered_geometry(spec):
    """The rendered (width, height, left margin, top margin) of a spec, in pixels."""
    import vl_convert as vlc

    svg = vlc.vegalite_to_svg(spec)
    (width, height), = re.findall(r'<svg[^>]*width="([\d.]+)" height="([\d.]+)"', svg)
    (left, top), = re.findall(
        r'stroke-miterlimit="10" transform="translate\(([\d.]+),([\d.]+)\)"', svg
    )
    return float(width), float(height), float(left), float(top)


def fit_pair(specs, width, measure=rendered_geometry):
    """Fit charts sharing a blog slot to identical geometry: equal left margins, the
    slot's exact width, equal heights. Every chart in the slot then renders at 1:1,
    so fonts hold one pixel size, and paired plots line up side by side."""
    fitted = [deepcopy(spec) for spec in specs]
    left = max(measure(spec)[2] for spec in fitted)
    for spec in fitted:
        _pad_axis(_units(spec)[0], "y", left - measure(spec)[2])
    for spec in fitted:
        _fit_width(spec, width, measure)
    top = max(measure(spec)[1] for spec in fitted)
    for spec in fitted:
        delta = top - measure(spec)[1]
        for unit in _units(spec):
            _pad_axis(unit, "x", delta)
    return fitted


def _units(spec):
    """Concat panels when there are any; the chart itself otherwise."""
    return spec.get("concat", [spec])


def align_panel_titles(spec, measure=None):
    """Anchor each concat panel's title to its plot area, not its y-axis."""
    measure = measure or _title_and_plot_xs
    spec = deepcopy(spec)
    units = spec.get("concat")
    if not units:
        return spec
    plots, titles = measure(spec)
    if spec.get("title") and len(titles) == len(units) + 1:
        titles = titles[:-1]  # the chart title renders after the panel titles
    for unit, plot_x, title_x in zip(units, plots, titles):
        title = unit.get("title")
        if isinstance(title, dict) and abs(plot_x - title_x) > 0.75:
            title["dx"] = title.get("dx", 0) + plot_x - title_x
    _, titles = measure(spec)
    if spec.get("title") and len(titles) == len(units) + 1:
        titles = titles[:-1]
    for plot_x, title_x in zip(plots, titles):
        if abs(plot_x - title_x) > 0.75:
            raise RuntimeError("panel titles did not align to their plots")
    return spec


def _title_and_plot_xs(spec):
    """(per-panel plot x's, title text x's) in document order, from the rendered SVG."""
    import xml.etree.ElementTree as ET
    import vl_convert as vlc

    root = ET.fromstring(vlc.vegalite_to_svg(spec))
    plots, titles = {}, []

    def walk(el, x, titled):
        match = re.match(r"translate\(([-\d.e]+)[, ]", el.get("transform", ""))
        if match:
            x += float(match.group(1))
        cls = el.get("class") or ""
        # A concat panel's first marks group sits at the panel's plot origin.
        panel = re.search(r"\bconcat_(\d+)_(?:layer_0_)?marks\b", cls)
        if panel and "role-mark" in cls:
            plots.setdefault(int(panel.group(1)), x)
        if "role-title" in cls:
            titled = True
        if titled and el.tag.endswith("}text"):
            titles.append(x)
            return  # exactly one text per title group
        for child in el:
            walk(child, x, titled)

    walk(root, 0.0, False)
    return [plots[i] for i in sorted(plots)], titles


def _fit_width(spec, width, measure, iterations=12):
    for _ in range(iterations):
        delta = width - measure(spec)[0]
        if 0 <= delta < QUANTUM:
            _pad_right(spec, delta)
            return
        units = _units(spec)
        share = (delta - QUANTUM / 2) / len(units) if delta > 0 else delta / len(units)
        for unit in units:
            if "width" not in unit:
                raise RuntimeError(f"no plot width to fit the {width}px slot")
            grown = unit["width"] + share
            if grown < 10:
                raise RuntimeError(f"plot cannot shrink to the {width}px slot")
            if unit.get("height") == unit["width"]:
                unit["height"] = grown  # the port-to-port matrix stays square
            unit["width"] = grown
    raise RuntimeError(f"plot did not converge to the {width}px slot")


def _pad_right(spec, delta):
    if delta < 0.05:
        return
    padding = spec.get("padding", DEFAULT_VIEW_PADDING)
    if not isinstance(padding, dict):
        padding = dict.fromkeys(("left", "top", "right", "bottom"), padding)
    spec["padding"] = padding | {"right": padding.get("right", DEFAULT_VIEW_PADDING) + delta}


def _pad_axis(unit, channel, delta):
    if abs(delta) < 0.05:
        return
    for layer in unit.get("layer", [unit]):
        enc = layer.get("encoding", {}).get(channel)
        if enc is None or "value" in enc or "datum" in enc:
            continue
        axis = enc.setdefault("axis", {})
        axis["labelPadding"] = axis.get("labelPadding", DEFAULT_LABEL_PADDING) + delta


TEXT = "#d8d3ca"
TITLE = "#f3f1ec"
GRID = "#2e2b26"
TICK = "#4c4840"
DARK_BLUE_RAMP = ["#161513", "#23466b", "#2f6fa3", "#3987e5", "#256abf"]


def dark_spec(spec, name):
    """Theme a copy of Vega-Lite, leaving data, layout and categorical scales intact."""
    from copy import deepcopy
    import re

    spec = deepcopy(spec)
    colors = {"#000": TEXT, "#000000": TEXT, "black": TEXT,
              "#0b0b0b": TITLE, "#ddd": GRID, "#dddddd": GRID,
              "#888": TICK, "#888888": TICK, "#898781": TEXT, "#fcfcfb": TICK}

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
