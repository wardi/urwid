# Urwid utility functions
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

import codecs
import contextlib
import typing
import warnings
from contextlib import suppress

from urwid import escape

if typing.TYPE_CHECKING:
    from typing_extensions import Self

str_util = escape.str_util

# bring str_util functions into our namespace
calc_text_pos = str_util.calc_text_pos
calc_width = str_util.calc_width
is_wide_char = str_util.is_wide_char
move_next_char = str_util.move_next_char
move_prev_char = str_util.move_prev_char
within_double_byte = str_util.within_double_byte


def detect_encoding() -> str:
    # Try to determine if using a supported double-byte encoding
    import locale

    no_set_locale = locale.getpreferredencoding(False)

    if no_set_locale != "ascii":
        # ascii is fallback locale in case of detect failed

        return no_set_locale

    # Use actual `getpreferredencoding` with public API only
    old_loc = locale.setlocale(locale.LC_CTYPE)  # == getlocale, but not mangle data
    try:
        with suppress(locale.Error):
            locale.setlocale(locale.LC_CTYPE, "")
        # internally call private `_get_locale_encoding`
        return locale.getpreferredencoding(False)
    finally:
        with suppress(locale.Error):
            locale.setlocale(locale.LC_CTYPE, old_loc)


if "detected_encoding" not in locals():
    detected_encoding = detect_encoding()
else:
    raise RuntimeError("Encoding detection broken")

_target_encoding = "ascii"
_use_dec_special = True


def set_encoding(encoding):
    """
    Set the byte encoding to assume when processing strings and the
    encoding to use when converting unicode strings.
    """
    encoding = encoding.lower()

    global _target_encoding, _use_dec_special  # noqa: PLW0603

    if encoding in ("utf-8", "utf8", "utf"):
        str_util.set_byte_encoding("utf8")

        _use_dec_special = False
    elif encoding in (
        "euc-jp",  # JISX 0208 only
        "euc-kr",
        "euc-cn",
        "euc-tw",  # CNS 11643 plain 1 only
        "gb2312",
        "gbk",
        "big5",
        "cn-gb",
        "uhc"
        # these shouldn't happen, should they?
        ,
        "eucjp",
        "euckr",
        "euccn",
        "euctw",
        "cncb",
    ):
        str_util.set_byte_encoding("wide")

        _use_dec_special = True
    else:
        str_util.set_byte_encoding("narrow")
        _use_dec_special = True

    # if encoding is valid for conversion from unicode, remember it
    _target_encoding = "ascii"
    with contextlib.suppress(LookupError):
        if encoding:
            "".encode(encoding)
            _target_encoding = encoding


def get_encoding_mode():
    """
    Get the mode Urwid is using when processing text strings.
    Returns 'narrow' for 8-bit encodings, 'wide' for CJK encodings
    or 'utf8' for UTF-8 encodings.
    """
    return str_util.get_byte_encoding()


def apply_target_encoding(s: str | bytes):
    """
    Return (encoded byte string, character set rle).
    """
    if _use_dec_special and isinstance(s, str):
        # first convert drawing characters
        s = s.translate(escape.DEC_SPECIAL_CHARMAP)

    if isinstance(s, str):
        s = s.replace(escape.SI + escape.SO, "")  # remove redundant shifts
        s = codecs.encode(s, _target_encoding, "replace")

    if not isinstance(s, bytes):
        raise TypeError(s)
    SO = escape.SO.encode("ascii")
    SI = escape.SI.encode("ascii")

    sis = s.split(SO)

    if not isinstance(sis[0], bytes):
        raise TypeError(sis[0])

    sis0 = sis[0].replace(SI, b"")
    sout = []
    cout = []
    if sis0:
        sout.append(sis0)
        cout.append((None, len(sis0)))

    if len(sis) == 1:
        return sis0, cout

    for sn in sis[1:]:
        if not isinstance(sn, bytes):
            raise TypeError(sn)
        if not isinstance(SI, bytes):
            raise TypeError(SI)

        sl = sn.split(SI, 1)
        if len(sl) == 1:
            sin = sl[0]
            if not isinstance(sin, bytes):
                raise TypeError(sin)
            sout.append(sin)
            rle_append_modify(cout, (escape.DEC_TAG, len(sin)))
            continue
        sin, son = sl
        son = son.replace(SI, b"")
        if sin:
            sout.append(sin)
            rle_append_modify(cout, (escape.DEC_TAG, len(sin)))
        if son:
            sout.append(son)
            rle_append_modify(cout, (None, len(son)))

    outstr = b"".join(sout)
    return outstr, cout


######################################################################
# Try to set the encoding using the one detected by the locale module
set_encoding(detected_encoding)
######################################################################


def supports_unicode():
    """
    Return True if python is able to convert non-ascii unicode strings
    to the current encoding.
    """
    return _target_encoding and _target_encoding != "ascii"


def calc_trim_text(text, start_offs: int, end_offs: int, start_col: int, end_col: int):
    """
    Calculate the result of trimming text.
    start_offs -- offset into text to treat as screen column 0
    end_offs -- offset into text to treat as the end of the line
    start_col -- screen column to trim at the left
    end_col -- screen column to trim at the right

    Returns (start, end, pad_left, pad_right), where:
    start -- resulting start offset
    end -- resulting end offset
    pad_left -- 0 for no pad or 1 for one space to be added
    pad_right -- 0 for no pad or 1 for one space to be added
    """
    spos = start_offs
    pad_left = pad_right = 0
    if start_col > 0:
        spos, sc = calc_text_pos(text, spos, end_offs, start_col)
        if sc < start_col:
            pad_left = 1
            spos, sc = calc_text_pos(text, start_offs, end_offs, start_col + 1)
    run = end_col - start_col - pad_left
    pos, sc = calc_text_pos(text, spos, end_offs, run)
    if sc < run:
        pad_right = 1
    return (spos, pos, pad_left, pad_right)


def trim_text_attr_cs(text, attr, cs, start_col: int, end_col: int):
    """
    Return ( trimmed text, trimmed attr, trimmed cs ).
    """
    spos, epos, pad_left, pad_right = calc_trim_text(text, 0, len(text), start_col, end_col)
    attrtr = rle_subseg(attr, spos, epos)
    cstr = rle_subseg(cs, spos, epos)
    if pad_left:
        al = rle_get_at(attr, spos - 1)
        rle_prepend_modify(attrtr, (al, 1))
        rle_prepend_modify(cstr, (None, 1))
    if pad_right:
        al = rle_get_at(attr, epos)
        rle_append_modify(attrtr, (al, 1))
        rle_append_modify(cstr, (None, 1))

    return (b"".rjust(pad_left) + text[spos:epos] + b"".rjust(pad_right), attrtr, cstr)


def rle_get_at(rle, pos: int):
    """
    Return the attribute at offset pos.
    """
    x = 0
    if pos < 0:
        return None
    for a, run in rle:
        if x + run > pos:
            return a
        x += run
    return None


def rle_subseg(rle, start: int, end: int):
    """Return a sub segment of a rle list."""
    sub_segment = []
    x = 0
    for a, run in rle:
        if start:
            if start >= run:
                start -= run
                x += run
                continue
            x += start
            run -= start  # noqa: PLW2901
            start = 0
        if x >= end:
            break
        if x + run > end:
            run = end - x  # noqa: PLW2901
        x += run
        sub_segment.append((a, run))
    return sub_segment


def rle_len(rle) -> int:
    """
    Return the number of characters covered by a run length
    encoded attribute list.
    """

    run = 0
    for v in rle:
        if not isinstance(v, tuple):
            raise TypeError(rle)
        a, r = v
        run += r
    return run


def rle_prepend_modify(rle, a_r) -> None:
    """
    Append (a, r) (unpacked from *a_r*) to BEGINNING of rle.
    Merge with first run when possible

    MODIFIES rle parameter contents. Returns None.
    """
    a, r = a_r
    if not rle:
        rle[:] = [(a, r)]
    else:
        al, run = rle[0]
        if a == al:
            rle[0] = (a, run + r)
        else:
            rle[0:0] = [(a, r)]


def rle_append_modify(rle, a_r):
    """
    Append (a, r) (unpacked from *a_r*) to the rle list rle.
    Merge with last run when possible.

    MODIFIES rle parameter contents. Returns None.
    """
    a, r = a_r
    if not rle or rle[-1][0] != a:
        rle.append((a, r))
        return
    la, lr = rle[-1]
    rle[-1] = (a, lr + r)


def rle_join_modify(rle, rle2):
    """
    Append attribute list rle2 to rle.
    Merge last run of rle with first run of rle2 when possible.

    MODIFIES attr parameter contents. Returns None.
    """
    if not rle2:
        return
    rle_append_modify(rle, rle2[0])
    rle += rle2[1:]


def rle_product(rle1, rle2):
    """
    Merge the runs of rle1 and rle2 like this:
    eg.
    rle1 = [ ("a", 10), ("b", 5) ]
    rle2 = [ ("Q", 5), ("P", 10) ]
    rle_product: [ (("a","Q"), 5), (("a","P"), 5), (("b","P"), 5) ]

    rle1 and rle2 are assumed to cover the same total run.
    """
    i1 = i2 = 1  # rle1, rle2 indexes
    if not rle1 or not rle2:
        return []
    a1, r1 = rle1[0]
    a2, r2 = rle2[0]

    result = []
    while r1 and r2:
        r = min(r1, r2)
        rle_append_modify(result, ((a1, a2), r))
        r1 -= r
        if r1 == 0 and i1 < len(rle1):
            a1, r1 = rle1[i1]
            i1 += 1
        r2 -= r
        if r2 == 0 and i2 < len(rle2):
            a2, r2 = rle2[i2]
            i2 += 1
    return result


def rle_factor(rle):
    """
    Inverse of rle_product.
    """
    rle1 = []
    rle2 = []
    for (a1, a2), r in rle:
        rle_append_modify(rle1, (a1, r))
        rle_append_modify(rle2, (a2, r))
    return rle1, rle2


class TagMarkupException(Exception):
    pass


def decompose_tagmarkup(tm):
    """Return (text string, attribute list) for tagmarkup passed."""

    tl, al = _tagmarkup_recurse(tm, None)
    # join as unicode or bytes based on type of first element
    if tl:
        text = tl[0][:0].join(tl)
    else:
        text = ""

    if al and al[-1][0] is None:
        del al[-1]

    return text, al


def _tagmarkup_recurse(tm, attr):
    """Return (text list, attribute list) for tagmarkup passed.

    tm -- tagmarkup
    attr -- current attribute or None"""

    if isinstance(tm, list):
        # for lists recurse to process each subelement
        rtl = []
        ral = []
        for element in tm:
            tl, al = _tagmarkup_recurse(element, attr)
            if ral:
                # merge attributes when possible
                last_attr, last_run = ral[-1]
                top_attr, top_run = al[0]
                if last_attr == top_attr:
                    ral[-1] = (top_attr, last_run + top_run)
                    del al[0]
            rtl += tl
            ral += al
        return rtl, ral

    if isinstance(tm, tuple):
        # tuples mark a new attribute boundary
        if len(tm) != 2:
            raise TagMarkupException(f"Tuples must be in the form (attribute, tagmarkup): {tm!r}")

        attr, element = tm
        return _tagmarkup_recurse(element, attr)

    if not isinstance(tm, (str, bytes)):
        raise TagMarkupException(f"Invalid markup element: {tm!r}")

    # text
    return [tm], [(attr, len(tm))]


def is_mouse_event(ev: tuple[str, int, int, int] | typing.Any) -> bool:
    return isinstance(ev, tuple) and len(ev) == 4 and "mouse" in ev[0]


def is_mouse_press(ev: str) -> bool:
    return "press" in ev


class MetaSuper(type):
    """adding .__super"""

    def __init__(cls, name: str, bases, d):
        super().__init__(name, bases, d)
        if hasattr(cls, f"_{name}__super"):
            raise AttributeError("Class has same name as one of its super classes")

        @property
        def _super(self):
            warnings.warn(
                f"`{name}.__super` was a deprecated feature for old python versions."
                f"Please use `super()` call instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            return super(cls, self)

        setattr(cls, f"_{name}__super", _super)


def int_scale(val: int, val_range: int, out_range: int):
    """
    Scale val in the range [0, val_range-1] to an integer in the range
    [0, out_range-1].  This implementation uses the "round-half-up" rounding
    method.

    >>> "%x" % int_scale(0x7, 0x10, 0x10000)
    '7777'
    >>> "%x" % int_scale(0x5f, 0x100, 0x10)
    '6'
    >>> int_scale(2, 6, 101)
    40
    >>> int_scale(1, 3, 4)
    2
    """
    num = int(val * (out_range - 1) * 2 + (val_range - 1))
    dem = (val_range - 1) * 2
    # if num % dem == 0 then we are exactly half-way and have rounded up.
    return num // dem


class StoppingContext:
    """Context manager that calls ``stop`` on a given object on exit.  Used to
    make the ``start`` method on `MainLoop` and `BaseScreen` optionally act as
    context managers.
    """

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info):
        self._wrapped.stop()
