# Urwid main loop code
#    Copyright (C) 2004-2012  Ian Ward
#    Copyright (C) 2008 Walter Mundt
#    Copyright (C) 2009 Andrew Psaltis
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

"""Select based urwid EventLoop implementation."""

from __future__ import annotations

import contextlib
import heapq
import select
import time
import typing
from contextlib import suppress
from itertools import count

from .abstract_loop import EventLoop, ExitMainLoop

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from typing_extensions import Literal

__all__ = ("SelectEventLoop",)


class SelectEventLoop(EventLoop):
    """
    Event loop based on :func:`select.select`
    """

    def __init__(self) -> None:
        self._alarms: list[tuple[float, int, Callable[[], typing.Any]]] = []
        self._watch_files: dict[int, Callable[[], typing.Any]] = {}
        self._idle_handle: int = 0
        self._idle_callbacks: dict[int, Callable[[], typing.Any]] = {}
        self._tie_break: Iterator[int] = count()
        self._did_something: bool = False

    def alarm(
        self,
        seconds: float,
        callback: Callable[[], typing.Any],
    ) -> tuple[float, int, Callable[[], typing.Any]]:
        """
        Call callback() a given time from now.  No parameters are
        passed to callback.

        Returns a handle that may be passed to remove_alarm()

        seconds -- floating point time to wait before calling callback
        callback -- function to call from event loop
        """
        tm = time.time() + seconds
        handle = (tm, next(self._tie_break), callback)
        heapq.heappush(self._alarms, handle)
        return handle

    def remove_alarm(self, handle: tuple[float, int, Callable[[], typing.Any]]) -> bool:
        """
        Remove an alarm.

        Returns True if the alarm exists, False otherwise
        """
        try:
            self._alarms.remove(handle)
            heapq.heapify(self._alarms)

        except ValueError:
            return False

        return True

    def watch_file(self, fd: int, callback: Callable[[], typing.Any]) -> int:
        """
        Call callback() when fd has some data to read.  No parameters
        are passed to callback.

        Returns a handle that may be passed to remove_watch_file()

        fd -- file descriptor to watch for input
        callback -- function to call when input is available
        """
        self._watch_files[fd] = callback
        return fd

    def remove_watch_file(self, handle: int) -> bool:
        """
        Remove an input file.

        Returns True if the input file exists, False otherwise
        """
        if handle in self._watch_files:
            del self._watch_files[handle]
            return True
        return False

    def enter_idle(self, callback: Callable[[], typing.Any]) -> int:
        """
        Add a callback for entering idle.

        Returns a handle that may be passed to remove_idle()
        """
        self._idle_handle += 1
        self._idle_callbacks[self._idle_handle] = callback
        return self._idle_handle

    def remove_enter_idle(self, handle: int) -> bool:
        """
        Remove an idle callback.

        Returns True if the handle was removed.
        """
        try:
            del self._idle_callbacks[handle]
        except KeyError:
            return False
        return True

    def _entering_idle(self) -> None:
        """
        Call all the registered idle callbacks.
        """
        for callback in self._idle_callbacks.values():
            callback()

    def run(self) -> None:
        """
        Start the event loop.  Exit the loop when any callback raises
        an exception.  If ExitMainLoop is raised, exit cleanly.
        """
        with contextlib.suppress(ExitMainLoop):
            self._did_something = True
            while True:
                with suppress(InterruptedError):
                    self._loop()

    def _loop(self) -> None:
        """
        A single iteration of the event loop
        """
        fds = list(self._watch_files)
        if self._alarms or self._did_something:
            timeout = 0.0
            tm: float | Literal["idle"] | None = None

            if self._alarms:
                timeout_ = self._alarms[0][0]
                tm = timeout_
                timeout = max(timeout, timeout_ - time.time())

            if self._did_something and (not self._alarms or (self._alarms and timeout > 0)):
                timeout = 0.0
                tm = "idle"

            ready, w, err = select.select(fds, [], fds, timeout)

        else:
            tm = None
            ready, w, err = select.select(fds, [], fds)

        if not ready:
            if tm == "idle":
                self._entering_idle()
                self._did_something = False
            elif tm is not None:
                # must have been a timeout
                tm, tie_break, alarm_callback = heapq.heappop(self._alarms)
                alarm_callback()
                self._did_something = True

        for fd in ready:
            self._watch_files[fd]()
            self._did_something = True
