# Urwid MonitoredList class
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

import functools
import typing
import warnings

if typing.TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import ParamSpec

    ArgSpec = ParamSpec("ArgSpec")
    Ret = typing.TypeVar("Ret")


def _call_modified(fn: Callable[ArgSpec, Ret]) -> Callable[ArgSpec, Ret]:
    @functools.wraps(fn)
    def call_modified_wrapper(self: MonitoredList, *args, **kwargs):
        rval = fn(self, *args, **kwargs)
        self._modified()
        return rval

    return call_modified_wrapper


class MonitoredList(list):
    """
    This class can trigger a callback any time its contents are changed
    with the usual list operations append, extend, etc.
    """

    def _modified(self):
        pass

    def set_modified_callback(self, callback):
        """
        Assign a callback function with no parameters that is called any
        time the list is modified.  Callback's return value is ignored.

        >>> import sys
        >>> ml = MonitoredList([1,2,3])
        >>> ml.set_modified_callback(lambda: sys.stdout.write("modified\\n"))
        >>> ml
        MonitoredList([1, 2, 3])
        >>> ml.append(10)
        modified
        >>> len(ml)
        4
        >>> ml += [11, 12, 13]
        modified
        >>> ml[:] = ml[:2] + ml[-2:]
        modified
        >>> ml
        MonitoredList([1, 2, 12, 13])
        """
        self._modified = callback

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self)!r})"

    __add__ = _call_modified(list.__add__)
    __delitem__ = _call_modified(list.__delitem__)

    __iadd__ = _call_modified(list.__iadd__)
    __imul__ = _call_modified(list.__imul__)
    __rmul__ = _call_modified(list.__rmul__)
    __setitem__ = _call_modified(list.__setitem__)

    append = _call_modified(list.append)
    extend = _call_modified(list.extend)
    insert = _call_modified(list.insert)
    pop = _call_modified(list.pop)
    remove = _call_modified(list.remove)
    reverse = _call_modified(list.reverse)
    sort = _call_modified(list.sort)
    if hasattr(list, "clear"):
        clear = _call_modified(list.clear)


class MonitoredFocusList(MonitoredList):
    """
    This class can trigger a callback any time its contents are modified,
    before and/or after modification, and any time the focus index is changed.
    """

    def __init__(self, *argl, **argd):
        """
        This is a list that tracks one item as the focus item.  If items
        are inserted or removed it will update the focus.

        >>> ml = MonitoredFocusList([10, 11, 12, 13, 14], focus=3)
        >>> ml
        MonitoredFocusList([10, 11, 12, 13, 14], focus=3)
        >>> del(ml[1])
        >>> ml
        MonitoredFocusList([10, 12, 13, 14], focus=2)
        >>> ml[:2] = [50, 51, 52, 53]
        >>> ml
        MonitoredFocusList([50, 51, 52, 53, 13, 14], focus=4)
        >>> ml[4] = 99
        >>> ml
        MonitoredFocusList([50, 51, 52, 53, 99, 14], focus=4)
        >>> ml[:] = []
        >>> ml
        MonitoredFocusList([], focus=None)
        """
        focus = argd.pop("focus", 0)

        super().__init__(*argl, **argd)

        self._focus = focus
        self._focus_modified = lambda ml, indices, new_items: None

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self)!r}, focus={self.focus!r})"

    @property
    def focus(self) -> int | None:
        """
        Get/set the focus index.  This value is read as None when the list
        is empty, and may only be set to a value between 0 and len(self)-1
        or an IndexError will be raised.

        Return the index of the item "in focus" or None if
        the list is empty.

        >>> MonitoredFocusList([1,2,3], focus=2).focus
        2
        >>> MonitoredFocusList().focus
        """
        if not self:
            return None
        return self._focus

    @focus.setter
    def focus(self, index: int) -> None:
        """
        index -- index into this list, any index out of range will
            raise an IndexError, except when the list is empty and
            the index passed is ignored.

        This function may call self._focus_changed when the focus
        is modified, passing the new focus position to the
        callback just before changing the old focus setting.
        That method may be overridden on the
        instance with set_focus_changed_callback().

        >>> ml = MonitoredFocusList([9, 10, 11])
        >>> ml.focus = 2; ml.focus
        2
        >>> ml.focus = 0; ml.focus
        0
        >>> ml.focus = -2
        Traceback (most recent call last):
        ...
        IndexError: focus index is out of range: -2
        """
        if not self:
            self._focus = 0
            return
        if index < 0 or index >= len(self):
            raise IndexError(f"focus index is out of range: {index}")
        if index != int(index):
            raise IndexError(f"invalid focus index: {index}")
        index = int(index)
        if index != self._focus:
            self._focus_changed(index)
        self._focus = index

    def _get_focus(self) -> int | None:
        warnings.warn(
            f"method `{self.__class__.__name__}._get_focus` is deprecated, "
            f"please use `{self.__class__.__name__}.focus` property",
            DeprecationWarning,
            stacklevel=3,
        )
        return self.focus

    def _set_focus(self, index: int) -> None:
        warnings.warn(
            f"method `{self.__class__.__name__}._set_focus` is deprecated, "
            f"please use `{self.__class__.__name__}.focus` property",
            DeprecationWarning,
            stacklevel=3,
        )
        self.focus = index

    def _focus_changed(self, new_focus: int):
        pass

    def set_focus_changed_callback(self, callback: Callable[[int], typing.Any]) -> None:
        """
        Assign a callback to be called when the focus index changes
        for any reason.  The callback is in the form:

        callback(new_focus)
        new_focus -- new focus index

        >>> import sys
        >>> ml = MonitoredFocusList([1,2,3], focus=1)
        >>> ml.set_focus_changed_callback(lambda f: sys.stdout.write("focus: %d\\n" % (f,)))
        >>> ml
        MonitoredFocusList([1, 2, 3], focus=1)
        >>> ml.append(10)
        >>> ml.insert(1, 11)
        focus: 2
        >>> ml
        MonitoredFocusList([1, 11, 2, 3, 10], focus=2)
        >>> del ml[:2]
        focus: 0
        >>> ml[:0] = [12, 13, 14]
        focus: 3
        >>> ml.focus = 5
        focus: 5
        >>> ml
        MonitoredFocusList([12, 13, 14, 2, 3, 10], focus=5)
        """
        self._focus_changed = callback

    def _validate_contents_modified(self, indices, new_items):
        return None

    def set_validate_contents_modified(self, callback):
        """
        Assign a callback function to handle validating changes to the list.
        This may raise an exception if the change should not be performed.
        It may also return an integer position to be the new focus after the
        list is modified, or None to use the default behaviour.

        The callback is in the form:

        callback(indices, new_items)
        indices -- a (start, stop, step) tuple whose range covers the
            items being modified
        new_items -- an iterable of items replacing those at range(*indices),
            empty if items are being removed, if step==1 this list may
            contain any number of items
        """
        self._validate_contents_modified = callback

    def _adjust_focus_on_contents_modified(self, slc: slice, new_items=()) -> int:
        """
        Default behaviour is to move the focus to the item following
        any removed items, unless that item was simply replaced.

        Failing that choose the last item in the list.

        returns focus position for after change is applied
        """
        num_new_items = len(new_items)
        start, stop, step = indices = slc.indices(len(self))
        num_removed = len(list(range(*indices)))

        focus = self._validate_contents_modified(indices, new_items)
        if focus is not None:
            return focus

        focus = self._focus
        if step == 1:
            if start + num_new_items <= focus < stop:
                focus = stop
            # adjust for added/removed items
            if stop <= focus:
                focus += num_new_items - (stop - start)

        else:  # noqa: PLR5501
            if not num_new_items:
                # extended slice being removed
                if focus in range(start, stop, step):
                    focus += 1

                # adjust for removed items
                focus -= len(list(range(start, min(focus, stop), step)))

        return min(focus, len(self) + num_new_items - num_removed - 1)

    # override all the list methods that modify the list

    def __delitem__(self, y: int | slice):
        """
        >>> ml = MonitoredFocusList([0,1,2,3,4], focus=2)
        >>> del ml[3]; ml
        MonitoredFocusList([0, 1, 2, 4], focus=2)
        >>> del ml[-1]; ml
        MonitoredFocusList([0, 1, 2], focus=2)
        >>> del ml[0]; ml
        MonitoredFocusList([1, 2], focus=1)
        >>> del ml[1]; ml
        MonitoredFocusList([1], focus=0)
        >>> del ml[0]; ml
        MonitoredFocusList([], focus=None)
        >>> ml = MonitoredFocusList([5,4,6,4,5,4,6,4,5], focus=4)
        >>> del ml[1::2]; ml
        MonitoredFocusList([5, 6, 5, 6, 5], focus=2)
        >>> del ml[::2]; ml
        MonitoredFocusList([6, 6], focus=1)
        >>> ml = MonitoredFocusList([0,1,2,3,4,6,7], focus=2)
        >>> del ml[-2:]; ml
        MonitoredFocusList([0, 1, 2, 3, 4], focus=2)
        >>> del ml[-4:-2]; ml
        MonitoredFocusList([0, 3, 4], focus=1)
        >>> del ml[:]; ml
        MonitoredFocusList([], focus=None)
        """
        if isinstance(y, slice):
            focus = self._adjust_focus_on_contents_modified(y)
        else:
            focus = self._adjust_focus_on_contents_modified(slice(y, y + 1 or None))
        rval = super().__delitem__(y)
        self.focus = focus
        return rval

    def __setitem__(self, i: int | slice, y):
        """
        >>> def modified(indices, new_items):
        ...     print("range%r <- %r" % (indices, new_items))
        >>> ml = MonitoredFocusList([0,1,2,3], focus=2)
        >>> ml.set_validate_contents_modified(modified)
        >>> ml[0] = 9
        range(0, 1, 1) <- [9]
        >>> ml[2] = 6
        range(2, 3, 1) <- [6]
        >>> ml.focus
        2
        >>> ml[-1] = 8
        range(3, 4, 1) <- [8]
        >>> ml
        MonitoredFocusList([9, 1, 6, 8], focus=2)
        >>> ml[1::2] = [12, 13]
        range(1, 4, 2) <- [12, 13]
        >>> ml[::2] = [10, 11]
        range(0, 4, 2) <- [10, 11]
        >>> ml[-3:-1] = [21, 22, 23]
        range(1, 3, 1) <- [21, 22, 23]
        >>> ml
        MonitoredFocusList([10, 21, 22, 23, 13], focus=2)
        >>> ml[:] = []
        range(0, 5, 1) <- []
        >>> ml
        MonitoredFocusList([], focus=None)
        """
        if isinstance(i, slice):
            focus = self._adjust_focus_on_contents_modified(i, y)
        else:
            focus = self._adjust_focus_on_contents_modified(slice(i, i + 1 or None), [y])
        rval = super().__setitem__(i, y)
        self.focus = focus
        return rval

    def __imul__(self, n: int):
        """
        >>> def modified(indices, new_items):
        ...     print("range%r <- %r" % (indices, list(new_items)))
        >>> ml = MonitoredFocusList([0,1,2], focus=2)
        >>> ml.set_validate_contents_modified(modified)
        >>> ml *= 3
        range(3, 3, 1) <- [0, 1, 2, 0, 1, 2]
        >>> ml
        MonitoredFocusList([0, 1, 2, 0, 1, 2, 0, 1, 2], focus=2)
        >>> ml *= 0
        range(0, 9, 1) <- []
        >>> print(ml.focus)
        None
        """
        if n > 0:
            focus = self._adjust_focus_on_contents_modified(slice(len(self), len(self)), list(self) * (n - 1))
        else:  # all contents are being removed
            focus = self._adjust_focus_on_contents_modified(slice(0, len(self)))
        rval = super().__imul__(n)
        self.focus = focus
        return rval

    def append(self, item):
        """
        >>> def modified(indices, new_items):
        ...     print("range%r <- %r" % (indices, new_items))
        >>> ml = MonitoredFocusList([0,1,2], focus=2)
        >>> ml.set_validate_contents_modified(modified)
        >>> ml.append(6)
        range(3, 3, 1) <- [6]
        """
        focus = self._adjust_focus_on_contents_modified(slice(len(self), len(self)), [item])
        rval = super().append(item)
        self.focus = focus
        return rval

    def extend(self, items):
        """
        >>> def modified(indices, new_items):
        ...     print("range%r <- %r" % (indices, list(new_items)))
        >>> ml = MonitoredFocusList([0,1,2], focus=2)
        >>> ml.set_validate_contents_modified(modified)
        >>> ml.extend((6,7,8))
        range(3, 3, 1) <- [6, 7, 8]
        """
        focus = self._adjust_focus_on_contents_modified(slice(len(self), len(self)), items)
        rval = super().extend(items)
        self.focus = focus
        return rval

    def insert(self, index: int, item):
        """
        >>> ml = MonitoredFocusList([0,1,2,3], focus=2)
        >>> ml.insert(-1, -1); ml
        MonitoredFocusList([0, 1, 2, -1, 3], focus=2)
        >>> ml.insert(0, -2); ml
        MonitoredFocusList([-2, 0, 1, 2, -1, 3], focus=3)
        >>> ml.insert(3, -3); ml
        MonitoredFocusList([-2, 0, 1, -3, 2, -1, 3], focus=4)
        """
        focus = self._adjust_focus_on_contents_modified(slice(index, index), [item])
        rval = super().insert(index, item)
        self.focus = focus
        return rval

    def pop(self, index: int = -1):
        """
        >>> ml = MonitoredFocusList([-2,0,1,-3,2,3], focus=4)
        >>> ml.pop(3); ml
        -3
        MonitoredFocusList([-2, 0, 1, 2, 3], focus=3)
        >>> ml.pop(0); ml
        -2
        MonitoredFocusList([0, 1, 2, 3], focus=2)
        >>> ml.pop(-1); ml
        3
        MonitoredFocusList([0, 1, 2], focus=2)
        >>> ml.pop(2); ml
        2
        MonitoredFocusList([0, 1], focus=1)
        """
        focus = self._adjust_focus_on_contents_modified(slice(index, index + 1 or None))
        rval = super().pop(index)
        self.focus = focus
        return rval

    def remove(self, value):
        """
        >>> ml = MonitoredFocusList([-2,0,1,-3,2,-1,3], focus=4)
        >>> ml.remove(-3); ml
        MonitoredFocusList([-2, 0, 1, 2, -1, 3], focus=3)
        >>> ml.remove(-2); ml
        MonitoredFocusList([0, 1, 2, -1, 3], focus=2)
        >>> ml.remove(3); ml
        MonitoredFocusList([0, 1, 2, -1], focus=2)
        """
        index = self.index(value)
        focus = self._adjust_focus_on_contents_modified(slice(index, index + 1 or None))
        rval = super().remove(value)
        self.focus = focus
        return rval

    def reverse(self):
        """
        >>> ml = MonitoredFocusList([0,1,2,3,4], focus=1)
        >>> ml.reverse(); ml
        MonitoredFocusList([4, 3, 2, 1, 0], focus=3)
        """
        rval = super().reverse()
        self.focus = max(0, len(self) - self._focus - 1)
        return rval

    def sort(self, **kwargs):
        """
        >>> ml = MonitoredFocusList([-2,0,1,-3,2,-1,3], focus=4)
        >>> ml.sort(); ml
        MonitoredFocusList([-3, -2, -1, 0, 1, 2, 3], focus=5)
        """
        if not self:
            return None
        value = self[self._focus]
        rval = super().sort(**kwargs)
        self.focus = self.index(value)
        return rval

    if hasattr(list, "clear"):

        def clear(self):
            focus = self._adjust_focus_on_contents_modified(slice(0, 0))
            rval = super().clear()
            self.focus = focus
            return rval


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
