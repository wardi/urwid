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


from __future__ import annotations

import heapq
import os
import time
import typing
import warnings
from contextlib import suppress

from urwid import raw_display, signals
from urwid.command_map import Command, command_map
from urwid.display_common import INPUT_DESCRIPTORS_CHANGED
from urwid.util import StoppingContext, is_mouse_event
from urwid.widget import PopUpTarget

from .abstract_loop import ExitMainLoop
from .select_loop import SelectEventLoop

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from urwid.display_common import BaseScreen
    from urwid.widget import Widget


try:  # noqa: SIM105
    import fcntl
except ImportError:
    pass  # windows

PIPE_BUFFER_READ_SIZE = 4096  # can expect this much on Linux, so try for that

__all__ = ("CantUseExternalLoop", "MainLoop")


class CantUseExternalLoop(Exception):
    pass


class MainLoop:
    """
    This is the standard main loop implementation for a single interactive
    session.

    :param widget: the topmost widget used for painting the screen, stored as
                   :attr:`widget` and may be modified. Must be a box widget.
    :type widget: widget instance

    :param palette: initial palette for screen
    :type palette: iterable of palette entries

    :param screen: screen to use, default is a new :class:`raw_display.Screen`
                   instance; stored as :attr:`screen`
    :type screen: display module screen instance

    :param handle_mouse: ``True`` to ask :attr:`.screen` to process mouse events
    :type handle_mouse: bool

    :param input_filter: a function to filter input before sending it to
                   :attr:`.widget`, called from :meth:`.input_filter`
    :type input_filter: callable

    :param unhandled_input: a function called when input is not handled by
                            :attr:`.widget`, called from :meth:`.unhandled_input`
    :type unhandled_input: callable

    :param event_loop: if :attr:`.screen` supports external an event loop it may be
                       given here, default is a new :class:`SelectEventLoop` instance;
                       stored as :attr:`.event_loop`
    :type event_loop: event loop instance

    :param pop_ups: `True` to wrap :attr:`.widget` with a :class:`PopUpTarget`
                    instance to allow any widget to open a pop-up anywhere on the screen
    :type pop_ups: boolean


    .. attribute:: screen

        The screen object this main loop uses for screen updates and reading input

    .. attribute:: event_loop

        The event loop object this main loop uses for waiting on alarms and IO
    """

    def __init__(
        self,
        widget: Widget,
        palette=(),
        screen: BaseScreen | None = None,
        handle_mouse: bool = True,
        input_filter: Callable[[list[str], list[int]], list[str]] | None = None,
        unhandled_input: Callable[[str | tuple[str, int, int, int]], bool] | None = None,
        event_loop=None,
        pop_ups: bool = False,
    ):
        self._widget = widget
        self.handle_mouse = handle_mouse
        self.pop_ups = pop_ups  # triggers property setting side-effect

        if not screen:
            screen = raw_display.Screen()

        if palette:
            screen.register_palette(palette)

        self.screen = screen
        self.screen_size = None

        self._unhandled_input = unhandled_input
        self._input_filter = input_filter

        if not hasattr(screen, "hook_event_loop") and event_loop is not None:
            raise NotImplementedError(f"screen object passed {screen!r} does not support external event loops")
        if event_loop is None:
            event_loop = SelectEventLoop()
        self.event_loop = event_loop

        if hasattr(self.screen, "signal_handler_setter"):
            # Tell the screen what function it must use to set
            # signal handlers
            self.screen.signal_handler_setter = self.event_loop.set_signal_handler

        self._watch_pipes: dict[int, tuple[Callable[[], typing.Any], int]] = {}

    @property
    def widget(self) -> Widget:
        """
        Property for the topmost widget used to draw the screen.
        This must be a box widget.
        """
        return self._widget

    @widget.setter
    def widget(self, widget: Widget) -> None:
        self._widget = widget
        if self.pop_ups:
            self._topmost_widget.original_widget = self._widget
        else:
            self._topmost_widget = self._widget

    def _set_widget(self, widget: Widget) -> None:
        warnings.warn(
            f"method `{self.__class__.__name__}._set_widget` is deprecated, "
            f"please use `{self.__class__.__name__}.widget` property",
            DeprecationWarning,
            stacklevel=2,
        )
        self.widget = widget

    @property
    def pop_ups(self):
        return self._pop_ups

    @pop_ups.setter
    def pop_ups(self, pop_ups) -> None:
        self._pop_ups = pop_ups
        if pop_ups:
            self._topmost_widget = PopUpTarget(self._widget)
        else:
            self._topmost_widget = self._widget

    def _set_pop_ups(self, pop_ups) -> None:
        warnings.warn(
            f"method `{self.__class__.__name__}._set_pop_ups` is deprecated, "
            f"please use `{self.__class__.__name__}.pop_ups` property",
            DeprecationWarning,
            stacklevel=2,
        )
        self.pop_ups = pop_ups

    def set_alarm_in(self, sec, callback, user_data=None):
        """
        Schedule an alarm in *sec* seconds that will call *callback* from the
        within the :meth:`run` method.

        :param sec: seconds until alarm
        :type sec: float
        :param callback: function to call with two parameters: this main loop
                         object and *user_data*
        :type callback: callable
        """

        def cb():
            callback(self, user_data)

        return self.event_loop.alarm(sec, cb)

    def set_alarm_at(self, tm, callback, user_data=None):
        """
        Schedule an alarm at *tm* time that will call *callback* from the
        within the :meth:`run` function. Returns a handle that may be passed to
        :meth:`remove_alarm`.

        :param tm: time to call callback e.g. ``time.time() + 5``
        :type tm: float
        :param callback: function to call with two parameters: this main loop
                         object and *user_data*
        :type callback: callable
        """

        def cb():
            callback(self, user_data)

        return self.event_loop.alarm(tm - time.time(), cb)

    def remove_alarm(self, handle):
        """
        Remove an alarm. Return ``True`` if *handle* was found, ``False``
        otherwise.
        """
        return self.event_loop.remove_alarm(handle)

    def watch_pipe(self, callback):
        """
        Create a pipe for use by a subprocess or thread to trigger a callback
        in the process/thread running the main loop.

        :param callback: function taking one parameter to call from within
                         the process/thread running the main loop
        :type callback: callable

        This method returns a file descriptor attached to the write end of a
        pipe. The read end of the pipe is added to the list of files
        :attr:`event_loop` is watching. When data is written to the pipe the
        callback function will be called and passed a single value containing
        data read from the pipe.

        This method may be used any time you want to update widgets from
        another thread or subprocess.

        Data may be written to the returned file descriptor with
        ``os.write(fd, data)``. Ensure that data is less than 512 bytes (or 4K
        on Linux) so that the callback will be triggered just once with the
        complete value of data passed in.

        If the callback returns ``False`` then the watch will be removed from
        :attr:`event_loop` and the read end of the pipe will be closed. You
        are responsible for closing the write end of the pipe with
        ``os.close(fd)``.
        """
        pipe_rd, pipe_wr = os.pipe()
        fcntl.fcntl(pipe_rd, fcntl.F_SETFL, os.O_NONBLOCK)
        watch_handle = None

        def cb() -> None:
            data = os.read(pipe_rd, PIPE_BUFFER_READ_SIZE)
            rval = callback(data)
            if rval is False:
                self.event_loop.remove_watch_file(watch_handle)
                os.close(pipe_rd)

        watch_handle = self.event_loop.watch_file(pipe_rd, cb)
        self._watch_pipes[pipe_wr] = (watch_handle, pipe_rd)
        return pipe_wr

    def remove_watch_pipe(self, write_fd):
        """
        Close the read end of the pipe and remove the watch created by
        :meth:`watch_pipe`. You are responsible for closing the write end of
        the pipe.

        Returns ``True`` if the watch pipe exists, ``False`` otherwise
        """
        try:
            watch_handle, pipe_rd = self._watch_pipes.pop(write_fd)
        except KeyError:
            return False

        if not self.event_loop.remove_watch_file(watch_handle):
            return False
        os.close(pipe_rd)
        return True

    def watch_file(self, fd, callback):
        """
        Call *callback* when *fd* has some data to read. No parameters are
        passed to callback.

        Returns a handle that may be passed to :meth:`remove_watch_file`.
        """
        return self.event_loop.watch_file(fd, callback)

    def remove_watch_file(self, handle):
        """
        Remove a watch file. Returns ``True`` if the watch file
        exists, ``False`` otherwise.
        """
        return self.event_loop.remove_watch_file(handle)

    def run(self):
        """
        Start the main loop handling input events and updating the screen. The
        loop will continue until an :exc:`ExitMainLoop` exception is raised.

        If you would prefer to manage the event loop yourself, don't use this
        method.  Instead, call :meth:`start` before starting the event loop,
        and :meth:`stop` once it's finished.
        """
        with suppress(ExitMainLoop):
            self._run()

    def _test_run(self):
        """
        >>> w = _refl("widget")   # _refl prints out function calls
        >>> w.render_rval = "fake canvas"  # *_rval is used for return values
        >>> scr = _refl("screen")
        >>> scr.get_input_descriptors_rval = [42]
        >>> scr.get_cols_rows_rval = (20, 10)
        >>> scr.started = True
        >>> scr._urwid_signals = {}
        >>> evl = _refl("event_loop")
        >>> evl.enter_idle_rval = 1
        >>> evl.watch_file_rval = 2
        >>> ml = MainLoop(w, [], scr, event_loop=evl)
        >>> ml.run()    # doctest:+ELLIPSIS
        screen.start()
        screen.set_mouse_tracking()
        screen.unhook_event_loop(...)
        screen.hook_event_loop(...)
        event_loop.enter_idle(<bound method MainLoop.entering_idle...>)
        event_loop.run()
        event_loop.remove_enter_idle(1)
        screen.unhook_event_loop(...)
        screen.stop()
        >>> ml.draw_screen()    # doctest:+ELLIPSIS
        screen.get_cols_rows()
        widget.render((20, 10), focus=True)
        screen.draw_screen((20, 10), 'fake canvas')
        """

    def start(self):
        """
        Sets up the main loop, hooking into the event loop where necessary.
        Starts the :attr:`screen` if it hasn't already been started.

        If you want to control starting and stopping the event loop yourself,
        you should call this method before starting, and call `stop` once the
        loop has finished.  You may also use this method as a context manager,
        which will stop the loop automatically at the end of the block:

            with main_loop.start():
                ...

        Note that some event loop implementations don't handle exceptions
        specially if you manage the event loop yourself.  In particular, the
        Twisted and asyncio loops won't stop automatically when
        :exc:`ExitMainLoop` (or anything else) is raised.
        """

        self.screen.start()

        if self.handle_mouse:
            self.screen.set_mouse_tracking()

        if not hasattr(self.screen, "hook_event_loop"):
            raise CantUseExternalLoop("Screen {0!r} doesn't support external event loops")

        with suppress(NameError):
            signals.connect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED, self._reset_input_descriptors)

        # watch our input descriptors
        self._reset_input_descriptors()
        self.idle_handle = self.event_loop.enter_idle(self.entering_idle)

        # the screen is redrawn automatically after input and alarms,
        # however, there can be none of those at the start,
        # so draw the initial screen here unconditionally
        self.event_loop.alarm(0, self.entering_idle)

        return StoppingContext(self)

    def stop(self) -> None:
        """
        Cleans up any hooks added to the event loop.  Only call this if you're
        managing the event loop yourself, after the loop stops.
        """

        self.event_loop.remove_enter_idle(self.idle_handle)
        del self.idle_handle
        signals.disconnect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED, self._reset_input_descriptors)
        self.screen.unhook_event_loop(self.event_loop)

        self.screen.stop()

    def _reset_input_descriptors(self) -> None:
        self.screen.unhook_event_loop(self.event_loop)
        self.screen.hook_event_loop(self.event_loop, self._update)

    def _run(self) -> None:
        try:
            self.start()
        except CantUseExternalLoop:
            try:
                self._run_screen_event_loop()
                return
            finally:
                self.screen.stop()

        try:
            self.event_loop.run()
        except:
            self.screen.stop()  # clean up screen control
            raise
        self.stop()

    def _update(self, keys: list[str], raw: list[int]) -> None:
        """
        >>> w = _refl("widget")
        >>> w.selectable_rval = True
        >>> w.mouse_event_rval = True
        >>> scr = _refl("screen")
        >>> scr.get_cols_rows_rval = (15, 5)
        >>> evl = _refl("event_loop")
        >>> ml = MainLoop(w, [], scr, event_loop=evl)
        >>> ml._input_timeout = "old timeout"
        >>> ml._update(['y'], [121])    # doctest:+ELLIPSIS
        screen.get_cols_rows()
        widget.selectable()
        widget.keypress((15, 5), 'y')
        >>> ml._update([("mouse press", 1, 5, 4)], [])
        widget.mouse_event((15, 5), 'mouse press', 1, 5, 4, focus=True)
        >>> ml._update([], [])
        """
        keys = self.input_filter(keys, raw)

        if keys:
            self.process_input(keys)
            if "window resize" in keys:
                self.screen_size = None

    def _run_screen_event_loop(self) -> None:
        """
        This method is used when the screen does not support using
        external event loops.

        The alarms stored in the SelectEventLoop in :attr:`event_loop`
        are modified by this method.
        """
        next_alarm = None

        while True:
            self.draw_screen()

            if not next_alarm and self.event_loop._alarms:
                next_alarm = heapq.heappop(self.event_loop._alarms)

            keys: list[str] = []
            raw: list[int] = []
            while not keys:
                if next_alarm:
                    sec = max(0, next_alarm[0] - time.time())
                    self.screen.set_input_timeouts(sec)
                else:
                    self.screen.set_input_timeouts(None)
                keys, raw = self.screen.get_input(True)
                if not keys and next_alarm:
                    sec = next_alarm[0] - time.time()
                    if sec <= 0:
                        break

            keys = self.input_filter(keys, raw)

            if keys:
                self.process_input(keys)

            while next_alarm:
                sec = next_alarm[0] - time.time()
                if sec > 0:
                    break
                tm, tie_break, callback = next_alarm
                callback()

                if self.event_loop._alarms:
                    next_alarm = heapq.heappop(self.event_loop._alarms)
                else:
                    next_alarm = None

            if "window resize" in keys:
                self.screen_size = None

    def _test_run_screen_event_loop(self):
        """
        >>> w = _refl("widget")
        >>> scr = _refl("screen")
        >>> scr.get_cols_rows_rval = (10, 5)
        >>> scr.get_input_rval = [], []
        >>> ml = MainLoop(w, screen=scr)
        >>> def stop_now(loop, data):
        ...     raise ExitMainLoop()
        >>> handle = ml.set_alarm_in(0, stop_now)
        >>> try:
        ...     ml._run_screen_event_loop()
        ... except ExitMainLoop:
        ...     pass
        screen.get_cols_rows()
        widget.render((10, 5), focus=True)
        screen.draw_screen((10, 5), None)
        screen.set_input_timeouts(0)
        screen.get_input(True)
        """

    def process_input(self, keys: Iterable[str | tuple[str, int, int, int]]) -> bool:
        """
        This method will pass keyboard input and mouse events to :attr:`widget`.
        This method is called automatically from the :meth:`run` method when
        there is input, but may also be called to simulate input from the user.

        *keys* is a list of input returned from :attr:`screen`'s get_input()
        or get_input_nonblocking() methods.

        Returns ``True`` if any key was handled by a widget or the
        :meth:`unhandled_input` method.
        """
        if not self.screen_size:
            self.screen_size = self.screen.get_cols_rows()

        something_handled = False

        for k in keys:
            if k == "window resize":
                continue

            if isinstance(k, str):
                if self._topmost_widget.selectable():
                    k = self._topmost_widget.keypress(self.screen_size, k)  # noqa: PLW2901

            elif isinstance(k, tuple):
                if is_mouse_event(k):
                    event, button, col, row = k
                    if hasattr(self._topmost_widget, "mouse_event") and self._topmost_widget.mouse_event(
                        self.screen_size,
                        event,
                        button,
                        col,
                        row,
                        focus=True,
                    ):
                        k = None  # noqa: PLW2901

            else:
                raise TypeError(f"{k!r} is not str | tuple[str, int, int, int]")

            if k:
                if command_map[k] == Command.REDRAW_SCREEN:
                    self.screen.clear()
                    something_handled = True
                else:
                    something_handled |= bool(self.unhandled_input(k))
            else:
                something_handled = True

        return something_handled

    def _test_process_input(self):
        """
        >>> w = _refl("widget")
        >>> w.selectable_rval = True
        >>> scr = _refl("screen")
        >>> scr.get_cols_rows_rval = (10, 5)
        >>> ml = MainLoop(w, [], scr)
        >>> ml.process_input(['enter', ('mouse drag', 1, 14, 20)])
        screen.get_cols_rows()
        widget.selectable()
        widget.keypress((10, 5), 'enter')
        widget.mouse_event((10, 5), 'mouse drag', 1, 14, 20, focus=True)
        True
        """

    def input_filter(self, keys: list[str], raw: list[int]) -> list[str]:
        """
        This function is passed each all the input events and raw keystroke
        values. These values are passed to the *input_filter* function
        passed to the constructor. That function must return a list of keys to
        be passed to the widgets to handle. If no *input_filter* was
        defined this implementation will return all the input events.
        """
        if self._input_filter:
            return self._input_filter(keys, raw)
        return keys

    def unhandled_input(self, data: str | tuple[str, int, int, int]) -> bool:
        """
        This function is called with any input that was not handled by the
        widgets, and calls the *unhandled_input* function passed to the
        constructor. If no *unhandled_input* was defined then the input
        will be ignored.

        *input* is the keyboard or mouse input.

        The *unhandled_input* function should return ``True`` if it handled
        the input.
        """
        if self._unhandled_input:
            return self._unhandled_input(data)
        return False

    def entering_idle(self):
        """
        This method is called whenever the event loop is about to enter the
        idle state. :meth:`draw_screen` is called here to update the
        screen when anything has changed.
        """
        if self.screen.started:
            self.draw_screen()

    def draw_screen(self):
        """
        Render the widgets and paint the screen. This method is called
        automatically from :meth:`entering_idle`.

        If you modify the widgets displayed outside of handling input or
        responding to an alarm you will need to call this method yourself
        to repaint the screen.
        """
        if not self.screen_size:
            self.screen_size = self.screen.get_cols_rows()

        canvas = self._topmost_widget.render(self.screen_size, focus=True)
        self.screen.draw_screen(self.screen_size, canvas)


def _refl(name: str, rval=None, loop_exit=False):
    """
    This function is used to test the main loop classes.

    >>> scr = _refl("screen")
    >>> scr.function("argument")
    screen.function('argument')
    >>> scr.callme(when="now")
    screen.callme(when='now')
    >>> scr.want_something_rval = 42
    >>> x = scr.want_something()
    screen.want_something()
    >>> x
    42

    """

    class Reflect:
        def __init__(self, name: str, rval=None):
            self._name = name
            self._rval = rval

        def __call__(self, *argl, **argd):
            args = ", ".join([repr(a) for a in argl])
            if args and argd:
                args = f"{args}, "
            args += ", ".join([f"{k}={v!r}" for k, v in argd.items()])
            print(f"{self._name}({args})")
            if loop_exit:
                raise ExitMainLoop()
            return self._rval

        def __getattr__(self, attr):
            if attr.endswith("_rval"):
                raise AttributeError()
            # print(self._name+"."+attr)
            if hasattr(self, f"{attr}_rval"):
                return Reflect(f"{self._name}.{attr}", getattr(self, f"{attr}_rval"))
            return Reflect(f"{self._name}.{attr}")

    return Reflect(name)


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
