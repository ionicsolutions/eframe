"""Common plotting tools for :mod:`pyqtgraph`."""

import pyqtgraph as pg

# PENS

def pen(color, width=1):
    return pg.mkPen(color)


# BRUSHES

def brush(color):
    return pg.mkBrush(color)


# SYMBOLS
circle = "o"
square = "s"
triangle = "t"
diamond = "d"
plus = "+"
x = "x"

symbols = [circle, square, triangle, diamond, plus, x]
bold_symbols = [circle, square, triangle, diamond]
light_symbols = [plus, x]