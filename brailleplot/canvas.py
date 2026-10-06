"""A pixel canvas where each terminal cell holds a 2x4 grid of braille dots."""

BRAILLE_BASE = 0x2800

# Bit for the dot at (column, row) within a cell; see Unicode braille patterns.
_DOT_BITS = (
    (0x01, 0x02, 0x04, 0x40),  # left column, rows 0..3
    (0x08, 0x10, 0x20, 0x80),  # right column, rows 0..3
)


class BrailleCanvas:
    """Canvas of ``width`` x ``height`` character cells.

    The pixel resolution is ``2*width`` x ``4*height``. Pixel (0, 0) is the
    top-left corner. Each pixel can be set on one or more numbered layers so
    that multiple series can be coloured independently.
    """

    def __init__(self, width, height):
        if width < 1 or height < 1:
            raise ValueError("canvas width and height must be >= 1")
        self.width = width
        self.height = height
        # cells[row][col] -> {layer: bitmask}
        self.cells = [[{} for _ in range(width)] for _ in range(height)]

    @property
    def pixel_width(self):
        return self.width * 2

    @property
    def pixel_height(self):
        return self.height * 4

    def set(self, x, y, layer=0):
        """Turn on pixel (x, y) for ``layer``; out-of-range pixels are ignored."""
        if not (0 <= x < self.pixel_width and 0 <= y < self.pixel_height):
            return
        cell = self.cells[y // 4][x // 2]
        cell[layer] = cell.get(layer, 0) | _DOT_BITS[x % 2][y % 4]

    def dot(self, x, y, layer=0, thickness=1):
        """Set a ``thickness`` x ``thickness`` block of pixels at (x, y)."""
        for dx in range(thickness):
            for dy in range(thickness):
                self.set(x + dx, y + dy, layer)

    @staticmethod
    def trace(x0, y0, x1, y1):
        """Yield the pixels of a straight line between two pixels (Bresenham)."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            yield x0, y0
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def line(self, x0, y0, x1, y1, layer=0, thickness=1):
        """Draw a straight line between two pixels.

        ``thickness`` > 1 draws with a square brush, widening the line.
        """
        for x, y in self.trace(x0, y0, x1, y1):
            self.dot(x, y, layer, thickness)

    def dotted(self, pixels, layer=0, thickness=1):
        """Draw a path as one dot per character cell.

        ``pixels`` is the path in drawing order; in each cell it passes
        through, only the middle one of its pixels there is drawn.
        """
        by_cell = {}
        for x, y in pixels:
            by_cell.setdefault((x // 2, y // 4), []).append((x, y))
        for pts in by_cell.values():
            self.dot(*pts[len(pts) // 2], layer, thickness)

    def cell_char(self, row, col):
        """Return (character, set_of_layers) for one cell."""
        cell = self.cells[row][col]
        mask = 0
        for bits in cell.values():
            mask |= bits
        return chr(BRAILLE_BASE + mask), frozenset(k for k, v in cell.items() if v)

    def rows(self, colors=None, overlap_color=None):
        """Yield rendered text rows.

        ``colors`` maps layer -> ANSI escape prefix. Cells shared by more than
        one layer use ``overlap_color`` if given.
        """
        reset = "\x1b[0m"
        for r in range(self.height):
            out = []
            for c in range(self.width):
                ch, layers = self.cell_char(r, c)
                prefix = None
                if colors and layers:
                    if len(layers) > 1 and overlap_color:
                        prefix = overlap_color
                    else:
                        prefix = colors.get(min(layers))
                out.append(prefix + ch + reset if prefix else ch)
            yield "".join(out)

    def render(self, colors=None, overlap_color=None):
        return "\n".join(self.rows(colors, overlap_color))
