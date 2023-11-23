# Urwid escape sequences common to curses_display and raw_display
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


"""
Terminal Escape Sequences for input and display
"""

from __future__ import annotations

import re
from collections.abc import MutableMapping, Sequence

try:
    from urwid import str_util
except ImportError:
    from urwid import old_str_util as str_util

# NOTE: because of circular imports (urwid.util -> urwid.escape -> urwid.util)
# from urwid.util import is_mouse_event -- will not work here
import urwid.util

within_double_byte = str_util.within_double_byte

SO = "\x0e"
SI = "\x0f"
IBMPC_ON = "\x1b[11m"
IBMPC_OFF = "\x1b[10m"

DEC_TAG = "0"
DEC_SPECIAL_CHARS = "▮◆▒␉␌␍␊°±␤␋┘┐┌└┼⎺⎻─⎼⎽├┤┴┬│≤≥π≠£·"
ALT_DEC_SPECIAL_CHARS = "_`abcdefghijklmnopqrstuvwxyz{|}~"

DEC_SPECIAL_CHARMAP = {}
if len(DEC_SPECIAL_CHARS) != len(ALT_DEC_SPECIAL_CHARS):
    raise RuntimeError(repr((DEC_SPECIAL_CHARS, ALT_DEC_SPECIAL_CHARS)))

for c, alt in zip(DEC_SPECIAL_CHARS, ALT_DEC_SPECIAL_CHARS):
    DEC_SPECIAL_CHARMAP[ord(c)] = SO + alt + SI

SAFE_ASCII_DEC_SPECIAL_RE = re.compile(f"^[ -~{DEC_SPECIAL_CHARS}]*$")
DEC_SPECIAL_RE = re.compile(f"[{DEC_SPECIAL_CHARS}]")


###################
## Input sequences
###################


class MoreInputRequired(Exception):
    pass


def escape_modifier(digit):
    mode = ord(digit) - ord("1")
    return "shift " * (mode & 1) + "meta " * ((mode & 2) // 2) + "ctrl " * ((mode & 4) // 4)


input_sequences = [
    ("[A", "up"),
    ("[B", "down"),
    ("[C", "right"),
    ("[D", "left"),
    ("[E", "5"),
    ("[F", "end"),
    ("[G", "5"),
    ("[H", "home"),
    ("[1~", "home"),
    ("[2~", "insert"),
    ("[3~", "delete"),
    ("[4~", "end"),
    ("[5~", "page up"),
    ("[6~", "page down"),
    ("[7~", "home"),
    ("[8~", "end"),
    ("[[A", "f1"),
    ("[[B", "f2"),
    ("[[C", "f3"),
    ("[[D", "f4"),
    ("[[E", "f5"),
    ("[11~", "f1"),
    ("[12~", "f2"),
    ("[13~", "f3"),
    ("[14~", "f4"),
    ("[15~", "f5"),
    ("[17~", "f6"),
    ("[18~", "f7"),
    ("[19~", "f8"),
    ("[20~", "f9"),
    ("[21~", "f10"),
    ("[23~", "f11"),
    ("[24~", "f12"),
    ("[25~", "f13"),
    ("[26~", "f14"),
    ("[28~", "f15"),
    ("[29~", "f16"),
    ("[31~", "f17"),
    ("[32~", "f18"),
    ("[33~", "f19"),
    ("[34~", "f20"),
    ("OA", "up"),
    ("OB", "down"),
    ("OC", "right"),
    ("OD", "left"),
    ("OH", "home"),
    ("OF", "end"),
    ("OP", "f1"),
    ("OQ", "f2"),
    ("OR", "f3"),
    ("OS", "f4"),
    ("Oo", "/"),
    ("Oj", "*"),
    ("Om", "-"),
    ("Ok", "+"),
    ("[Z", "shift tab"),
    ("On", "."),
    ("[200~", "begin paste"),
    ("[201~", "end paste"),
    *(
        (prefix + letter, modifier + key)
        for prefix, modifier in zip("O[", ("meta ", "shift "))
        for letter, key in zip("abcd", ("up", "down", "right", "left"))
    ),
    *(
        (f"[{digit}{symbol}", modifier + key)
        for modifier, symbol in zip(("shift ", "meta "), "$^")
        for digit, key in zip("235678", ("insert", "delete", "page up", "page down", "home", "end"))
    ),
    *((f"O{ord('p') + n:c}", str(n)) for n in range(10)),
    *(
        # modified cursor keys + home, end, 5 -- [#X and [1;#X forms
        (prefix + digit + letter, escape_modifier(digit) + key)
        for prefix in ("[", "[1;")
        for digit in "12345678"
        for letter, key in zip("ABCDEFGH", ("up", "down", "right", "left", "5", "end", "5", "home"))
    ),
    *(
        # modified F1-F4 keys -- O#X form
        (f"O{digit}{letter}", escape_modifier(digit) + key)
        for digit in "12345678"
        for letter, key in zip("PQRS", ("f1", "f2", "f3", "f4"))
    ),
    *(
        # modified F1-F13 keys -- [XX;#~ form
        (f"[{num!s};{digit}~", escape_modifier(digit) + key)
        for digit in "12345678"
        for num, key in zip(
            (3, 5, 6, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 31, 32, 33, 34),
            (
                "delete",
                "page up",
                "page down",
                *(f"{idx}" for idx in range(1, 20)),
            ),
        )
    ),
    # mouse reporting (special handling done in KeyqueueTrie)
    ("[M", "mouse"),
    # mouse reporting for SGR 1006
    ("[<", "sgrmouse"),
    # report status response
    ("[0n", "status ok"),
]


class KeyqueueTrie:
    def __init__(self, sequences) -> None:
        self.data = {}
        for s, result in sequences:
            if isinstance(result, dict):
                raise TypeError(result)
            self.add(self.data, s, result)

    def add(self, root, s, result):
        if not isinstance(root, MutableMapping) or len(s) <= 0:
            raise RuntimeError("trie conflict detected")

        if ord(s[0]) in root:
            return self.add(root[ord(s[0])], s[1:], result)
        if len(s) > 1:
            d = {}
            root[ord(s[0])] = d
            return self.add(d, s[1:], result)
        root[ord(s)] = result
        return None

    def get(self, keys, more_available: bool):
        result = self.get_recurse(self.data, keys, more_available)
        if not result:
            result = self.read_cursor_position(keys, more_available)
        return result

    def get_recurse(self, root, keys, more_available: bool):
        if not isinstance(root, MutableMapping):
            if root == "mouse":
                return self.read_mouse_info(keys, more_available)

            if root == "sgrmouse":
                return self.read_sgrmouse_info(keys, more_available)

            return (root, keys)
        if not keys:
            # get more keys
            if more_available:
                raise MoreInputRequired()
            return None
        if keys[0] not in root:
            return None
        return self.get_recurse(root[keys[0]], keys[1:], more_available)

    def read_mouse_info(self, keys, more_available: bool):
        if len(keys) < 3:
            if more_available:
                raise MoreInputRequired()
            return None

        b = keys[0] - 32
        x, y = (keys[1] - 33) % 256, (keys[2] - 33) % 256  # supports 0-255

        prefix = ""
        if b & 4:
            prefix = f"{prefix}shift "
        if b & 8:
            prefix = f"{prefix}meta "
        if b & 16:
            prefix = f"{prefix}ctrl "
        if (b & MOUSE_MULTIPLE_CLICK_MASK) >> 9 == 1:
            prefix = f"{prefix}double "
        if (b & MOUSE_MULTIPLE_CLICK_MASK) >> 9 == 2:
            prefix = f"{prefix}triple "

        # 0->1, 1->2, 2->3, 64->4, 65->5
        button = ((b & 64) // 64 * 3) + (b & 3) + 1

        if b & 3 == 3:
            action = "release"
            button = 0
        elif b & MOUSE_RELEASE_FLAG:
            action = "release"
        elif b & MOUSE_DRAG_FLAG:
            action = "drag"
        elif b & MOUSE_MULTIPLE_CLICK_MASK:
            action = "click"
        else:
            action = "press"

        return ((f"{prefix}mouse {action}", button, x, y), keys[3:])

    def read_sgrmouse_info(self, keys, more_available: bool):
        # Helpful links:
        # https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
        # http://invisible-island.net/xterm/ctlseqs/ctlseqs.pdf

        if not keys:
            if more_available:
                raise MoreInputRequired()
            return None

        value = ""
        pos_m = 0
        found_m = False
        for k in keys:
            value = value + chr(k)
            if k in (ord("M"), ord("m")):
                found_m = True
                break
            pos_m += 1
        if not found_m:
            if more_available:
                raise MoreInputRequired()
            return None

        (b, x, y) = value[:-1].split(";")

        # shift, meta, ctrl etc. is not communicated on my machine, so I
        # can't and won't be able to add support for it.
        # Double and triple clicks are not supported as well. They can be
        # implemented by using a timer. This timer can check if the last
        # registered click is below a certain threshold. This threshold
        # is normally set in the operating system itself, so setting one
        # here will cause an inconsistent behaviour. I do not plan to use
        # that feature, so I won't implement it.

        button = ((int(b) & 64) // 64 * 3) + (int(b) & 3) + 1
        x = int(x) - 1
        y = int(y) - 1

        if value[-1] == "M":
            if int(b) & MOUSE_DRAG_FLAG:
                action = "drag"
            else:
                action = "press"
        else:
            action = "release"

        return ((f"mouse {action}", button, x, y), keys[pos_m + 1 :])

    def read_cursor_position(self, keys, more_available: bool):
        """
        Interpret cursor position information being sent by the
        user's terminal.  Returned as ('cursor position', x, y)
        where (x, y) == (0, 0) is the top left of the screen.
        """
        if not keys:
            if more_available:
                raise MoreInputRequired()
            return None
        if keys[0] != ord("["):
            return None
        # read y value
        y = 0
        i = 1
        for k in keys[i:]:
            i += 1
            if k == ord(";"):
                if not y:
                    return None
                break
            if k < ord("0") or k > ord("9"):
                return None
            if not y and k == ord("0"):
                return None
            y = y * 10 + k - ord("0")
        if not keys[i:]:
            if more_available:
                raise MoreInputRequired()
            return None
        # read x value
        x = 0
        for k in keys[i:]:
            i += 1
            if k == ord("R"):
                if not x:
                    return None
                return (("cursor position", x - 1, y - 1), keys[i:])
            if k < ord("0") or k > ord("9"):
                return None
            if not x and k == ord("0"):
                return None
            x = x * 10 + k - ord("0")
        if not keys[i:] and more_available:
            raise MoreInputRequired()
        return None


# This is added to button value to signal mouse release by curses_display
# and raw_display when we know which button was released.  NON-STANDARD
MOUSE_RELEASE_FLAG = 2048

# This 2-bit mask is used to check if the mouse release from curses or gpm
# is a double or triple release. 00 means single click, 01 double,
# 10 triple. NON-STANDARD
MOUSE_MULTIPLE_CLICK_MASK = 1536

# This is added to button value at mouse release to differentiate between
# single, double and triple press. Double release adds this times one,
# triple release adds this times two.  NON-STANDARD
MOUSE_MULTIPLE_CLICK_FLAG = 512

# xterm adds this to the button value to signal a mouse drag event
MOUSE_DRAG_FLAG = 32


#################################################
# Build the input trie from input_sequences list
input_trie = KeyqueueTrie(input_sequences)
#################################################

_keyconv = {
    -1: None,
    8: "backspace",
    9: "tab",
    10: "enter",
    13: "enter",
    127: "backspace",
    # curses-only keycodes follow..  (XXX: are these used anymore?)
    258: "down",
    259: "up",
    260: "left",
    261: "right",
    262: "home",
    263: "backspace",
    265: "f1",
    266: "f2",
    267: "f3",
    268: "f4",
    269: "f5",
    270: "f6",
    271: "f7",
    272: "f8",
    273: "f9",
    274: "f10",
    275: "f11",
    276: "f12",
    277: "shift f1",
    278: "shift f2",
    279: "shift f3",
    280: "shift f4",
    281: "shift f5",
    282: "shift f6",
    283: "shift f7",
    284: "shift f8",
    285: "shift f9",
    286: "shift f10",
    287: "shift f11",
    288: "shift f12",
    330: "delete",
    331: "insert",
    338: "page down",
    339: "page up",
    343: "enter",  # on numpad
    350: "5",  # on numpad
    360: "end",
}


def process_keyqueue(codes: Sequence[int], more_available: bool) -> tuple[list[str], Sequence[int]]:
    """
    codes -- list of key codes
    more_available -- if True then raise MoreInputRequired when in the
        middle of a character sequence (escape/utf8/wide) and caller
        will attempt to send more key codes on the next call.

    returns (list of input, list of remaining key codes).
    """
    code = codes[0]
    if 32 <= code <= 126:
        key = chr(code)
        return [key], codes[1:]
    if code in _keyconv:
        return [_keyconv[code]], codes[1:]
    if 0 < code < 27:
        return [f"ctrl {ord('a') + code - 1:c}"], codes[1:]
    if 27 < code < 32:
        return [f"ctrl {ord('A') + code - 1:c}"], codes[1:]

    em = str_util.get_byte_encoding()

    if em == "wide" and code < 256 and within_double_byte(code.to_bytes(1, "little"), 0, 0):
        if not codes[1:] and more_available:
            raise MoreInputRequired()
        if codes[1:] and codes[1] < 256:
            db = chr(code) + chr(codes[1])
            if within_double_byte(db, 0, 1):
                return [db], codes[2:]
    if em == "utf8" and 127 < code < 256:
        if code & 0xE0 == 0xC0:  # 2-byte form
            need_more = 1
        elif code & 0xF0 == 0xE0:  # 3-byte form
            need_more = 2
        elif code & 0xF8 == 0xF0:  # 4-byte form
            need_more = 3
        else:
            return [f"<{code:d}>"], codes[1:]

        for i in range(need_more):
            if len(codes) - 1 <= i:
                if more_available:
                    raise MoreInputRequired()

                return [f"<{code:d}>"], codes[1:]

            k = codes[i + 1]
            if k > 256 or k & 0xC0 != 0x80:
                return [f"<{code:d}>"], codes[1:]

        s = bytes(codes[: need_more + 1])

        try:
            return [s.decode("utf-8")], codes[need_more + 1 :]
        except UnicodeDecodeError:
            return [f"<{code:d}>"], codes[1:]

    if 127 < code < 256:
        key = chr(code)
        return [key], codes[1:]
    if code != 27:
        return [f"<{code:d}>"], codes[1:]

    result = input_trie.get(codes[1:], more_available)

    if result is not None:
        result, remaining_codes = result
        return [result], remaining_codes

    if codes[1:]:
        # Meta keys -- ESC+Key form
        run, remaining_codes = process_keyqueue(codes[1:], more_available)
        if urwid.util.is_mouse_event(run[0]):
            return ["esc", *run], remaining_codes
        if run[0] == "esc" or run[0].find("meta ") >= 0:
            return ["esc", *run], remaining_codes
        return [f"meta {run[0]}"] + run[1:], remaining_codes

    return ["esc"], codes[1:]


####################
## Output sequences
####################

ESC = "\x1b"

CURSOR_HOME = f"{ESC}[H"
CURSOR_HOME_COL = "\r"

APP_KEYPAD_MODE = f"{ESC}="
NUM_KEYPAD_MODE = f"{ESC}>"

SWITCH_TO_ALTERNATE_BUFFER = f"{ESC}[?1049h"
RESTORE_NORMAL_BUFFER = f"{ESC}[?1049l"

ENABLE_BRACKETED_PASTE_MODE = f"{ESC}[?2004h"
DISABLE_BRACKETED_PASTE_MODE = f"{ESC}[?2004l"

# RESET_SCROLL_REGION = ESC+"[;r"
# RESET = ESC+"c"

REPORT_STATUS = f"{ESC}[5n"
REPORT_CURSOR_POSITION = f"{ESC}[6n"

INSERT_ON = f"{ESC}[4h"
INSERT_OFF = f"{ESC}[4l"


def set_cursor_position(x: int, y: int) -> str:
    if not isinstance(x, int):
        raise TypeError(x)
    if not isinstance(y, int):
        raise TypeError(y)

    return ESC + f"[{y + 1:d};{x + 1:d}H"


def move_cursor_right(x: int) -> str:
    if x < 1:
        return ""
    return ESC + f"[{x:d}C"


def move_cursor_up(x: int) -> str:
    if x < 1:
        return ""
    return ESC + f"[{x:d}A"


def move_cursor_down(x: int) -> str:
    if x < 1:
        return ""
    return ESC + f"[{x:d}B"


HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"

MOUSE_TRACKING_ON = f"{ESC}[?1000h{ESC}[?1002h{ESC}[?1006h"
MOUSE_TRACKING_OFF = f"{ESC}[?1006l{ESC}[?1002l{ESC}[?1000l"

DESIGNATE_G1_SPECIAL = f"{ESC})0"

ERASE_IN_LINE_RIGHT = f"{ESC}[K"
