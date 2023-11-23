# Urwid graphics widgets
#    Copyright (C) 2004-2011  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: https://urwid.org/


from __future__ import annotations

from urwid.display_common import AttrSpec
from urwid.widget import (
    BarGraph,
    BarGraphError,
    BarGraphMeta,
    BigText,
    GraphVScale,
    LineBox,
    ProgressBar,
    Sizing,
    Text,
    Widget,
    fixed_size,
    scale_bar_values,
)

__all__ = (
    "BigText",
    "LineBox",
    "BarGraph",
    "BarGraphError",
    "BarGraphMeta",
    "GraphVScale",
    "scale_bar_values",
    "ProgressBar",
)


class PythonLogo(Widget):
    _sizing = frozenset([Sizing.FIXED])

    def __init__(self) -> None:
        """
        Create canvas containing an ASCII version of the Python
        Logo and store it.
        """
        blu = AttrSpec("light blue", "default")
        yel = AttrSpec("yellow", "default")
        width = 17
        # fmt: off
        self._canvas = Text(
            [
                (blu, "     ______\n"),
                (blu, "   _|_o__  |"), (yel, "__\n"),
                (blu, "  |   _____|"), (yel, "  |\n"),
                (blu, "  |__|  "), (yel, "______|\n"),
                (yel, "     |____o_|"),
            ]
        ).render((width,))
        # fmt: on

    def pack(self, size=None, focus: bool = False):
        """
        Return the size from our pre-rendered canvas.
        """
        return self._canvas.cols(), self._canvas.rows()

    def render(self, size, focus: bool = False):
        """
        Return the pre-rendered canvas.
        """
        fixed_size(size)
        return self._canvas


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
