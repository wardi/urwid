from __future__ import annotations

import typing
import warnings

from .constants import Align, Sizing, WrapMode
from .text import Text
from .widget import Widget

if typing.TYPE_CHECKING:
    from urwid.canvas import TextCanvas


class ProgressBar(Widget):
    _sizing = frozenset([Sizing.FLOW])

    eighths = " ▏▎▍▌▋▊▉"

    text_align = Align.CENTER

    def __init__(self, normal, complete, current: int = 0, done: int = 100, satt=None):
        """
        :param normal: display attribute for incomplete part of progress bar
        :param complete: display attribute for complete part of progress bar
        :param current: current progress
        :param done: progress amount at 100%
        :param satt: display attribute for smoothed part of bar where the
                     foreground of satt corresponds to the normal part and the
                     background corresponds to the complete part.  If satt
                     is ``None`` then no smoothing will be done.

        >>> pb = ProgressBar('a', 'b')
        >>> pb
        <ProgressBar flow widget>
        >>> print(pb.get_text())
        0 %
        >>> pb.set_completion(34.42)
        >>> print(pb.get_text())
        34 %
        >>> class CustomProgressBar(ProgressBar):
        ...     def get_text(self):
        ...         return u'Foobar'
        >>> cpb = CustomProgressBar('a', 'b')
        >>> print(cpb.get_text())
        Foobar
        >>> for x in range(101):
        ...     cpb.set_completion(x)
        ...     s = cpb.render((10, ))
        >>> cpb2 = CustomProgressBar('a', 'b', satt='c')
        >>> for x in range(101):
        ...     cpb2.set_completion(x)
        ...     s = cpb2.render((10, ))
        """
        self.normal = normal
        self.complete = complete
        self._current = current
        self._done = done
        self.satt = satt

    def set_completion(self, current):
        """
        current -- current progress
        """
        self._current = current
        self._invalidate()

    current = property(lambda self: self._current, set_completion)

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, done):
        """
        done -- progress amount at 100%
        """
        self._done = done
        self._invalidate()

    def _set_done(self, done):
        warnings.warn(
            f"Method `{self.__class__.__name__}._set_done` is deprecated, "
            f"please use property `{self.__class__.__name__}.done`",
            DeprecationWarning,
            stacklevel=2,
        )
        self.done = done

    def rows(self, size, focus: bool = False) -> int:
        return 1

    def get_text(self) -> str:
        """
        Return the progress bar percentage text.
        You can override this method to display custom text.
        """
        percent = min(100, max(0, int(self.current * 100 / self.done)))
        return f"{percent!s} %"

    def render(self, size: tuple[int], focus: bool = False) -> TextCanvas:
        """
        Render the progress bar.
        """
        (maxcol,) = size
        txt = Text(self.get_text(), self.text_align, WrapMode.CLIP)
        c = txt.render((maxcol,))

        cf = float(self.current) * maxcol / self.done
        ccol_dirty = int(cf)
        ccol = len(c._text[0][:ccol_dirty].decode("utf-8", "ignore").encode("utf-8"))
        cs = 0
        if self.satt is not None:
            cs = int((cf - ccol) * 8)
        if ccol < 0 or (ccol == cs == 0):
            c._attr = [[(self.normal, maxcol)]]
        elif ccol >= maxcol:
            c._attr = [[(self.complete, maxcol)]]
        elif cs and c._text[0][ccol] == 32:
            t = c._text[0]
            cenc = self.eighths[cs].encode("utf-8")
            c._text[0] = t[:ccol] + cenc + t[ccol + 1 :]
            a = []
            if ccol > 0:
                a.append((self.complete, ccol))
            a.append((self.satt, len(cenc)))
            if maxcol - ccol - 1 > 0:
                a.append((self.normal, maxcol - ccol - 1))
            c._attr = [a]
            c._cs = [[(None, len(c._text[0]))]]
        else:
            c._attr = [[(self.complete, ccol), (self.normal, maxcol - ccol)]]
        return c
