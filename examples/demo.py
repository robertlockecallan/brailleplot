#!/usr/bin/env python3
"""Plot two lines in the terminal with brailleplot."""

import math
import os
import sys

# Let the demo run from a checkout without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from brailleplot import plot, plot_two

xs = [i * 0.1 for i in range(126)]  # 0 .. 4*pi
sin = [math.sin(x) for x in xs]
damped = [math.exp(-x / 6) * math.cos(2 * x) for x in xs]

print(plot_two(sin, damped, x=xs, labels=("sin(x)", "e^(-x/6) cos(2x)"),
               title="Trig functions", width=70, height=16))
print()

# Two series with different x values, given as (xs, ys) pairs.
epochs = list(range(1, 31))
train = [1 - 0.9 * math.exp(-e / 5) for e in epochs]
val_epochs = epochs[::3]
val = [0.95 - 0.85 * math.exp(-e / 6) for e in val_epochs]
print(plot([(epochs, train), (val_epochs, val)], labels=["train", "val"],
           title="Accuracy vs epoch", width=50, height=10,
           colors=["green", "red"]))
print()

# The same two lines told apart by dashing instead of colour or thickness.
print(plot_two(sin, damped, x=xs, labels=("sin(x)", "damped"),
               title="Solid vs dashed", width=70, height=16,
               color=False, thickness=[1, 1], style=["solid", "dashed"]))
