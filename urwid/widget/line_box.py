from __future__ import annotations

import typing

from .columns import Columns
from .constants import Align, Sizing
from .divider import Divider
from .pile import Pile
from .solid_fill import SolidFill
from .text import Text
from .widget import Widget, WidgetWrap
from .widget_decoration import WidgetDecoration

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


class LineBox(WidgetDecoration, WidgetWrap):
    def __init__(
        self,
        original_widget: Widget,
        title: str = "",
        title_align: Literal["left", "center", "right"] | Align = Align.CENTER,
        title_attr=None,
        tlcorner: str = "┌",
        tline: str = "─",
        lline: str = "│",
        trcorner: str = "┐",
        blcorner: str = "└",
        rline: str = "│",
        bline: str = "─",
        brcorner: str = "┘",
    ) -> None:
        """
        Draw a line around original_widget.

        Use 'title' to set an initial title text with will be centered
        on top of the box.

        Use `title_attr` to apply a specific attribute to the title text.

        Use `title_align` to align the title to the 'left', 'right', or 'center'.
        The default is 'center'.

        You can also override the widgets used for the lines/corners:
            tline: top line
            bline: bottom line
            lline: left line
            rline: right line
            tlcorner: top left corner
            trcorner: top right corner
            blcorner: bottom left corner
            brcorner: bottom right corner

        If empty string is specified for one of the lines/corners, then no
        character will be output there.  This allows for seamless use of
        adjoining LineBoxes.
        """

        if tline:
            tline = Divider(tline)
        if bline:
            bline = Divider(bline)
        if lline:
            lline = SolidFill(lline)
        if rline:
            rline = SolidFill(rline)

        tlcorner, trcorner = Text(tlcorner), Text(trcorner)
        blcorner, brcorner = Text(blcorner), Text(brcorner)

        if not tline and title:
            raise ValueError("Cannot have a title when tline is empty string")

        if title_attr:
            self.title_widget = Text((title_attr, self.format_title(title)))
        else:
            self.title_widget = Text(self.format_title(title))

        if tline:
            if title_align not in ("left", "center", "right"):
                raise ValueError('title_align must be one of "left", "right", or "center"')
            if title_align == Align.LEFT:
                tline_widgets = [("flow", self.title_widget), tline]
            else:
                tline_widgets = [tline, (Sizing.FLOW, self.title_widget)]
                if title_align == "center":
                    tline_widgets.append(tline)
            self.tline_widget = Columns(tline_widgets)
            top = Columns([(Sizing.FIXED, 1, tlcorner), self.tline_widget, (Sizing.FIXED, 1, trcorner)])

        else:
            self.tline_widget = None
            top = None

        middle_widgets = []
        if lline:
            middle_widgets.append(("fixed", 1, lline))
        else:
            # Note: We need to define a fixed first widget (even if it's 0 width) so that the other
            # widgets have something to anchor onto
            middle_widgets.append(("fixed", 0, SolidFill("")))
        middle_widgets.append(original_widget)
        focus_col = len(middle_widgets) - 1
        if rline:
            middle_widgets.append((Sizing.FIXED, 1, rline))

        middle = Columns(middle_widgets, box_columns=[0, 2], focus_column=focus_col)

        if bline:
            bottom = Columns([(Sizing.FIXED, 1, blcorner), bline, (Sizing.FIXED, 1, brcorner)])
        else:
            bottom = None

        pile_widgets = []
        if top:
            pile_widgets.append(("flow", top))
        pile_widgets.append(middle)
        focus_pos = len(pile_widgets) - 1
        if bottom:
            pile_widgets.append(("flow", bottom))
        pile = Pile(pile_widgets, focus_item=focus_pos)

        WidgetDecoration.__init__(self, original_widget)
        WidgetWrap.__init__(self, pile)

    def format_title(self, text: str) -> str:
        if text:
            return f" {text} "

        return ""

    def set_title(self, text):
        if not self.title_widget:
            raise ValueError("Cannot set title when tline is unset")
        self.title_widget.set_text(self.format_title(text))
        self.tline_widget._invalidate()

    def pack(self, size=None, focus: bool = False) -> tuple[int, int]:
        """
        Return the number of screen columns and rows required for
        this Linebox widget to be displayed without wrapping or
        clipping, as a single element tuple.

        :param size: ``None`` for unlimited screen columns or (*maxcol*,) to
                     specify a maximum column size
        :type size: widget size
        """
        size = list(self._original_widget.pack(size, focus))
        size[0] += 2
        size[1] += 2
        return size
