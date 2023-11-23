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

"""Tornado IOLoop based urwid EventLoop implementation.

Tornado library is required.
"""

from __future__ import annotations

import functools
import typing
from contextlib import suppress

from tornado import ioloop

from .abstract_loop import EventLoop, ExitMainLoop

if typing.TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Literal, ParamSpec

    _Spec = ParamSpec("_Spec")
    _T = typing.TypeVar("_T")

__all__ = ("TornadoEventLoop",)


class TornadoEventLoop(EventLoop):
    """This is an Urwid-specific event loop to plug into its MainLoop.
    It acts as an adaptor for Tornado's IOLoop which does all
    heavy lifting except idle-callbacks.
    """

    def __init__(self, loop: ioloop.IOLoop | None = None) -> None:
        if loop:
            self._loop: ioloop.IOLoop = loop
        else:
            self._loop = ioloop.IOLoop.current()  # TODO(Aleksei): Switch to the syncio.EventLoop as tornado >= 6.0 !

        self._pending_alarms: dict[object, int] = {}
        self._watch_handles: dict[int, int] = {}  # {<watch_handle> : <file_descriptor>}
        self._max_watch_handle: int = 0
        self._exc: BaseException | None = None

        self._idle_asyncio_handle: object | None = None
        self._idle_handle: int = 0
        self._idle_callbacks: dict[int, Callable[[], typing.Any]] = {}

    def _also_call_idle(self, callback: Callable[_Spec, _T]) -> Callable[_Spec, _T]:
        """
        Wrap the callback to also call _entering_idle.
        """

        @functools.wraps(callback)
        def wrapper(*args: _Spec.args, **kwargs: _Spec.kwargs) -> _T:
            if not self._idle_asyncio_handle:
                self._idle_asyncio_handle = self._loop.call_later(0, self._entering_idle)
            return callback(*args, **kwargs)

        return wrapper

    def _entering_idle(self) -> None:
        """
        Call all the registered idle callbacks.
        """
        try:
            for callback in self._idle_callbacks.values():
                callback()
        finally:
            self._idle_asyncio_handle = None

    def alarm(self, seconds: float, callback: Callable[[], typing.Any]):
        @self._also_call_idle
        @functools.wraps(callback)
        def wrapped() -> None:
            with suppress(KeyError):
                del self._pending_alarms[handle]

            self.handle_exit(callback)()

        handle = self._loop.add_timeout(self._loop.time() + seconds, wrapped)
        self._pending_alarms[handle] = 1
        return handle

    def remove_alarm(self, handle: object) -> bool:
        self._loop.remove_timeout(handle)
        try:
            del self._pending_alarms[handle]
        except KeyError:
            return False
        else:
            return True

    def watch_file(self, fd: int, callback: Callable[[], _T]) -> int:
        @self._also_call_idle
        def handler(_fd: int, _events: int) -> None:
            self.handle_exit(callback)()

        self._loop.add_handler(fd, handler, ioloop.IOLoop.READ)
        self._max_watch_handle += 1
        handle = self._max_watch_handle
        self._watch_handles[handle] = fd
        return handle

    def remove_watch_file(self, handle: int) -> bool:
        fd = self._watch_handles.pop(handle, None)
        if fd is None:
            return False

        self._loop.remove_handler(fd)
        return True

    def enter_idle(self, callback: Callable[[], typing.Any]) -> int:
        """
        Add a callback for entering idle.

        Returns a handle that may be passed to remove_idle()
        """
        # XXX there's no such thing as "idle" in most event loops; this fakes
        # it by adding extra callback to the timer and file watch callbacks.
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

    def handle_exit(self, f: Callable[_Spec, _T]) -> Callable[_Spec, _T | Literal[False]]:
        @functools.wraps(f)
        def wrapper(*args: _Spec.args, **kwargs: _Spec.kwargs) -> _T | Literal[False]:
            try:
                return f(*args, **kwargs)
            except ExitMainLoop:
                pass  # handled later
            except Exception as exc:
                self._exc = exc

            if self._idle_asyncio_handle:
                # clean it up to prevent old callbacks
                # from messing things up if loop is restarted
                self._loop.remove_timeout(self._idle_asyncio_handle)
                self._idle_asyncio_handle = None

            self._loop.stop()
            return False

        return wrapper

    def run(self) -> None:
        self._loop.start()
        if self._exc:
            exc, self._exc = self._exc, None
            raise exc.with_traceback(exc.__traceback__)
