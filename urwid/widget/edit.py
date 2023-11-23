from __future__ import annotations

import string
import typing

from urwid import text_layout
from urwid.canvas import CompositeCanvas
from urwid.command_map import Command
from urwid.split_repr import remove_defaults
from urwid.util import decompose_tagmarkup, is_wide_char, move_next_char, move_prev_char

if typing.TYPE_CHECKING:
    from typing_extensions import Literal

    from urwid.canvas import TextCanvas

from .constants import Align, WrapMode
from .text import Text, TextError


class EditError(TextError):
    pass


class Edit(Text):
    """
    Text editing widget implements cursor movement, text insertion and
    deletion.  A caption may prefix the editing area.  Uses text class
    for text layout.

    Users of this class may listen for ``"change"`` or ``"postchange"``
    events.  See :func:``connect_signal``.

    * ``"change"`` is sent just before the value of edit_text changes.
      It receives the new text as an argument.  Note that ``"change"`` cannot
      change the text in question as edit_text changes the text afterwards.
    * ``"postchange"`` is sent after the value of edit_text changes.
      It receives the old value of the text as an argument and thus is
      appropriate for changing the text.  It is possible for a ``"postchange"``
      event handler to get into a loop of changing the text and then being
      called when the event is re-emitted.  It is up to the event
      handler to guard against this case (for instance, by not changing the
      text if it is signaled for text that it has already changed once).
    """

    _selectable = True
    ignore_focus = False
    # (this variable is picked up by the MetaSignals metaclass)
    signals: typing.ClassVar[list[str]] = ["change", "postchange"]

    def valid_char(self, ch: str) -> bool:
        """
        Filter for text that may be entered into this widget by the user

        :param ch: character to be inserted
        :type ch: str

        This implementation returns True for all printable characters.
        """
        return is_wide_char(ch, 0) or (len(ch) == 1 and ord(ch) >= 32)

    def __init__(
        self,
        caption="",
        edit_text: str | bytes = "",
        multiline: bool = False,
        align: Literal["left", "center", "right"] | Align = Align.LEFT,
        wrap: Literal["space", "any", "clip", "ellipsis"] | WrapMode = WrapMode.SPACE,
        allow_tab: bool = False,
        edit_pos: int | None = None,
        layout=None,
        mask: str | bytes | None = None,
    ) -> None:
        """
        :param caption: markup for caption preceding edit_text, see
                        :class:`Text` for description of text markup.
        :type caption: text markup
        :param edit_text: initial text for editing, type (bytes or unicode)
                          must match the text in the caption
        :type edit_text: bytes or unicode
        :param multiline: True: 'enter' inserts newline  False: return it
        :type multiline: bool
        :param align: typically 'left', 'center' or 'right'
        :type align: text alignment mode
        :param wrap: typically 'space', 'any' or 'clip'
        :type wrap: text wrapping mode
        :param allow_tab: True: 'tab' inserts 1-8 spaces  False: return it
        :type allow_tab: bool
        :param edit_pos: initial position for cursor, None:end of edit_text
        :type edit_pos: int
        :param layout: defaults to a shared :class:`StandardTextLayout` instance
        :type layout: text layout instance
        :param mask: hide text entered with this character, None:disable mask
        :type mask: bytes or unicode

        >>> Edit()
        <Edit selectable flow widget '' edit_pos=0>
        >>> Edit(u"Y/n? ", u"yes")
        <Edit selectable flow widget 'yes' caption='Y/n? ' edit_pos=3>
        >>> Edit(u"Name ", u"Smith", edit_pos=1)
        <Edit selectable flow widget 'Smith' caption='Name ' edit_pos=1>
        >>> Edit(u"", u"3.14", align='right')
        <Edit selectable flow widget '3.14' align='right' edit_pos=4>
        """

        super().__init__("", align, wrap, layout)
        self.multiline = multiline
        self.allow_tab = allow_tab
        self._edit_pos = 0
        self._caption, self._attrib = decompose_tagmarkup(caption)
        self._edit_text = ""
        self.highlight = None
        self.set_edit_text(edit_text)
        if edit_pos is None:
            edit_pos = len(edit_text)
        self.set_edit_pos(edit_pos)
        self.set_mask(mask)
        self._shift_view_to_cursor = False

    def _repr_words(self) -> list[str]:
        return (
            super()._repr_words()[:-1]
            + [repr(self._edit_text)]
            + [f"caption={self._caption!r}"] * bool(self._caption)
            + ["multiline"] * (self.multiline is True)
        )

    def _repr_attrs(self):
        attrs = dict(super()._repr_attrs(), edit_pos=self._edit_pos)
        return remove_defaults(attrs, Edit.__init__)

    def get_text(self):
        """
        Returns ``(text, display attributes)``. See :meth:`Text.get_text`
        for details.

        Text returned includes the caption and edit_text, possibly masked.

        >>> Edit(u"What? ","oh, nothing.").get_text() # ... = u in Python 2
        (...'What? oh, nothing.', [])
        >>> Edit(('bright',u"user@host:~$ "),"ls").get_text()
        (...'user@host:~$ ls', [('bright', 13)])
        >>> Edit(u"password:", u"seekrit", mask=u"*").get_text()
        (...'password:*******', [])
        """

        if self._mask is None:
            return self._caption + self._edit_text, self._attrib

        return self._caption + (self._mask * len(self._edit_text)), self._attrib

    def set_text(self, markup) -> None:
        """
        Not supported by Edit widget.

        >>> Edit().set_text("test")
        Traceback (most recent call last):
        EditError: set_text() not supported.  Use set_caption() or set_edit_text() instead.
        """
        # FIXME: this smells. reimplement Edit as a WidgetWrap subclass to
        # clean this up

        # hack to let Text.__init__() work
        if not hasattr(self, "_text") and markup == "":
            self._text = None
            return

        raise EditError("set_text() not supported.  Use set_caption() or set_edit_text() instead.")

    def get_pref_col(self, size: tuple[int]) -> int:
        """
        Return the preferred column for the cursor, or the
        current cursor x value.  May also return ``'left'`` or ``'right'``
        to indicate the leftmost or rightmost column available.

        This method is used internally and by other widgets when
        moving the cursor up or down between widgets so that the
        column selected is one that the user would expect.

        >>> size = (10,)
        >>> Edit().get_pref_col(size)
        0
        >>> e = Edit(u"", u"word")
        >>> e.get_pref_col(size)
        4
        >>> e.keypress(size, 'left')
        >>> e.get_pref_col(size)
        3
        >>> e.keypress(size, 'end')
        >>> e.get_pref_col(size)
        <Align.RIGHT: 'right'>
        >>> e = Edit(u"", u"2\\nwords")
        >>> e.keypress(size, 'left')
        >>> e.keypress(size, 'up')
        >>> e.get_pref_col(size)
        4
        >>> e.keypress(size, 'left')
        >>> e.get_pref_col(size)
        0
        """
        (maxcol,) = size
        pref_col, then_maxcol = self.pref_col_maxcol
        if then_maxcol != maxcol:
            return self.get_cursor_coords((maxcol,))[0]

        return pref_col

    def set_caption(self, caption) -> None:
        """
        Set the caption markup for this widget.

        :param caption: markup for caption preceding edit_text, see
                        :meth:`Text.__init__` for description of text markup.

        >>> e = Edit("")
        >>> e.set_caption("cap1")
        >>> print(e.caption)
        cap1
        >>> e.set_caption(('bold', "cap2"))
        >>> print(e.caption)
        cap2
        >>> e.attrib
        [('bold', 4)]
        >>> e.caption = "cap3"  # not supported because caption stores text but set_caption() takes markup
        Traceback (most recent call last):
        AttributeError: can't set attribute
        """
        self._caption, self._attrib = decompose_tagmarkup(caption)
        self._invalidate()

    @property
    def caption(self) -> str:
        """
        Read-only property returning the caption for this widget.
        """
        return self._caption

    def set_edit_pos(self, pos: int) -> None:
        """
        Set the cursor position with a self.edit_text offset.
        Clips pos to [0, len(edit_text)].

        :param pos: cursor position
        :type pos: int

        >>> e = Edit(u"", u"word")
        >>> e.edit_pos
        4
        >>> e.set_edit_pos(2)
        >>> e.edit_pos
        2
        >>> e.edit_pos = -1  # Urwid 0.9.9 or later
        >>> e.edit_pos
        0
        >>> e.edit_pos = 20
        >>> e.edit_pos
        4
        """
        if pos < 0:
            pos = 0
        if pos > len(self._edit_text):
            pos = len(self._edit_text)
        self.highlight = None
        self.pref_col_maxcol = None, None
        self._edit_pos = pos
        self._invalidate()

    edit_pos = property(
        lambda self: self._edit_pos,
        set_edit_pos,
        doc="""
        Property controlling the edit position for this widget.
        """,
    )

    def set_mask(self, mask: str | bytes | None) -> None:
        """
        Set the character for masking text away.

        :param mask: hide text entered with this character, None:disable mask
        :type mask: bytes or unicode
        """

        self._mask = mask
        self._invalidate()

    def set_edit_text(self, text: str | bytes) -> None:
        """
        Set the edit text for this widget.

        :param text: text for editing, type (bytes or unicode)
                     must match the text in the caption
        :type text: bytes or unicode

        >>> e = Edit()
        >>> e.set_edit_text(u"yes")
        >>> print(e.edit_text)
        yes
        >>> e
        <Edit selectable flow widget 'yes' edit_pos=0>
        >>> e.edit_text = u"no"  # Urwid 0.9.9 or later
        >>> print(e.edit_text)
        no
        """
        text = self._normalize_to_caption(text)
        self.highlight = None
        self._emit("change", text)
        old_text = self._edit_text
        self._edit_text = text
        if self.edit_pos > len(text):
            self.edit_pos = len(text)
        self._emit("postchange", old_text)
        self._invalidate()

    def get_edit_text(self) -> str:
        """
        Return the edit text for this widget.

        >>> e = Edit(u"What? ", u"oh, nothing.")
        >>> print(e.get_edit_text())
        oh, nothing.
        >>> print(e.edit_text)
        oh, nothing.
        """
        return self._edit_text

    edit_text = property(
        get_edit_text,
        set_edit_text,
        doc="""
        Property controlling the edit text for this widget.
        """,
    )

    def insert_text(self, text: str | bytes) -> None:
        """
        Insert text at the cursor position and update cursor.
        This method is used by the keypress() method when inserting
        one or more characters into edit_text.

        :param text: text for inserting, type (bytes or unicode)
                     must match the text in the caption
        :type text: bytes or unicode

        >>> e = Edit(u"", u"42")
        >>> e.insert_text(u".5")
        >>> e
        <Edit selectable flow widget '42.5' edit_pos=4>
        >>> e.set_edit_pos(2)
        >>> e.insert_text(u"a")
        >>> print(e.edit_text)
        42a.5
        """
        text = self._normalize_to_caption(text)
        result_text, result_pos = self.insert_text_result(text)
        self.set_edit_text(result_text)
        self.set_edit_pos(result_pos)
        self.highlight = None

    def _normalize_to_caption(self, text: str | bytes) -> str | bytes:
        """
        Return text converted to the same type as self.caption
        (bytes or unicode)
        """
        tu = isinstance(text, str)
        cu = isinstance(self._caption, str)
        if tu == cu:
            return text
        if tu:
            return text.encode("ascii")  # follow python2's implicit conversion
        return text.decode("ascii")

    def insert_text_result(self, text: str | bytes) -> tuple[str | bytes, int]:
        """
        Return result of insert_text(text) without actually performing the
        insertion.  Handy for pre-validation.

        :param text: text for inserting, type (bytes or unicode)
                     must match the text in the caption
        :type text: bytes or unicode
        """

        # if there's highlighted text, it'll get replaced by the new text
        text = self._normalize_to_caption(text)
        if self.highlight:
            start, stop = self.highlight
            btext, etext = self.edit_text[:start], self.edit_text[stop:]
            result_text = btext + etext
            result_pos = start
        else:
            result_text = self.edit_text
            result_pos = self.edit_pos

        try:
            result_text = result_text[:result_pos] + text + result_text[result_pos:]
        except (IndexError, TypeError) as exc:
            raise ValueError(repr((self.edit_text, result_text, text))).with_traceback(exc.__traceback__) from exc

        result_pos += len(text)
        return (result_text, result_pos)

    def keypress(self, size: tuple[int], key: str) -> str | None:
        """
        Handle editing keystrokes, return others.

        >>> e, size = Edit(), (20,)
        >>> e.keypress(size, 'x')
        >>> e.keypress(size, 'left')
        >>> e.keypress(size, '1')
        >>> print(e.edit_text)
        1x
        >>> e.keypress(size, 'backspace')
        >>> e.keypress(size, 'end')
        >>> e.keypress(size, '2')
        >>> print(e.edit_text)
        x2
        >>> e.keypress(size, 'shift f1')
        'shift f1'
        """
        (maxcol,) = size

        pos = self.edit_pos
        if self.valid_char(key):
            if isinstance(key, str) and not isinstance(self._caption, str):
                # screen is sending us unicode input, must be using utf-8
                # encoding because that's all we support, so convert it
                # to bytes to match our caption's type
                key = key.encode("utf-8")
            self.insert_text(key)
            return None

        if key == "tab" and self.allow_tab:
            key = " " * (8 - (self.edit_pos % 8))
            self.insert_text(key)
            return None

        if key == "enter" and self.multiline:
            key = "\n"
            self.insert_text(key)
            return None

        if self._command_map[key] == Command.LEFT:
            if pos == 0:
                return key
            pos = move_prev_char(self.edit_text, 0, pos)
            self.set_edit_pos(pos)
            return None

        if self._command_map[key] == Command.RIGHT:
            if pos >= len(self.edit_text):
                return key
            pos = move_next_char(self.edit_text, pos, len(self.edit_text))
            self.set_edit_pos(pos)
            return None

        if self._command_map[key] in (Command.UP, Command.DOWN):
            self.highlight = None

            x, y = self.get_cursor_coords((maxcol,))
            pref_col = self.get_pref_col((maxcol,))
            if pref_col is None:
                raise ValueError(pref_col)

            # if pref_col is None:
            #    pref_col = x

            if self._command_map[key] == Command.UP:
                y -= 1
            else:
                y += 1

            if not self.move_cursor_to_coords((maxcol,), pref_col, y):
                return key
            return None

        if key == "backspace":
            self.pref_col_maxcol = None, None
            if not self._delete_highlighted():
                if pos == 0:
                    return key
                pos = move_prev_char(self.edit_text, 0, pos)
                self.set_edit_text(self.edit_text[:pos] + self.edit_text[self.edit_pos :])
                self.set_edit_pos(pos)
                return None
            return None

        if key == "delete":
            self.pref_col_maxcol = None, None
            if not self._delete_highlighted():
                if pos >= len(self.edit_text):
                    return key
                pos = move_next_char(self.edit_text, pos, len(self.edit_text))
                self.set_edit_text(self.edit_text[: self.edit_pos] + self.edit_text[pos:])
                return None
            return None

        if self._command_map[key] in (Command.MAX_LEFT, Command.MAX_RIGHT):
            self.highlight = None
            self.pref_col_maxcol = None, None

            x, y = self.get_cursor_coords((maxcol,))

            if self._command_map[key] == Command.MAX_LEFT:
                self.move_cursor_to_coords((maxcol,), Align.LEFT, y)
            else:
                self.move_cursor_to_coords((maxcol,), Align.RIGHT, y)
            return None

        # key wasn't handled
        return key

    def move_cursor_to_coords(
        self,
        size: tuple[int],
        x: int | Literal[Align.LEFT, Align.RIGHT],
        y: int,
    ) -> bool:
        """
        Set the cursor position with (x,y) coordinates.
        Returns True if move succeeded, False otherwise.

        >>> size = (10,)
        >>> e = Edit("","edit\\ntext")
        >>> e.move_cursor_to_coords(size, 5, 0)
        True
        >>> e.edit_pos
        4
        >>> e.move_cursor_to_coords(size, 5, 3)
        False
        >>> e.move_cursor_to_coords(size, 0, 1)
        True
        >>> e.edit_pos
        5
        """
        (maxcol,) = size
        trans = self.get_line_translation(maxcol)
        top_x, top_y = self.position_coords(maxcol, 0)
        if y < top_y or y >= len(trans):
            return False

        pos = text_layout.calc_pos(self.get_text()[0], trans, x, y)
        e_pos = pos - len(self.caption)
        if e_pos < 0:
            e_pos = 0
        if e_pos > len(self.edit_text):
            e_pos = len(self.edit_text)
        self.edit_pos = e_pos
        self.pref_col_maxcol = x, maxcol
        self._invalidate()
        return True

    def mouse_event(self, size: tuple[int], event, button: int, x: int, y: int, focus: bool) -> bool:
        """
        Move the cursor to the location clicked for button 1.

        >>> size = (20,)
        >>> e = Edit("","words here")
        >>> e.mouse_event(size, 'mouse press', 1, 2, 0, True)
        True
        >>> e.edit_pos
        2
        """
        (maxcol,) = size
        if button == 1:
            return self.move_cursor_to_coords((maxcol,), x, y)
        return False

    def _delete_highlighted(self) -> bool:
        """
        Delete all highlighted text and update cursor position, if any
        text is highlighted.
        """
        if not self.highlight:
            return False
        start, stop = self.highlight
        btext, etext = self.edit_text[:start], self.edit_text[stop:]
        self.set_edit_text(btext + etext)
        self.edit_pos = start
        self.highlight = None
        return True

    def render(self, size: tuple[int], focus: bool = False) -> TextCanvas | CompositeCanvas:
        """
        Render edit widget and return canvas.  Include cursor when in
        focus.

        >>> c = Edit("? ","yes").render((10,), focus=True)
        >>> c.text # ... = b in Python 3
        [...'? yes     ']
        >>> c.cursor
        (5, 0)
        """
        self._shift_view_to_cursor = bool(focus)

        canv: TextCanvas | CompositeCanvas = super().render(size)
        if focus:
            canv = CompositeCanvas(canv)
            canv.cursor = self.get_cursor_coords(size)

        # .. will need to FIXME if I want highlight to work again
        # if self.highlight:
        #    hstart, hstop = self.highlight_coords()
        #    d.coords['highlight'] = [ hstart, hstop ]
        return canv

    def get_line_translation(self, maxcol: int, ta=None):
        trans = Text.get_line_translation(self, maxcol, ta)
        if not self._shift_view_to_cursor:
            return trans

        text, ignore = self.get_text()
        x, y = text_layout.calc_coords(text, trans, self.edit_pos + len(self.caption))
        if x < 0:
            return [
                *trans[:y],
                *[text_layout.shift_line(trans[y], -x)],
                *trans[y + 1 :],
            ]

        if x >= maxcol:
            return [
                *trans[:y],
                *[text_layout.shift_line(trans[y], -(x - maxcol + 1))],
                *trans[y + 1 :],
            ]

        return trans

    def get_cursor_coords(self, size: tuple[int]) -> tuple[int, int]:
        """
        Return the (*x*, *y*) coordinates of cursor within widget.

        >>> Edit("? ","yes").get_cursor_coords((10,))
        (5, 0)
        """
        (maxcol,) = size

        self._shift_view_to_cursor = True
        return self.position_coords(maxcol, self.edit_pos)

    def position_coords(self, maxcol: int, pos) -> tuple[int, int]:
        """
        Return (*x*, *y*) coordinates for an offset into self.edit_text.
        """

        p = pos + len(self.caption)
        trans = self.get_line_translation(maxcol)
        x, y = text_layout.calc_coords(self.get_text()[0], trans, p)
        return x, y


class IntEdit(Edit):
    """Edit widget for integer values"""

    def valid_char(self, ch):
        """
        Return true for decimal digits.
        """
        return len(ch) == 1 and ch in string.digits

    def __init__(self, caption="", default: int | str | None = None) -> None:
        """
        caption -- caption markup
        default -- default edit value

        >>> IntEdit(u"", 42)
        <IntEdit selectable flow widget '42' edit_pos=2>
        """
        if default is not None:
            val = str(default)
        else:
            val = ""
        super().__init__(caption, val)

    def keypress(self, size: tuple[int], key: str) -> str | None:
        """
        Handle editing keystrokes.  Remove leading zeros.

        >>> e, size = IntEdit(u"", 5002), (10,)
        >>> e.keypress(size, 'home')
        >>> e.keypress(size, 'delete')
        >>> print(e.edit_text)
        002
        >>> e.keypress(size, 'end')
        >>> print(e.edit_text)
        2
        """
        unhandled = super().keypress(size, key)

        if not unhandled:
            # trim leading zeros
            while self.edit_pos > 0 and self.edit_text[:1] == "0":
                self.set_edit_pos(self.edit_pos - 1)
                self.set_edit_text(self.edit_text[1:])

        return unhandled

    def value(self) -> int:
        """
        Return the numeric value of self.edit_text.

        >>> e, size = IntEdit(), (10,)
        >>> e.keypress(size, '5')
        >>> e.keypress(size, '1')
        >>> e.value() == 51
        True
        """
        if self.edit_text:
            return int(self.edit_text)

        return 0
