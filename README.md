# brailleplot

Plot lines in the terminal using Unicode braille characters. Each character
cell holds a 2×4 grid of dots, giving twice the horizontal and four times the
vertical resolution of plain character plots. Pure Python, no dependencies.

```
                       Accuracy vs epoch
0.998 ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⠤⠤⠤⠔⠒⠒⠒⠒⠒⠒⠒⠒⠉⠉⠉⢉⣉⣉⣉⣉⣉⣉⣉⣉⠉⠉⠉ train
      ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠤⠔⠒⠉⠉⣀⣀⣤⣤⣴⠶⠶⠶⠟⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀ val
      ┤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠊⠁⠀⣀⣠⣴⠶⠟⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      ┤⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⣀⣤⡶⠟⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      ┤⠀⠀⠀⠀⠀⢀⠤⠊⢀⣴⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
0.614 ┤⠀⠀⠀⠀⡰⠁⣠⡾⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      ┤⠀⠀⠀⡔⢡⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      ┤⠀⢀⠎⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      ┤⢀⢎⣾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 0.23 ┤⣺⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
      └──────────────────────────────────────────────────
       1                      15.5                     30
       ⠤⠤⠤ train   ⠶⠶⠶ val
```

## Install

```
pip install -e .
```

## Usage

```python
from brailleplot import plot, plot_two

print(plot_two(ys1, ys2, x=xs, labels=("a", "b"), title="Demo"))

# Series may have different x values: pass (xs, ys) pairs.
print(plot([(x1, y1), (x2, y2)], labels=["train", "val"], width=50, height=10))
```

Options for `plot` (all optional):

| option | meaning |
|---|---|
| `width`, `height` | plot area size in character cells |
| `labels`, `title` | series names and plot title |
| `xlim`, `ylim` | axis ranges (default: data range) |
| `color` | force ANSI colour on/off (default: on when writing to a TTY) |
| `colors` | per-series colour names (`cyan`, `magenta`, `green`, `red`, ...) |
| `thickness` | per-series line width in dots |
| `style` | per-series `"solid"` or `"dashed"` (one dot per character) |
| `end_labels` | print series labels at the right-hand end of each line |

With colour on, each line has its own colour and cells shared by two lines
are highlighted. Without colour, the second line is dashed (one dot per character) by
default so the lines remain distinguishable; `thickness=[1, 2]` with
`style=["solid", "solid"]` gives a thin/thick pair instead. NaN/inf values break a line.

## Example

```
python examples/demo.py
```
