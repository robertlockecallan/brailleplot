"""High-level line plotting on a BrailleCanvas with axes and legend."""

import math
import sys

from .canvas import BrailleCanvas

ANSI = {
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "white": "\x1b[37m",
}
RESET = "\x1b[0m"
DEFAULT_COLORS = ("cyan", "magenta")
OVERLAP_COLOR = "yellow"
STYLES = ("solid", "dashed")


def _fmt(v, scale=None):
    if v == 0 or (scale and abs(v) < 1e-4 * scale):
        return "0"
    if abs(v) >= 1e4 or abs(v) < 1e-2:
        return f"{v:.2e}"
    return f"{v:.3g}"


def _as_series(s):
    """Accept ``ys`` or ``(xs, ys)`` and return two float lists."""
    if isinstance(s, tuple) and len(s) == 2:
        xs, ys = list(s[0]), list(s[1])
    else:
        ys = list(s)
        xs = list(range(len(ys)))
    if len(xs) != len(ys):
        raise ValueError("x and y must have the same length")
    return [float(x) for x in xs], [float(y) for y in ys]


def plot(series, width=60, height=15, labels=None, colors=None, title=None,
         xlim=None, ylim=None, color=None, file=None, thickness=None,
         style=None, end_labels=True):
    """Plot one or more line series and return the rendered string.

    ``series`` is a list where each item is either a sequence of y values or a
    ``(xs, ys)`` tuple. NaN/inf points break the line. ``width``/``height`` are
    the plot area size in character cells. ``color`` forces ANSI colour on or
    off; by default it is used when ``file`` (stdout) is a TTY.
    ``thickness`` is a per-series list of line widths in dots. By default all
    lines are 1 dot wide, except that without colour every second line is
    drawn 2 dots wide so the lines stay distinguishable.
    ``style`` is a per-series list of ``"solid"`` or ``"dashed"`` (default all
    solid); a dashed line has one dot per character cell. ``end_labels``
    prints each series label just right of the plot, on the row where that
    series ends.
    """
    data = [_as_series(s) for s in series]
    if not data:
        raise ValueError("need at least one series")
    colors = list(colors or DEFAULT_COLORS)
    while len(colors) < len(data):
        colors.append(list(ANSI)[len(colors) % len(ANSI)])
    if labels is None:
        labels = [f"series {i + 1}" for i in range(len(data))]

    finite = [(x, y) for xs, ys in data for x, y in zip(xs, ys)
              if math.isfinite(x) and math.isfinite(y)]
    if not finite:
        raise ValueError("no finite data points")
    xmin, xmax = xlim or (min(p[0] for p in finite), max(p[0] for p in finite))
    ymin, ymax = ylim or (min(p[1] for p in finite), max(p[1] for p in finite))
    if xmax == xmin:
        xmin, xmax = xmin - 0.5, xmax + 0.5
    if ymax == ymin:
        ymin, ymax = ymin - 0.5, ymax + 0.5

    if file is None:
        file = sys.stdout
    if color is None:
        color = hasattr(file, "isatty") and file.isatty()
    if thickness is None:
        thickness = [1 if color else 1 + i % 2 for i in range(len(data))]
    if len(thickness) != len(data):
        raise ValueError("need one thickness per series")
    if style is None:
        style = ["solid"] * len(data)
    if len(style) != len(data) or any(st not in STYLES for st in style):
        raise ValueError(f"need one style per series, each one of {STYLES}")

    canvas = BrailleCanvas(width, height)
    pw, ph = canvas.pixel_width - 1, canvas.pixel_height - 1

    def to_px(x, y):
        px = round((x - xmin) / (xmax - xmin) * pw)
        py = round((ymax - y) / (ymax - ymin) * ph)
        return px, py

    end_ys = []  # pixel y of each series' last finite point
    for layer, (xs, ys) in enumerate(data):
        path = []  # pixels of the whole series, used for dashed lines
        prev = None
        for x, y in zip(xs, ys):
            if not (math.isfinite(x) and math.isfinite(y)):
                prev = None
                continue
            cur = to_px(x, y)
            if style[layer] == "dashed":
                path.extend(canvas.trace(*(prev or cur), *cur))
            elif prev is None:
                canvas.dot(*cur, layer, thickness[layer])
            else:
                canvas.line(*prev, *cur, layer, thickness[layer])
            prev = cur
        if path:
            canvas.dotted(path, layer, thickness[layer])
        end_ys.append(prev[1] if prev else None)

    layer_colors = {i: ANSI[c] for i, c in enumerate(colors)} if color else None
    overlap = ANSI[OVERLAP_COLOR] if color and len(data) > 1 else None

    # Y-axis labels at top, middle and bottom rows.
    ylabels = {0: _fmt(ymax), height // 2: _fmt((ymax + ymin) / 2, ymax - ymin),
               height - 1: _fmt(ymin)}
    lw = max(len(s) for s in ylabels.values())

    # Line-end labels, one per row, kept in the same top-to-bottom order as
    # the line ends; labels that share a row are pushed apart.
    row_labels = {}
    if end_labels:
        order = sorted((y, i) for i, y in enumerate(end_ys) if y is not None)
        rows = []
        for y, _ in order:  # push down past the previous label
            rows.append(max(min(max(y, 0) // 4, height - 1),
                            rows[-1] + 1 if rows else 0))
        for k in range(len(rows) - 1, -1, -1):  # pull back inside the plot
            rows[k] = min(rows[k], height - 1 if k == len(rows) - 1
                          else rows[k + 1] - 1)
        for (_, i), r in zip(order, rows):
            if r < 0:  # more labels than rows
                continue
            text = labels[i]
            if color:
                text = ANSI[colors[i]] + text + RESET
            row_labels[r] = text

    lines = []
    if title:
        lines.append(" " * (lw + 2) + title.center(width).rstrip())
    for r, row in enumerate(canvas.rows(layer_colors, overlap)):
        end = " " + row_labels[r] if r in row_labels else ""
        lines.append(f"{ylabels.get(r, ''):>{lw}} ┤{row}{end}")
    lines.append(" " * lw + " └" + "─" * width)
    left, right = _fmt(xmin), _fmt(xmax)
    mid = _fmt((xmin + xmax) / 2, xmax - xmin)
    axis = [" "] * width
    placements = [(0, left), (width - len(right), right)]
    mid_pos = (width - len(mid)) // 2
    if len(left) < mid_pos and mid_pos + len(mid) < width - len(right):
        placements.append((mid_pos, mid))
    for pos, text in placements:
        for i, ch in enumerate(text):
            if 0 <= pos + i < width:
                axis[pos + i] = ch
    lines.append(" " * (lw + 2) + "".join(axis))

    legend = []
    for lab, c, t, st in zip(labels, colors, thickness, style):
        ch = "⠤" if t == 1 else "⠶" if t == 2 else "⣿"
        if st == "dashed":
            mark = "⠂⠂⠂" if t == 1 else ch + "⠀" + ch
        else:
            mark = ch * 3
        legend.append((ANSI[c] + mark + RESET if color else mark) + " " + lab)
    if overlap:
        legend.append(overlap + "⣿⣿⣿" + RESET + " overlap")
    lines.append(" " * (lw + 2) + "   ".join(legend))
    return "\n".join(lines)


def plot_two(y1, y2, x=None, labels=("line 1", "line 2"), **kwargs):
    """Convenience wrapper: plot two lines sharing optional x values."""
    s1 = (x, y1) if x is not None else y1
    s2 = (x, y2) if x is not None else y2
    return plot([s1, s2], labels=list(labels), **kwargs)
