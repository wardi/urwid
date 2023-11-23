# Urwid Text Layout classes
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

import typing

from urwid.util import calc_text_pos, calc_trim_text, calc_width, is_wide_char, move_next_char, move_prev_char

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


class TextLayout:
    def supports_align_mode(self, align):
        """Return True if align is a supported align mode."""
        return True

    def supports_wrap_mode(self, wrap):
        """Return True if wrap is a supported wrap mode."""
        return True

    def layout(self, text, width, align, wrap):
        """
        Return a layout structure for text.

        :param text: string in current encoding or unicode string
        :param width: number of screen columns available
        :param align: align mode for text
        :param wrap: wrap mode for text

        Layout structure is a list of line layouts, one per output line.
        Line layouts are lists than may contain the following tuples:

        * (column width of text segment, start offset, end offset)
        * (number of space characters to insert, offset or None)
        * (column width of insert text, offset, "insert text")

        The offset in the last two tuples is used to determine the
        attribute used for the inserted spaces or text respectively.
        The attribute used will be the same as the attribute at that
        text offset.  If the offset is None when inserting spaces
        then no attribute will be used.
        """
        raise NotImplementedError(
            "This function must be overridden by a real text layout class. (see StandardTextLayout)"
        )


class CanNotDisplayText(Exception):
    pass


class StandardTextLayout(TextLayout):
    def __init__(self):  # , tab_stops=(), tab_stop_every=8):
        pass
        # """
        # tab_stops -- list of screen column indexes for tab stops
        # tab_stop_every -- repeated interval for following tab stops
        # """
        # assert tab_stop_every is None or type(tab_stop_every)==int
        # if not tab_stops and tab_stop_every:
        #    self.tab_stops = (tab_stop_every,)
        # self.tab_stops = tab_stops
        # self.tab_stop_every = tab_stop_every

    def supports_align_mode(self, align: str) -> bool:
        """Return True if align is 'left', 'center' or 'right'."""
        return align in ("left", "center", "right")

    def supports_wrap_mode(self, wrap: str) -> bool:
        """Return True if wrap is 'any', 'space', 'clip' or 'ellipsis'."""
        return wrap in ("any", "space", "clip", "ellipsis")

    def layout(
        self,
        text,
        width: int,
        align: Literal["left", "center", "right"],
        wrap: Literal["any", "space", "clip", "ellipsis"],
    ):
        """Return a layout structure for text."""
        try:
            segs = self.calculate_text_segments(text, width, wrap)
            return self.align_layout(text, width, segs, wrap, align)
        except CanNotDisplayText:
            return [[]]

    def pack(self, maxcol: int, layout) -> int:
        """
        Return a minimal maxcol value that would result in the same
        number of lines for layout.  layout must be a layout structure
        returned by self.layout().
        """
        maxwidth = 0
        if not layout:
            raise ValueError(f"huh? empty layout?: {layout!r}")
        for lines in layout:
            lw = line_width(lines)
            if lw >= maxcol:
                return maxcol
            maxwidth = max(maxwidth, lw)
        return maxwidth

    def align_layout(
        self,
        text,
        width: int,
        segs,
        wrap: Literal["any", "space", "clip", "ellipsis"],
        align: Literal["left", "center", "right"],
    ):
        """Convert the layout segs to an aligned layout."""
        out = []
        for lines in segs:
            sc = line_width(lines)
            if sc == width or align == "left":
                out.append(lines)
                continue

            if align == "right":
                out.append([(width - sc, None), *lines])
                continue
            if align != "center":
                raise ValueError(align)
            pad_trim_left = (width - sc + 1) // 2
            out.append([(pad_trim_left, None), *lines] if pad_trim_left else lines)
        return out

    def calculate_text_segments(
        self,
        text,
        width: int,
        wrap: Literal["any", "space", "clip", "ellipsis"],
    ):
        """
        Calculate the segments of text to display given width screen
        columns to display them.

        text - unicode text or byte string to display
        width - number of available screen columns
        wrap - wrapping mode used

        Returns a layout structure without alignment applied.
        """
        nl, nl_o, sp_o = "\n", "\n", " "
        if isinstance(text, bytes):
            nl = nl.encode("iso8859-1")  # can only find bytes in python3 bytestrings
            nl_o = ord(nl_o)  # + an item of a bytestring is the ordinal value
            sp_o = ord(sp_o)
        b = []
        p = 0
        if wrap in ("clip", "ellipsis"):
            # no wrapping to calculate, so it's easy.
            while p <= len(text):
                n_cr = text.find(nl, p)
                if n_cr == -1:
                    n_cr = len(text)
                sc = calc_width(text, p, n_cr)

                # trim line to max width if needed, add ellipsis if trimmed
                if wrap == "ellipsis" and sc > width:
                    trimmed = True
                    spos, n_end, pad_left, pad_right = calc_trim_text(text, p, n_cr, 0, width - 1)
                    # pad_left should be 0, because the start_col parameter was 0 (no trimming on the left)
                    # similarly spos should not be changed from p
                    if pad_left != 0:
                        raise ValueError(pad_left)
                    if spos != p:
                        raise ValueError(spos)
                    sc = width - 1 - pad_right
                else:
                    trimmed = False
                    n_end = n_cr
                    pad_right = 0

                line = []
                if p != n_end:
                    line += [(sc, p, n_end)]
                if trimmed:
                    line += [(1, n_end, "…".encode())]
                line += [(pad_right, n_end)]
                b.append(line)
                p = n_cr + 1
            return b

        while p <= len(text):
            # look for next eligible line break
            n_cr = text.find(nl, p)
            if n_cr == -1:
                n_cr = len(text)
            sc = calc_width(text, p, n_cr)
            if sc == 0:
                # removed character hint
                b.append([(0, n_cr)])
                p = n_cr + 1
                continue
            if sc <= width:
                # this segment fits
                b.append([(sc, p, n_cr), (0, n_cr)])
                # removed character hint

                p = n_cr + 1
                continue
            pos, sc = calc_text_pos(text, p, n_cr, width)
            if pos == p:  # pathological width=1 double-byte case
                raise CanNotDisplayText("Wide character will not fit in 1-column width")
            if wrap == "any":
                b.append([(sc, p, pos)])
                p = pos
                continue
            if wrap != "space":
                raise ValueError(wrap)
            if text[pos] == sp_o:
                # perfect space wrap
                b.append([(sc, p, pos), (0, pos)])
                # removed character hint

                p = pos + 1
                continue
            if is_wide_char(text, pos):
                # perfect next wide
                b.append([(sc, p, pos)])
                p = pos
                continue
            prev = pos
            while prev > p:
                prev = move_prev_char(text, p, prev)
                if text[prev] == sp_o:
                    sc = calc_width(text, p, prev)
                    line = [(0, prev)]
                    if p != prev:
                        line = [(sc, p, prev), *line]
                    b.append(line)
                    p = prev + 1
                    break
                if is_wide_char(text, prev):
                    # wrap after wide char
                    next_char = move_next_char(text, prev, pos)
                    sc = calc_width(text, p, next_char)
                    b.append([(sc, p, next_char)])
                    p = next_char
                    break
            else:
                # unwrap previous line space if possible to
                # fit more text (we're breaking a word anyway)
                if b and (len(b[-1]) == 2 or (len(b[-1]) == 1 and len(b[-1][0]) == 2)):
                    # look for removed space above
                    if len(b[-1]) == 1:
                        [(h_sc, h_off)] = b[-1]
                        p_sc = 0
                        p_off = p_end = h_off
                    else:
                        [(p_sc, p_off, p_end), (h_sc, h_off)] = b[-1]
                    if p_sc < width and h_sc == 0 and text[h_off] == sp_o:
                        # combine with previous line
                        del b[-1]
                        p = p_off
                        pos, sc = calc_text_pos(text, p, n_cr, width)
                        b.append([(sc, p, pos)])
                        # check for trailing " " or "\n"
                        p = pos
                        if p < len(text) and (text[p] in (sp_o, nl_o)):
                            # removed character hint
                            b[-1].append((0, p))
                            p += 1
                        continue

                # force any char wrap
                b.append([(sc, p, pos)])
                p = pos
        return b


######################################
# default layout object to use
default_layout = StandardTextLayout()
######################################


class LayoutSegment:
    def __init__(self, seg: tuple[int, int, bytes | int] | tuple[int, int | None]) -> None:
        """Create object from line layout segment structure"""

        if not isinstance(seg, tuple):
            raise TypeError(seg)
        if len(seg) not in (2, 3):
            raise ValueError(seg)

        self.sc, self.offs = seg[:2]

        if not isinstance(self.sc, int):
            raise TypeError(self.sc)

        if len(seg) == 3:
            if not isinstance(self.offs, int):
                raise TypeError(self.offs)
            if self.sc <= 0:
                raise ValueError(seg)
            t = seg[2]
            if isinstance(t, bytes):
                self.text: bytes | None = t
                self.end = None
            else:
                if not isinstance(t, int):
                    raise TypeError(t)
                self.text = None
                self.end = t
        else:
            if len(seg) != 2:
                raise ValueError(seg)
            if self.offs is not None:
                if self.sc < 0:
                    raise ValueError(seg)
                if not isinstance(self.offs, int):
                    raise TypeError(self.offs)
            self.text = self.end = None

    def subseg(self, text, start: int, end: int):
        """
        Return a "sub-segment" list containing segment structures
        that make up a portion of this segment.

        A list is returned to handle cases where wide characters
        need to be replaced with a space character at either edge
        so two or three segments will be returned.
        """
        if start < 0:
            start = 0
        if end > self.sc:
            end = self.sc
        if start >= end:
            return []  # completely gone
        if self.text:
            # use text stored in segment (self.text)
            spos, epos, pad_left, pad_right = calc_trim_text(self.text, 0, len(self.text), start, end)
            return [(end - start, self.offs, b"".ljust(pad_left) + self.text[spos:epos] + b"".ljust(pad_right))]
        if self.end:
            # use text passed as parameter (text)
            spos, epos, pad_left, pad_right = calc_trim_text(text, self.offs, self.end, start, end)
            lines = []
            if pad_left:
                lines.append((1, spos - 1))
            lines.append((end - start - pad_left - pad_right, spos, epos))
            if pad_right:
                lines.append((1, epos))
            return lines

        return [(end - start, self.offs)]


def line_width(segs):
    """
    Return the screen column width of one line of a text layout structure.

    This function ignores any existing shift applied to the line,
    represented by an (amount, None) tuple at the start of the line.
    """
    sc = 0
    seglist = segs
    if segs and len(segs[0]) == 2 and segs[0][1] is None:
        seglist = segs[1:]
    for s in seglist:
        sc += s[0]
    return sc


def shift_line(segs, amount: int):
    """
    Return a shifted line from a layout structure to the left or right.
    segs -- line of a layout structure
    amount -- screen columns to shift right (+ve) or left (-ve)
    """
    if not isinstance(amount, int):
        raise TypeError(amount)

    if segs and len(segs[0]) == 2 and segs[0][1] is None:
        # existing shift
        amount += segs[0][0]
        if amount:
            return [(amount, None)] + segs[1:]
        return segs[1:]

    if amount:
        return [(amount, None), *segs]
    return segs


def trim_line(segs, text, start: int, end: int):
    """
    Return a trimmed line of a text layout structure.
    text -- text to which this layout structure applies
    start -- starting screen column
    end -- ending screen column
    """
    result = []
    x = 0
    for seg in segs:
        sc = seg[0]
        if start or sc < 0:
            if start >= sc:
                start -= sc
                x += sc
                continue
            s = LayoutSegment(seg)
            if x + sc >= end:
                # can all be done at once
                return s.subseg(text, start, end - x)
            result += s.subseg(text, start, sc)
            start = 0
            x += sc
            continue
        if x >= end:
            break
        if x + sc > end:
            s = LayoutSegment(seg)
            result += s.subseg(text, 0, end - x)
            break
        result.append(seg)
    return result


def calc_line_pos(text, line_layout, pref_col: Literal["left", "right"] | int):
    """
    Calculate the closest linear position to pref_col given a
    line layout structure.  Returns None if no position found.
    """
    closest_sc = None
    closest_pos = None
    current_sc = 0

    if pref_col == "left":
        for seg in line_layout:
            s = LayoutSegment(seg)
            if s.offs is not None:
                return s.offs
        return None
    if pref_col == "right":
        for seg in line_layout:
            s = LayoutSegment(seg)
            if s.offs is not None:
                closest_pos = s
        s = closest_pos
        if s is None:
            return None
        if s.end is None:
            return s.offs
        return calc_text_pos(text, s.offs, s.end, s.sc - 1)[0]

    for seg in line_layout:
        s = LayoutSegment(seg)
        if s.offs is not None:
            if s.end is not None:
                if current_sc <= pref_col < current_sc + s.sc:
                    # exact match within this segment
                    return calc_text_pos(text, s.offs, s.end, pref_col - current_sc)[0]
                if current_sc <= pref_col:
                    closest_sc = current_sc + s.sc - 1
                    closest_pos = s

            if closest_sc is None or (abs(pref_col - current_sc) < abs(pref_col - closest_sc)):
                # this screen column is closer
                closest_sc = current_sc
                closest_pos = s.offs
            if current_sc > closest_sc:
                # we're moving past
                break
        current_sc += s.sc

    if closest_pos is None or isinstance(closest_pos, int):
        return closest_pos

    # return the last positions in the segment "closest_pos"
    s = closest_pos
    return calc_text_pos(text, s.offs, s.end, s.sc - 1)[0]


def calc_pos(text, layout, pref_col: Literal["left", "right"] | int, row: int) -> int:
    """
    Calculate the closest linear position to pref_col and row given a
    layout structure.
    """

    if row < 0 or row >= len(layout):
        raise ValueError("calculate_pos: out of layout row range")

    pos = calc_line_pos(text, layout[row], pref_col)
    if pos is not None:
        return pos

    rows_above = list(range(row - 1, -1, -1))
    rows_below = list(range(row + 1, len(layout)))
    while rows_above and rows_below:
        if rows_above:
            r = rows_above.pop(0)
            pos = calc_line_pos(text, layout[r], pref_col)
            if pos is not None:
                return pos
        if rows_below:
            r = rows_below.pop(0)
            pos = calc_line_pos(text, layout[r], pref_col)
            if pos is not None:
                return pos
    return 0


def calc_coords(text, layout, pos, clamp: int = 1):
    """
    Calculate the coordinates closest to position pos in text with layout.

    text -- raw string or unicode string
    layout -- layout structure applied to text
    pos -- integer position into text
    clamp -- ignored right now
    """
    closest = None
    y = 0
    for line_layout in layout:
        x = 0
        for seg in line_layout:
            s = LayoutSegment(seg)
            if s.offs is None:
                x += s.sc
                continue
            if s.offs == pos:
                return x, y
            if s.end is not None and s.offs <= pos < s.end:
                x += calc_width(text, s.offs, pos)
                return x, y
            distance = abs(s.offs - pos)
            if s.end is not None and s.end < pos:
                distance = pos - (s.end - 1)
            if closest is None or distance < closest[0]:
                closest = distance, (x, y)
            x += s.sc
        y += 1

    if closest:
        return closest[1]
    return 0, 0
