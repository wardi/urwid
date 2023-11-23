# Urwid Window-Icon-Menu-Pointer-style widget classes
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

from urwid.canvas import CompositeCanvas
from urwid.command_map import Command
from urwid.signals import connect_signal
from urwid.text_layout import calc_coords
from urwid.util import is_mouse_press

from .columns import Columns
from .constants import Align, Sizing, WrapMode
from .text import Text
from .widget import WidgetWrap

if typing.TYPE_CHECKING:
    from collections.abc import Callable, MutableSequence

    from typing_extensions import Literal, Self

    from urwid.canvas import TextCanvas
    from urwid.text_layout import TextLayout

    _T = typing.TypeVar("_T")


class SelectableIcon(Text):
    ignore_focus = False
    _selectable = True

    def __init__(
        self,
        text,
        cursor_position: int = 0,
        align: Literal["left", "center", "right"] | Align = Align.LEFT,
        wrap: Literal["space", "any", "clip", "ellipsis"] | WrapMode = WrapMode.SPACE,
        layout: TextLayout | None = None,
    ) -> None:
        """
        :param text: markup for this widget; see :class:`Text` for
                     description of text markup
        :param cursor_position: position the cursor will appear in the
                                text when this widget is in focus
        :param align: typically ``'left'``, ``'center'`` or ``'right'``
        :type align: text alignment mode
        :param wrap: typically ``'space'``, ``'any'``, ``'clip'`` or ``'ellipsis'``
        :type wrap: text wrapping mode
        :param layout: defaults to a shared :class:`StandardTextLayout` instance
        :type layout: text layout instance

        This is a text widget that is selectable.  A cursor
        displayed at a fixed location in the text when in focus.
        This widget has no special handling of keyboard or mouse input.
        """
        super().__init__(text, align=align, wrap=wrap, layout=layout)
        self._cursor_position = cursor_position

    def render(self, size: tuple[int], focus: bool = False) -> TextCanvas | CompositeCanvas:  # type: ignore[override]
        """
        Render the text content of this widget with a cursor when
        in focus.

        >>> si = SelectableIcon(u"[!]")
        >>> si
        <SelectableIcon selectable flow widget '[!]'>
        >>> si.render((4,), focus=True).cursor
        (0, 0)
        >>> si = SelectableIcon("((*))", 2)
        >>> si.render((8,), focus=True).cursor
        (2, 0)
        >>> si.render((2,), focus=True).cursor
        (0, 1)
        """
        c: TextCanvas | CompositeCanvas = super().render(size, focus)
        if focus:
            # create a new canvas so we can add a cursor
            c = CompositeCanvas(c)
            c.cursor = self.get_cursor_coords(size)
        return c

    def get_cursor_coords(self, size: tuple[int]) -> tuple[int, int] | None:
        """
        Return the position of the cursor if visible.  This method
        is required for widgets that display a cursor.
        """
        if self._cursor_position > len(self.text):
            return None
        # find out where the cursor will be displayed based on
        # the text layout
        (maxcol,) = size
        trans = self.get_line_translation(maxcol)
        x, y = calc_coords(self.text, trans, self._cursor_position)
        if maxcol <= x:
            return None
        return x, y

    def keypress(self, size: tuple[int], key: str) -> str:
        """
        No keys are handled by this widget.  This method is
        required for selectable widgets.
        """
        return key


class CheckBoxError(Exception):
    pass


class CheckBox(WidgetWrap):
    def sizing(self):
        return frozenset([Sizing.FLOW])

    states: typing.ClassVar[dict[bool | Literal["mixed"], SelectableIcon]] = {
        True: SelectableIcon("[X]", 1),
        False: SelectableIcon("[ ]", 1),
        "mixed": SelectableIcon("[#]", 1),
    }
    reserve_columns = 4

    # allow users of this class to listen for change events
    # sent when the state of this widget is modified
    # (this variable is picked up by the MetaSignals metaclass)
    signals: typing.ClassVar[list[str]] = ["change", "postchange"]

    @typing.overload
    def __init__(
        self,
        label,
        state: bool = False,
        has_mixed: typing.Literal[False] = False,
        on_state_change: Callable[[Self, bool, _T], typing.Any] | None = None,
        user_data: _T = ...,
        checked_symbol: str | None = ...,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        label,
        state: bool = False,
        has_mixed: typing.Literal[False] = False,
        on_state_change: Callable[[Self, bool], typing.Any] | None = None,
        user_data: None = None,
        checked_symbol: str | None = ...,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        label: str,
        state: typing.Literal["mixed"] | bool = False,
        has_mixed: typing.Literal[True] = True,
        on_state_change: Callable[[Self, bool | typing.Literal["mixed"], _T], typing.Any] | None = None,
        user_data: _T = ...,
        checked_symbol: str | None = ...,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        label: str,
        state: typing.Literal["mixed"] | bool = False,
        has_mixed: typing.Literal[True] = True,
        on_state_change: Callable[[Self, bool | typing.Literal["mixed"]], typing.Any] | None = None,
        user_data: None = None,
        checked_symbol: str | None = ...,
    ) -> None:
        ...

    def __init__(
        self,
        label,
        state: bool | Literal["mixed"] = False,
        has_mixed: typing.Literal[False, True] = False,  # MyPy issue: Literal[True, False] is not equal `bool`
        on_state_change: (
            Callable[[Self, bool, _T], typing.Any]
            | Callable[[Self, bool], typing.Any]
            | Callable[[Self, bool | typing.Literal["mixed"], _T], typing.Any]
            | Callable[[Self, bool | typing.Literal["mixed"]], typing.Any]
            | None
        ) = None,
        user_data: _T | None = None,
        checked_symbol: str | None = None,
    ):
        """
        :param label: markup for check box label
        :param state: False, True or "mixed"
        :param has_mixed: True if "mixed" is a state to cycle through
        :param on_state_change: shorthand for connect_signal()
                                function call for a single callback
        :param user_data: user_data for on_state_change

        ..note:: `pack` method expect, that `Columns` backend widget is not modified from outside

        Signals supported: ``'change'``, ``"postchange"``

        Register signal handler with::

          urwid.connect_signal(check_box, 'change', callback, user_data)

        where callback is callback(check_box, new_state [,user_data])
        Unregister signal handlers with::

          urwid.disconnect_signal(check_box, 'change', callback, user_data)

        >>> CheckBox("Confirm")
        <CheckBox selectable flow widget 'Confirm' state=False>
        >>> CheckBox("Yogourt", "mixed", True)
        <CheckBox selectable flow widget 'Yogourt' state='mixed'>
        >>> cb = CheckBox("Extra onions", True)
        >>> cb
        <CheckBox selectable flow widget 'Extra onions' state=True>
        >>> cb.render((20,), focus=True).text
        [b'[X] Extra onions    ']
        >>> CheckBox("Test", None)
        Traceback (most recent call last):
        ...
        ValueError: None not in (True, False, 'mixed')
        """
        if state not in self.states:
            raise ValueError(f"{state!r} not in {tuple(self.states.keys())}")

        self._label = Text(label)
        self.has_mixed = has_mixed

        self._state = state
        if checked_symbol:
            self.states[True] = SelectableIcon(f"[{checked_symbol}]", 1)
        # The old way of listening for a change was to pass the callback
        # in to the constructor.  Just convert it to the new way:
        if on_state_change:
            connect_signal(self, "change", on_state_change, user_data)

        # Initial create expect no callbacks call, create explicit
        super().__init__(
            Columns(
                [(self.reserve_columns, self.states[state]), self._label],
                focus_column=0,
            ),
        )

    def pack(self, size: tuple[int] | None = None, focus: bool = False) -> tuple[str, str]:
        """Pack for widget.

        :param size: size data. Special case: None - get minimal widget size to fit
        :param focus: widget is focused

        >>> cb = CheckBox("test")
        >>> cb.pack((10,))
        (10, 1)
        >>> cb.pack()
        (8, 1)
        >>> ml_cb = CheckBox("Multi\\nline\\ncheckbox")
        >>> ml_cb.pack()
        (12, 3)
        """
        if size is not None:
            return super().pack(size, focus)

        width, _height = self._label.pack()
        width += self.reserve_columns
        return width, self.rows((width,))

    def _repr_words(self) -> list[str]:
        return [*super()._repr_words(), repr(self.label)]

    def _repr_attrs(self):
        return dict(super()._repr_attrs(), state=self.state)

    def set_label(self, label):
        """
        Change the check box label.

        label -- markup for label.  See Text widget for description
        of text markup.

        >>> cb = CheckBox(u"foo")
        >>> cb
        <CheckBox selectable flow widget 'foo' state=False>
        >>> cb.set_label(('bright_attr', u"bar"))
        >>> cb
        <CheckBox selectable flow widget 'bar' state=False>
        """
        self._label.set_text(label)
        # no need to call self._invalidate(). WidgetWrap takes care of
        # that when self.w changes

    def get_label(self):
        """
        Return label text.

        >>> cb = CheckBox(u"Seriously")
        >>> print(cb.get_label())
        Seriously
        >>> print(cb.label)
        Seriously
        >>> cb.set_label([('bright_attr', u"flashy"), u" normal"])
        >>> print(cb.label)  #  only text is returned
        flashy normal
        """
        return self._label.text

    label = property(get_label)

    def set_state(
        self,
        state: bool | Literal["mixed"],
        do_callback: bool = True,
    ) -> None:
        """
        Set the CheckBox state.

        state -- True, False or "mixed"
        do_callback -- False to suppress signal from this change

        >>> from urwid import disconnect_signal
        >>> changes = []
        >>> def callback_a(user_data, cb, state):
        ...     changes.append("A %r %r" % (state, user_data))
        >>> def callback_b(cb, state):
        ...     changes.append("B %r" % state)
        >>> cb = CheckBox('test', False, False)
        >>> key1 = connect_signal(cb, 'change', callback_a, user_args=("user_a",))
        >>> key2 = connect_signal(cb, 'change', callback_b)
        >>> cb.set_state(True) # both callbacks will be triggered
        >>> cb.state
        True
        >>> disconnect_signal(cb, 'change', callback_a, user_args=("user_a",))
        >>> cb.state = False
        >>> cb.state
        False
        >>> cb.set_state(True)
        >>> cb.state
        True
        >>> cb.set_state(False, False) # don't send signal
        >>> changes
        ["A True 'user_a'", 'B True', 'B False', 'B True']
        """
        if self._state == state:
            return

        if state not in self.states:
            raise CheckBoxError(f"{self!r} Invalid state: {state!r}")

        # self._state is None is a special case when the CheckBox
        # has just been created
        old_state = self._state
        if do_callback:
            self._emit("change", state)
        self._state = state
        # rebuild the display widget with the new state
        self._w = Columns([(self.reserve_columns, self.states[state]), self._label], focus_column=0)
        if do_callback:
            self._emit("postchange", old_state)

    def get_state(self) -> bool | Literal["mixed"]:
        """Return the state of the checkbox."""
        return self._state

    state = property(get_state, set_state)

    def keypress(self, size: tuple[int], key: str) -> str | None:
        """
        Toggle state on 'activate' command.

        >>> assert CheckBox._command_map[' '] == 'activate'
        >>> assert CheckBox._command_map['enter'] == 'activate'
        >>> size = (10,)
        >>> cb = CheckBox('press me')
        >>> cb.state
        False
        >>> cb.keypress(size, ' ')
        >>> cb.state
        True
        >>> cb.keypress(size, ' ')
        >>> cb.state
        False
        """
        if self._command_map[key] != Command.ACTIVATE:
            return key

        self.toggle_state()
        return None

    def toggle_state(self) -> None:
        """
        Cycle to the next valid state.

        >>> cb = CheckBox("3-state", has_mixed=True)
        >>> cb.state
        False
        >>> cb.toggle_state()
        >>> cb.state
        True
        >>> cb.toggle_state()
        >>> cb.state
        'mixed'
        >>> cb.toggle_state()
        >>> cb.state
        False
        """
        if self.state is False:
            self.set_state(True)
        elif self.state is True:
            if self.has_mixed:
                self.set_state("mixed")
            else:
                self.set_state(False)
        elif self.state == "mixed":
            self.set_state(False)

    def mouse_event(self, size: tuple[int], event, button: int, x: int, y: int, focus: bool) -> bool:
        """
        Toggle state on button 1 press.

        >>> size = (20,)
        >>> cb = CheckBox("clickme")
        >>> cb.state
        False
        >>> cb.mouse_event(size, 'mouse press', 1, 2, 0, True)
        True
        >>> cb.state
        True
        """
        if button != 1 or not is_mouse_press(event):
            return False
        self.toggle_state()
        return True


class RadioButton(CheckBox):
    states: typing.ClassVar[dict[bool | Literal["mixed"], SelectableIcon]] = {
        True: SelectableIcon("(X)", 1),
        False: SelectableIcon("( )", 1),
        "mixed": SelectableIcon("(#)", 1),
    }
    reserve_columns = 4

    @typing.overload
    def __init__(
        self,
        group: MutableSequence[CheckBox],
        label,
        state: bool | Literal["first True"] = ...,
        on_state_change: Callable[[Self, bool, _T], typing.Any] | None = None,
        user_data: _T = ...,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        group: MutableSequence[CheckBox],
        label,
        state: bool | Literal["first True"] = ...,
        on_state_change: Callable[[Self, bool], typing.Any] | None = None,
        user_data: None = None,
    ) -> None:
        ...

    def __init__(
        self,
        group: MutableSequence[CheckBox],
        label,
        state: bool | Literal["first True"] = "first True",
        on_state_change: Callable[[Self, bool, _T], typing.Any] | Callable[[Self, bool], typing.Any] | None = None,
        user_data: _T | None = None,
    ) -> None:
        """
        :param group: list for radio buttons in same group
        :param label: markup for radio button label
        :param state: False, True, "mixed" or "first True"
        :param on_state_change: shorthand for connect_signal()
                                function call for a single 'change' callback
        :param user_data: user_data for on_state_change

        ..note:: `pack` method expect, that `Columns` backend widget is not modified from outside

        This function will append the new radio button to group.
        "first True" will set to True if group is empty.

        Signals supported: ``'change'``, ``"postchange"``

        Register signal handler with::

          urwid.connect_signal(radio_button, 'change', callback, user_data)

        where callback is callback(radio_button, new_state [,user_data])
        Unregister signal handlers with::

          urwid.disconnect_signal(radio_button, 'change', callback, user_data)

        >>> bgroup = [] # button group
        >>> b1 = RadioButton(bgroup, u"Agree")
        >>> b2 = RadioButton(bgroup, u"Disagree")
        >>> len(bgroup)
        2
        >>> b1
        <RadioButton selectable flow widget 'Agree' state=True>
        >>> b2
        <RadioButton selectable flow widget 'Disagree' state=False>
        >>> b2.render((15,), focus=True).text # ... = b in Python 3
        [...'( ) Disagree   ']
        """
        if state == "first True":
            state = not group

        self.group = group
        super().__init__(label, state, False, on_state_change, user_data)  # type: ignore[call-overload]
        group.append(self)

    def set_state(self, state: bool | Literal["mixed"], do_callback: bool = True) -> None:
        """
        Set the RadioButton state.

        state -- True, False or "mixed"

        do_callback -- False to suppress signal from this change

        If state is True all other radio buttons in the same button
        group will be set to False.

        >>> bgroup = [] # button group
        >>> b1 = RadioButton(bgroup, u"Agree")
        >>> b2 = RadioButton(bgroup, u"Disagree")
        >>> b3 = RadioButton(bgroup, u"Unsure")
        >>> b1.state, b2.state, b3.state
        (True, False, False)
        >>> b2.set_state(True)
        >>> b1.state, b2.state, b3.state
        (False, True, False)
        >>> def relabel_button(radio_button, new_state):
        ...     radio_button.set_label(u"Think Harder!")
        >>> key = connect_signal(b3, 'change', relabel_button)
        >>> b3
        <RadioButton selectable flow widget 'Unsure' state=False>
        >>> b3.set_state(True) # this will trigger the callback
        >>> b3
        <RadioButton selectable flow widget 'Think Harder!' state=True>
        """
        if self._state == state:
            return

        super().set_state(state, do_callback)

        # if we're clearing the state we don't have to worry about
        # other buttons in the button group
        if state is not True:
            return

        # clear the state of each other radio button
        for cb in self.group:
            if cb is self:
                continue
            if cb._state:
                cb.set_state(False)

    def toggle_state(self) -> None:
        """
        Set state to True.

        >>> bgroup = [] # button group
        >>> b1 = RadioButton(bgroup, "Agree")
        >>> b2 = RadioButton(bgroup, "Disagree")
        >>> b1.state, b2.state
        (True, False)
        >>> b2.toggle_state()
        >>> b1.state, b2.state
        (False, True)
        >>> b2.toggle_state()
        >>> b1.state, b2.state
        (False, True)
        """
        self.set_state(True)


class Button(WidgetWrap):
    def sizing(self):
        return frozenset([Sizing.FLOW])

    button_left = Text("<")
    button_right = Text(">")

    signals: typing.ClassVar[list[str]] = ["click"]

    @typing.overload
    def __init__(
        self,
        label,
        on_press: Callable[[Self, _T], typing.Any] | None = None,
        user_data: _T = ...,
        *,
        align: Literal["left", "center", "right"] | Align = ...,
        wrap: Literal["space", "any", "clip", "ellipsis"] | WrapMode = ...,
        layout: TextLayout | None = ...,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        label,
        on_press: Callable[[Self], typing.Any] | None = None,
        user_data: None = None,
        *,
        align: Literal["left", "center", "right"] | Align = ...,
        wrap: Literal["space", "any", "clip", "ellipsis"] | WrapMode = ...,
        layout: TextLayout | None = ...,
    ) -> None:
        ...

    def __init__(
        self,
        label,
        on_press: Callable[[Self, _T], typing.Any] | Callable[[Self], typing.Any] | None = None,
        user_data: _T | None = None,
        *,
        align: Literal["left", "center", "right"] | Align = Align.LEFT,
        wrap: Literal["space", "any", "clip", "ellipsis"] | WrapMode = WrapMode.SPACE,
        layout: TextLayout | None = None,
    ) -> None:
        """
        :param label: markup for button label
        :param on_press: shorthand for connect_signal()
                         function call for a single callback
        :param user_data: user_data for on_press
        :param align: typically ``'left'``, ``'center'`` or ``'right'``
        :type align: label alignment mode
        :param wrap: typically ``'space'``, ``'any'``, ``'clip'`` or ``'ellipsis'``
        :type wrap: label wrapping mode
        :param layout: defaults to a shared :class:`StandardTextLayout` instance
        :type layout: text layout instance

        ..note:: `pack` method expect, that `Columns` backend widget is not modified from outside

        Signals supported: ``'click'``

        Register signal handler with::

          urwid.connect_signal(button, 'click', callback, user_data)

        where callback is callback(button [,user_data])
        Unregister signal handlers with::

          urwid.disconnect_signal(button, 'click', callback, user_data)

        >>> Button(u"Ok")
        <Button selectable flow widget 'Ok'>
        >>> b = Button("Cancel")
        >>> b.render((15,), focus=True).text # ... = b in Python 3
        [b'< Cancel      >']
        >>> aligned_button = Button("Test", align=Align.CENTER)
        >>> aligned_button.render((10,), focus=True).text
        [b'<  Test  >']
        >>> wrapped_button = Button("Long label", wrap=WrapMode.ELLIPSIS)
        >>> wrapped_button.render((7,), focus=False).text[0].decode('utf-8')
        '< Lo… >'
        """
        self._label = SelectableIcon(label, 0, align=align, wrap=wrap, layout=layout)
        cols = Columns(
            [(1, self.button_left), self._label, (1, self.button_right)],
            dividechars=1,
        )
        super().__init__(cols)

        # The old way of listening for a change was to pass the callback
        # in to the constructor.  Just convert it to the new way:
        if on_press:
            connect_signal(self, "click", on_press, user_data)

    def pack(self, size: tuple[int] | None = None, focus: bool = False) -> tuple[int, int]:
        """Pack for widget.

        :param size: size data. Special case: None - get minimal widget size to fit
        :param focus: widget is focused

        >>> btn = Button("Some button")
        >>> btn.pack((10,))
        (10, 2)
        >>> btn.pack()
        (15, 1)
        """
        if size is not None:
            return super().pack(size, focus)

        width, _height = self._label.pack()
        width += 4  # We use Given sizing for button ends and `dividechars=1`
        return width, self.rows((width,))

    def _repr_words(self) -> list[str]:
        # include button.label in repr(button)
        return [*super()._repr_words(), repr(self.label)]

    def set_label(self, label) -> None:
        """
        Change the button label.

        label -- markup for button label

        >>> b = Button("Ok")
        >>> b.set_label(u"Yup yup")
        >>> b
        <Button selectable flow widget 'Yup yup'>
        """
        self._label.set_text(label)

    def get_label(self) -> str:
        """
        Return label text.

        >>> b = Button(u"Ok")
        >>> print(b.get_label())
        Ok
        >>> print(b.label)
        Ok
        """
        return self._label.text

    label = property(get_label)

    def keypress(self, size: tuple[int], key: str) -> str | None:
        """
        Send 'click' signal on 'activate' command.

        >>> assert Button._command_map[' '] == 'activate'
        >>> assert Button._command_map['enter'] == 'activate'
        >>> size = (15,)
        >>> b = Button(u"Cancel")
        >>> clicked_buttons = []
        >>> def handle_click(button):
        ...     clicked_buttons.append(button.label)
        >>> key = connect_signal(b, 'click', handle_click)
        >>> b.keypress(size, 'enter')
        >>> b.keypress(size, ' ')
        >>> clicked_buttons # ... = u in Python 2
        [...'Cancel', ...'Cancel']
        """
        if self._command_map[key] != Command.ACTIVATE:
            return key

        self._emit("click")
        return None

    def mouse_event(self, size: tuple[int], event, button: int, x: int, y: int, focus: bool) -> bool:
        """
        Send 'click' signal on button 1 press.

        >>> size = (15,)
        >>> b = Button(u"Ok")
        >>> clicked_buttons = []
        >>> def handle_click(button):
        ...     clicked_buttons.append(button.label)
        >>> key = connect_signal(b, 'click', handle_click)
        >>> b.mouse_event(size, 'mouse press', 1, 4, 0, True)
        True
        >>> b.mouse_event(size, 'mouse press', 2, 4, 0, True) # ignored
        False
        >>> clicked_buttons # ... = u in Python 2
        [...'Ok']
        """
        if button != 1 or not is_mouse_press(event):
            return False

        self._emit("click")
        return True


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
