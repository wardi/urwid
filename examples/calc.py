#!/usr/bin/env python
#
# Urwid advanced example column calculator application
#    Copyright (C) 2004-2009  Ian Ward
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

"""
Urwid advanced example column calculator application

Features:
- multiple separate list boxes within columns
- custom edit widget for editing calculator cells
- custom parent widget for links to other columns
- custom list walker to show and hide cell results as required
- custom wrap and align modes for editing right-1 aligned numbers
- outputs commands that may be used to recreate expression on exit
"""


from __future__ import annotations

import operator
import string
import typing

import urwid
import urwid.raw_display
import urwid.web_display

# use appropriate Screen class
if urwid.web_display.is_web_request():
    Screen = urwid.web_display.Screen
else:
    Screen = urwid.raw_display.Screen


def div_or_none(a, b):
    """Divide a by b. Return result or None on divide by zero."""
    if b == 0:
        return None
    return a / b


# operators supported and the functions used to calculate a result
OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": div_or_none,
}

# the uppercase versions of keys used to switch columns
COLUMN_KEYS = list("?ABCDEF")

# these lists are used to determine when to display errors
EDIT_KEYS = list(OPERATORS.keys()) + COLUMN_KEYS + ["backspace", "delete"]
MOVEMENT_KEYS = ["up", "down", "left", "right", "page up", "page down"]

# Event text
E_no_such_column = "Column %s does not exist."
E_no_more_columns = "Maxumum number of columns reached."
E_new_col_cell_not_empty = "Column must be started from an empty cell."
E_invalid_key = "Invalid key '%s'."
E_no_parent_column = "There is no parent column to return to."
E_cant_combine = "Cannot combine cells with sub-expressions."
E_invalid_in_parent_cell = "Cannot enter numbers into parent cell."
E_invalid_in_help_col = [
    "Help Column is in focus.  Press ",
    ("key", COLUMN_KEYS[1]),
    "-",
    ("key", COLUMN_KEYS[-1]),
    " to select another column.",
]

# Shared layout object
CALC_LAYOUT = None


class CalcEvent(Exception):
    """Events triggered by user input."""

    attr = "event"

    def __init__(self, message):
        self.message = message

    def widget(self):
        """Return a widget containing event information"""
        text = urwid.Text(self.message, "center")
        return urwid.AttrMap(text, self.attr)


class ColumnDeleteEvent(CalcEvent):
    """Sent when user wants to delete a column"""

    attr = "confirm"

    def __init__(self, letter, from_parent=0):
        self.message = ["Press ", ("key", "BACKSPACE"), " again to confirm column removal."]
        self.letter = letter


class UpdateParentEvent(Exception):
    """Sent when parent columns may need to be updated."""

    pass


class Cell:
    def __init__(self, op):
        self.op = op
        self.is_top = op is None
        self.child = None
        self.setup_edit()
        self.result = urwid.Text("", layout=CALC_LAYOUT)

    def show_result(self, next_cell):
        """Return whether this widget should display its result.

        next_cell -- the cell following self or None"""

        if self.is_top:
            return False
        if next_cell is None:
            return True
        if self.op == next_cell.op == "+":
            return False
        return True

    def setup_edit(self):
        """Create the standard edit widget for this cell."""

        self.edit = urwid.IntEdit()
        if not self.is_top:
            self.edit.set_caption(f"{self.op} ")
        self.edit.set_layout(None, None, CALC_LAYOUT)

    def get_value(self):
        """Return the numeric value of the cell."""

        if self.child is not None:
            return self.child.get_result()

        return int(f"0{self.edit.edit_text}")

    def get_result(self):
        """Return the numeric result of this cell's operation."""

        if self.is_top:
            return self.get_value()
        if self.result.text == "":
            return None
        return int(self.result.text)

    def set_result(self, result):
        """Set the numeric result for this cell."""

        if result is None:
            self.result.set_text("")
        else:
            self.result.set_text("%d" % result)

    def become_parent(self, column, letter):
        """Change the edit widget to a parent cell widget."""

        self.child = column
        self.edit = ParentEdit(self.op, letter)

    def remove_child(self):
        """Change the edit widget back to a standard edit widget."""

        self.child = None
        self.setup_edit()

    def is_empty(self):
        """Return True if the cell is "empty"."""

        return self.child is None and self.edit.edit_text == ""


class ParentEdit(urwid.Edit):
    """Edit widget modified to link to a child column"""

    def __init__(self, op, letter):
        """Use the operator and letter of the child column as caption

        op -- operator or None
        letter -- letter of child column
        remove_fn -- function to call when user wants to remove child
                     function takes no parameters
        """

        super().__init__(layout=CALC_LAYOUT)
        self.op = op
        self.set_letter(letter)

    def set_letter(self, letter):
        """Set the letter of the child column for display."""

        self.letter = letter
        caption = f"({letter})"
        if self.op is not None:
            caption = f"{self.op} {caption}"
        self.set_caption(caption)

    def keypress(self, size, key):
        """Disable usual editing, allow only removing of child"""

        if key == "backspace":
            raise ColumnDeleteEvent(self.letter, from_parent=True)
        if key in string.digits:
            raise CalcEvent(E_invalid_in_parent_cell)

        return key


class CellWalker(urwid.ListWalker):
    def __init__(self, content):
        self.content = urwid.MonitoredList(content)
        self.content.modified = self._modified
        self.focus = (0, 0)
        # everyone can share the same divider widget
        self.div = urwid.Divider("-")

    def get_cell(self, i):
        if i < 0 or i >= len(self.content):
            return None

        return self.content[i]

    def _get_at_pos(self, pos):
        i, sub = pos
        assert sub in (0, 1, 2)  # noqa: S101  # for examples "assert" is acceptable
        if i < 0 or i >= len(self.content):
            return None, None
        if sub == 0:
            edit = self.content[i].edit
            return urwid.AttrMap(edit, "edit", "editfocus"), pos
        if sub == 1:
            return self.div, pos

        return self.content[i].result, pos

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus):
        self.focus = focus

    def get_next(self, start_from):
        i, sub = start_from
        assert sub in (0, 1, 2)  # noqa: S101  # for examples "assert" is acceptable
        if sub == 0:
            show_result = self.content[i].show_result(self.get_cell(i + 1))
            if show_result:
                return self._get_at_pos((i, 1))

            return self._get_at_pos((i + 1, 0))
        if sub == 1:
            return self._get_at_pos((i, 2))

        return self._get_at_pos((i + 1, 0))

    def get_prev(self, start_from):
        i, sub = start_from
        assert sub in (0, 1, 2)  # noqa: S101  # for examples "assert" is acceptable
        if sub == 0:
            if i == 0:
                return None, None
            show_result = self.content[i - 1].show_result(self.content[i])
            if show_result:
                return self._get_at_pos((i - 1, 2))

            return self._get_at_pos((i - 1, 0))
        if sub == 1:
            return self._get_at_pos((i, 0))

        return self._get_at_pos((i, 1))


class CellColumn(urwid.WidgetWrap):
    def __init__(self, letter):
        self.walker = CellWalker([Cell(None)])
        self.content = self.walker.content
        self.listbox = urwid.ListBox(self.walker)
        self.set_letter(letter)
        super().__init__(self.frame)

    def set_letter(self, letter):
        """Set the column header with letter."""

        self.letter = letter
        header = urwid.AttrMap(urwid.Text(["Column ", ("key", letter)], layout=CALC_LAYOUT), "colhead")
        self.frame = urwid.Frame(self.listbox, header)

    def keypress(self, size, key):
        key = self.frame.keypress(size, key)
        if key is None:
            changed = self.update_results()
            if changed:
                raise UpdateParentEvent()
            return None

        f, (i, sub) = self.walker.get_focus()
        if sub != 0:
            # f is not an edit widget
            return key
        if key in OPERATORS:
            # move trailing text to new cell below
            edit = self.walker.get_cell(i).edit
            cursor_pos = edit.edit_pos
            tail = edit.edit_text[cursor_pos:]
            edit.set_edit_text(edit.edit_text[:cursor_pos])

            new_cell = Cell(key)
            new_cell.edit.set_edit_text(tail)
            self.content[i + 1 : i + 1] = [new_cell]

            changed = self.update_results()
            self.move_focus_next(size)
            self.content[i + 1].edit.set_edit_pos(0)
            if changed:
                raise UpdateParentEvent()
            return None

        if key == "backspace":
            # unhandled backspace, we're at beginning of number
            # append current number to cell above, removing operator
            above = self.walker.get_cell(i - 1)
            if above is None:
                # we're the first cell
                raise ColumnDeleteEvent(self.letter, from_parent=False)

            edit = self.walker.get_cell(i).edit
            # check that we can combine
            if above.child is not None:
                # cell above is parent
                if edit.edit_text:
                    # ..and current not empty, no good
                    raise CalcEvent(E_cant_combine)
                above_pos = 0
            else:
                # above is normal number cell
                above_pos = len(above.edit.edit_text)
                above.edit.set_edit_text(above.edit.edit_text + edit.edit_text)

            self.move_focus_prev(size)
            self.content[i - 1].edit.set_edit_pos(above_pos)
            del self.content[i]
            changed = self.update_results()
            if changed:
                raise UpdateParentEvent()
            return None

        if key == "delete":
            # pull text from next cell into current
            cell = self.walker.get_cell(i)
            below = self.walker.get_cell(i + 1)
            if cell.child is not None:
                # this cell is a parent
                raise CalcEvent(E_cant_combine)
            if below is None:
                # nothing below
                return key
            if below.child is not None:
                # cell below is a parent
                raise CalcEvent(E_cant_combine)

            edit = self.walker.get_cell(i).edit
            edit.set_edit_text(edit.edit_text + below.edit.edit_text)

            del self.content[i + 1]
            changed = self.update_results()
            if changed:
                raise UpdateParentEvent()
            return None
        return key

    def move_focus_next(self, size):
        f, (i, sub) = self.walker.get_focus()
        assert i < len(self.content) - 1  # noqa: S101  # for examples "assert" is acceptable

        ni = i
        while ni == i:
            self.frame.keypress(size, "down")
            nf, (ni, nsub) = self.walker.get_focus()

    def move_focus_prev(self, size):
        f, (i, sub) = self.walker.get_focus()
        assert i > 0  # noqa: S101  # for examples "assert" is acceptable

        ni = i
        while ni == i:
            self.frame.keypress(size, "up")
            nf, (ni, nsub) = self.walker.get_focus()

    def update_results(self, start_from=None):
        """Update column.  Return True if final result changed.

        start_from -- Cell to start updating from or None to start from
                      the current focus (default None)
        """

        if start_from is None:
            f, (i, sub) = self.walker.get_focus()
        else:
            i = self.content.index(start_from)
            if i is None:
                return False

        focus_cell = self.walker.get_cell(i)

        if focus_cell.is_top:
            x = focus_cell.get_value()
        else:
            last_cell = self.walker.get_cell(i - 1)
            x = last_cell.get_result()

            if x is not None and focus_cell.op is not None:
                x = OPERATORS[focus_cell.op](x, focus_cell.get_value())
            focus_cell.set_result(x)

        for cell in self.content[i + 1 :]:
            if cell.op is None:
                x = None
            if x is not None:
                x = OPERATORS[cell.op](x, cell.get_value())
            if cell.get_result() == x:
                return False
            cell.set_result(x)

        return True

    def create_child(self, letter):
        """Return (parent cell,child column) or None,None on failure."""
        f, (i, sub) = self.walker.get_focus()
        if sub != 0:
            # f is not an edit widget
            return None, None

        cell = self.walker.get_cell(i)
        if cell.child is not None:
            raise CalcEvent(E_new_col_cell_not_empty)
        if cell.edit.edit_text:
            raise CalcEvent(E_new_col_cell_not_empty)

        child = CellColumn(letter)
        cell.become_parent(child, letter)

        return cell, child

    def is_empty(self):
        """Return True if this column is empty."""

        return len(self.content) == 1 and self.content[0].is_empty()

    def get_expression(self):
        """Return the expression as a printable string."""

        lines = []
        for c in self.content:
            if c.op is not None:  # only applies to first cell
                lines.append(c.op)
            if c.child is not None:
                lines.append(f"({c.child.get_expression()})")
            else:
                lines.append(f"{c.get_value():d}")

        return "".join(lines)

    def get_result(self):
        """Return the result of the last cell in the column."""

        return self.content[-1].get_result()


class HelpColumn(urwid.Widget):
    _selectable = True
    _sizing = frozenset((urwid.BOX,))

    help_text = [  # noqa: RUF012  # text layout typing is too complex
        ("title", "Column Calculator"),
        "",
        ["Numbers: ", ("key", "0"), "-", ("key", "9")],
        "",
        ["Operators: ", ("key", "+"), ", ", ("key", "-"), ", ", ("key", "*"), " and ", ("key", "/")],
        "",
        ["Editing: ", ("key", "BACKSPACE"), " and ", ("key", "DELETE")],
        "",
        [
            "Movement: ",
            ("key", "UP"),
            ", ",
            ("key", "DOWN"),
            ", ",
            ("key", "LEFT"),
            ", ",
            ("key", "RIGHT"),
            ", ",
            ("key", "PAGE UP"),
            " and ",
            ("key", "PAGE DOWN"),
        ],
        "",
        ["Sub-expressions: ", ("key", "("), " and ", ("key", ")")],
        "",
        ["Columns: ", ("key", COLUMN_KEYS[0]), " and ", ("key", COLUMN_KEYS[1]), "-", ("key", COLUMN_KEYS[-1])],
        "",
        ["Exit: ", ("key", "Q")],
        "",
        "",
        [
            "Column Calculator does operations in the order they are ",
            "typed, not by following usual precedence rules.  ",
            "If you want to calculate ",
            ("key", "12 - 2 * 3"),
            " with the multiplication happening before the ",
            "subtraction you must type ",
            ("key", "12 - (2 * 3)"),
            " instead.",
        ],
    ]

    def __init__(self):
        self.head = urwid.AttrMap(urwid.Text(["Help Column ", ("key", "?")], layout=CALC_LAYOUT), "help")
        self.foot = urwid.AttrMap(urwid.Text(["[text continues.. press ", ("key", "?"), " then scroll]"]), "helpnote")
        self.items = [urwid.Text(x) for x in self.help_text]
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(self.items))
        self.body = urwid.AttrMap(self.listbox, "help")
        self.frame = urwid.Frame(self.body, header=self.head)

    def render(self, size, focus=False):
        maxcol, maxrow = size
        head_rows = self.head.rows((maxcol,))
        if "bottom" in self.listbox.ends_visible((maxcol, maxrow - head_rows)):
            self.frame.footer = None
        else:
            self.frame.footer = self.foot

        return self.frame.render((maxcol, maxrow), focus)

    def keypress(self, size, key):
        return self.frame.keypress(size, key)


class CalcDisplay:
    palette: typing.ClassVar[list[tuple[str, str, str, ...]]] = [
        ("body", "white", "dark blue"),
        ("edit", "yellow", "dark blue"),
        ("editfocus", "yellow", "dark cyan", "bold"),
        ("key", "dark cyan", "light gray", ("standout", "underline")),
        ("title", "white", "light gray", ("bold", "standout")),
        ("help", "black", "light gray", "standout"),
        ("helpnote", "dark green", "light gray"),
        ("colhead", "black", "light gray", "standout"),
        ("event", "light red", "black", "standout"),
        ("confirm", "yellow", "black", "bold"),
    ]

    def __init__(self):
        self.columns = urwid.Columns([HelpColumn(), CellColumn("A")], 1)
        self.col_list = self.columns.widget_list
        self.columns.focus_position = 1
        view = urwid.AttrMap(self.columns, "body")
        self.view = urwid.Frame(view)  # for showing messages
        self.col_link = {}

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette, screen=Screen(), input_filter=self.input_filter)
        self.loop.run()

        # on exit write the formula and the result to the console
        expression, result = self.get_expression_result()
        print("Paste this expression into a new Column Calculator session to continue editing:")
        print(expression)
        print("Result:", result)

    def input_filter(self, data, raw_input):
        if "q" in data or "Q" in data:
            raise urwid.ExitMainLoop()

        # handle other keystrokes
        for k in data:
            try:
                self.wrap_keypress(k)
                self.event = None
                self.view.footer = None
            except CalcEvent as e:  # noqa: PERF203
                # display any message
                self.event = e
                self.view.footer = e.widget()

        # remove all input from further processing by MainLoop
        return []

    def wrap_keypress(self, key):
        """Handle confirmation and throw event on bad input."""

        try:
            key = self.keypress(key)

        except ColumnDeleteEvent as e:
            if e.letter == COLUMN_KEYS[1]:
                # cannot delete the first column, ignore key
                return

            if not self.column_empty(e.letter) and not isinstance(self.event, ColumnDeleteEvent):
                # need to get two in a row, so check last event ask for confirmation
                raise
            self.delete_column(e.letter)

        except UpdateParentEvent:
            self.update_parent_columns()
            return

        if key is None:
            return

        if self.columns.focus_position == 0 and key not in ("up", "down", "page up", "page down"):
            raise CalcEvent(E_invalid_in_help_col)

        if key not in EDIT_KEYS and key not in MOVEMENT_KEYS:
            raise CalcEvent(E_invalid_key % key.upper())

    def keypress(self, key):
        """Handle a keystroke."""

        self.loop.process_input([key])

        if isinstance(key, tuple):
            # ignore mouse events
            return None

        if key.upper() in COLUMN_KEYS:
            # column switch
            i = COLUMN_KEYS.index(key.upper())
            if i >= len(self.columns):
                raise CalcEvent(E_no_such_column % key.upper())
            self.columns.focus_position = i
            return None
        if key == "(":
            # open a new column
            if len(self.columns) >= len(COLUMN_KEYS):
                raise CalcEvent(E_no_more_columns)
            i = self.columns.focus_position
            if i == 0:
                # makes no sense in help column
                return key
            col = self.columns.contents[i][0]
            new_letter = COLUMN_KEYS[len(self.columns)]
            parent, child = col.create_child(new_letter)
            if child is None:
                # something invalid in focus
                return key
            self.col_list.append(child)
            self.set_link(parent, col, child)
            self.columns.focus_position = len(self.columns) - 1
            return None

        if key == ")":
            i = self.columns.focus_position
            if i == 0:
                # makes no sense in help column
                return key
            col = self.columns.contents[i][0]
            parent, pcol = self.get_parent(col)
            if parent is None:
                # column has no parent
                raise CalcEvent(E_no_parent_column)

            new_i = self.col_list.index(pcol)
            self.columns.focus_position = new_i
            return None

        return key

    def set_link(self, parent, pcol, child):
        """Store the link between a parent cell and child column.

        parent -- parent Cell object
        pcol -- CellColumn where parent resides
        child -- child CellColumn object"""

        self.col_link[child] = parent, pcol

    def get_parent(self, child):
        """Return the parent and parent column for a given column."""

        return self.col_link.get(child, (None, None))

    def column_empty(self, letter):
        """Return True if the column passed is empty."""

        i = COLUMN_KEYS.index(letter)
        col = self.columns.contents[i][0]
        return col.is_empty()

    def delete_column(self, letter):
        """Delete the column with the given letter."""

        i = COLUMN_KEYS.index(letter)
        col = self.columns.contents[i][0]

        parent, pcol = self.get_parent(col)

        f = self.columns.focus_position
        if f == i:
            # move focus to the parent column
            f = self.col_list.index(pcol)
            self.columns.focus_position = f

        parent.remove_child()
        pcol.update_results(parent)
        del self.columns.contents[i]

        # delete children of this column
        keep_right_cols = []
        remove_cols = [col]
        for rcol in self.col_list[i:]:
            parent, pcol = self.get_parent(rcol)
            if pcol in remove_cols:
                remove_cols.append(rcol)
            else:
                keep_right_cols.append(rcol)
        for rc in remove_cols:
            # remove the links
            del self.col_link[rc]
        # keep only the non-children
        self.col_list[i:] = keep_right_cols

        # fix the letter assignments
        for j in range(i, len(self.columns)):
            col = self.columns.contents[j][0]
            # fix the column heading
            col.set_letter(COLUMN_KEYS[j])
            parent, pcol = self.get_parent(col)
            # fix the parent cell
            parent.edit.set_letter(COLUMN_KEYS[j])

    def update_parent_columns(self):
        "Update the parent columns of the current focus column."

        f = self.columns.focus_position
        col = self.columns.contents[f][0]
        while 1:
            parent, pcol = self.get_parent(col)
            if pcol is None:
                return

            changed = pcol.update_results(start_from=parent)
            if not changed:
                return
            col = pcol

    def get_expression_result(self):
        """Return (expression, result) as strings."""

        col = self.columns.contents[1][0]
        return col.get_expression(), f"{col.get_result():d}"


class CalcNumLayout(urwid.TextLayout):
    """
    TextLayout class for bottom-right aligned numbers with a space on
    the last line for the cursor.
    """

    def layout(self, text, width, align, wrap):
        """
        Return layout structure for calculator number display.
        """
        lt = len(text) + 1  # extra space for cursor
        remaining = lt % width  # remaining segment not full width wide
        linestarts = range(remaining, lt, width)
        layout = []
        if linestarts:
            if remaining:
                # right-align the remaining segment on 1st line
                layout.append([(width - remaining, None), (remaining, 0, remaining)])
            # fill all but the last line
            for x in linestarts[:-1]:
                layout.append([(width, x, x + width)])  # noqa: PERF401
            s = linestarts[-1]
            # add the last line with a cursor hint
            layout.append([(width - 1, s, lt - 1), (0, lt - 1)])
        elif lt - 1:
            # all fits on one line, so right align the text
            # with a cursor hint at the end
            layout.append([(width - lt, None), (lt - 1, 0, lt - 1), (0, lt - 1)])
        else:
            # nothing on the line, right align a cursor hint
            layout.append([(width - 1, None), (0, 0)])

        return layout


def main():
    """Launch Column Calculator."""
    global CALC_LAYOUT  # noqa: PLW0603
    CALC_LAYOUT = CalcNumLayout()

    urwid.web_display.set_preferences("Column Calculator")
    # try to handle short web requests quickly
    if urwid.web_display.handle_short_request():
        return

    CalcDisplay().main()


if __name__ == "__main__" or urwid.web_display.is_web_request():
    main()
