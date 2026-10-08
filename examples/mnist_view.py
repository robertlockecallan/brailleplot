#!/usr/bin/env python3
"""Show MNIST images in the terminal as grayscale.

With colour, each character cell is a half block (▀) whose foreground and
background are the 256-colour grays of two vertically adjacent pixels, so a
28x28 digit takes 28 columns x 14 rows. Without colour (piped output or
--no-color) an ASCII brightness ramp is used instead, two characters per pixel.

    python examples/mnist_view.py                 # first 8 train images
    python examples/mnist_view.py 0 5 42          # those indices
    python examples/mnist_view.py --split test --random 12
    python examples/mnist_view.py --label 7 --n 6 # first six 7s
    python examples/mnist_view.py --npy samples.npy   # any (N, 28, 28) array
"""

import argparse
import gzip
import os
import random
import shutil
import struct
import sys

MNIST_DIR = os.path.expanduser("~/mnist")
RAMP = " .:-=+*#%@"
SIZE = 28


def _open(path):
    if os.path.exists(path):
        return open(path, "rb")
    return gzip.open(path + ".gz", "rb")


def load_idx(path):
    """Read an IDX file; return (dims, flat bytes)."""
    with _open(path) as f:
        data = f.read()
    ndim = data[3]
    dims = struct.unpack(">" + "I" * ndim, data[4:4 + 4 * ndim])
    return dims, data[4 + 4 * ndim:]


def load_mnist(split, directory=MNIST_DIR):
    prefix = "train" if split == "train" else "t10k"
    (n, h, w), pix = load_idx(os.path.join(directory, f"{prefix}-images-idx3-ubyte"))
    _, lab = load_idx(os.path.join(directory, f"{prefix}-labels-idx1-ubyte"))
    images = [pix[i * h * w:(i + 1) * h * w] for i in range(n)]
    return images, list(lab)


def load_npy(path):
    import numpy as np
    arr = np.load(path)
    arr = arr.reshape(-1, SIZE, SIZE)
    if arr.dtype != np.uint8:  # floats in [0, 1] or [-1, 1]
        lo = -1.0 if arr.min() < 0 else 0.0
        arr = ((arr - lo) / (1.0 - lo) * 255).clip(0, 255).astype(np.uint8)
    return [bytes(a.reshape(-1)) for a in arr], [None] * len(arr)


def gray_code(v):
    """Map 0..255 to the 256-colour palette's gray ramp (16, 232..255, 231)."""
    if v < 4:
        return 16
    if v > 250:
        return 231
    return 232 + (v - 4) * 24 // 247


def render_color(img, h=SIZE, w=SIZE):
    rows = []
    for y in range(0, h, 2):
        line = []
        for x in range(w):
            top = gray_code(img[y * w + x])
            bot = gray_code(img[(y + 1) * w + x]) if y + 1 < h else 16
            line.append(f"\x1b[38;5;{top};48;5;{bot}m▀")
        rows.append("".join(line) + "\x1b[0m")
    return rows


def render_ascii(img, h=SIZE, w=SIZE):
    rows = []
    for y in range(h):
        rows.append("".join(RAMP[img[y * w + x] * len(RAMP) // 256] * 2
                            for x in range(w)))
    return rows


def montage(tiles, widths, captions, per_row, gap=2):
    """Lay rendered tiles out in a grid of `per_row` columns."""
    out = []
    for start in range(0, len(tiles), per_row):
        group = tiles[start:start + per_row]
        caps = captions[start:start + per_row]
        width = widths[0]
        out.append((" " * gap).join(c.center(width) for c in caps).rstrip())
        for r in range(len(group[0])):
            out.append((" " * gap).join(t[r] for t in group))
        out.append("")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("indices", nargs="*", type=int, help="image indices to show")
    p.add_argument("--split", choices=["train", "test"], default="train")
    p.add_argument("--dir", default=MNIST_DIR, help="folder with the MNIST IDX files")
    p.add_argument("--npy", help="show images from a .npy array instead of MNIST")
    p.add_argument("--n", type=int, default=8, help="how many images when no indices are given")
    p.add_argument("--label", type=int, help="only show images of this digit")
    p.add_argument("--random", action="store_true", help="pick images at random")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--no-color", action="store_true", help="use the ASCII ramp")
    args = p.parse_args()

    images, labels = load_npy(args.npy) if args.npy else load_mnist(args.split, args.dir)

    if args.indices:
        idx = args.indices
    else:
        pool = [i for i, l in enumerate(labels) if args.label is None or l == args.label]
        if args.random:
            idx = random.Random(args.seed).sample(pool, min(args.n, len(pool)))
        else:
            idx = pool[:args.n]
    bad = [i for i in idx if not 0 <= i < len(images)]
    if bad:
        sys.exit(f"index out of range (0..{len(images) - 1}): {bad}")

    color = not args.no_color and (sys.stdout.isatty() or bool(os.environ.get("FORCE_COLOR")))
    render = render_color if color else render_ascii
    tile_w = SIZE if color else 2 * SIZE
    cols = shutil.get_terminal_size().columns
    per_row = max(1, (cols + 2) // (tile_w + 2))

    tiles = [render(images[i]) for i in idx]
    caps = [f"#{i}" + (f" = {labels[i]}" if labels[i] is not None else "") for i in idx]
    print(montage(tiles, [tile_w] * len(tiles), caps, per_row))


if __name__ == "__main__":
    main()
