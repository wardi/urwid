from __future__ import annotations

import asyncio
import os
import sys
import typing
import unittest

import urwid


class EventLoopTestMixin:
    def test_event_loop(self):
        rd, wr = os.pipe()
        evl: urwid.EventLoop = self.evl
        out = []

        def step1():
            out.append("writing")
            os.write(wr, b"hi")

        def step2():
            out.append(os.read(rd, 2).decode('ascii'))
            raise urwid.ExitMainLoop

        _handle = evl.alarm(0, step1)
        _handle = evl.watch_file(rd, step2)

        evl.run()
        self.assertEqual(out, ["writing", "hi"])

    def test_remove_alarm(self):
        evl: urwid.EventLoop = self.evl
        handle = evl.alarm(50, lambda: None)

        def step1():
            self.assertTrue(evl.remove_alarm(handle))
            self.assertFalse(evl.remove_alarm(handle))
            raise urwid.ExitMainLoop

        evl.alarm(0, step1)
        evl.run()

    def test_remove_watch_file(self):
        evl: urwid.EventLoop = self.evl
        fd_r, fd_w = os.pipe()

        try:
            handle = evl.watch_file(fd_r, lambda: None)

            def step1():
                self.assertTrue(evl.remove_watch_file(handle))
                self.assertFalse(evl.remove_watch_file(handle))
                raise urwid.ExitMainLoop

            evl.alarm(0, step1)
            evl.run()
        finally:
            os.close(fd_r)
            os.close(fd_w)

    _expected_idle_handle = 1

    def test_run(self):
        evl: urwid.EventLoop = self.evl
        out = []
        rd, wr = os.pipe()
        self.assertEqual(os.write(wr, b"data"), 4)

        def say_hello():
            out.append("hello")

        def say_waiting():
            out.append("waiting")

        def exit_clean() -> typing.NoReturn:
            out.append("clean exit")
            raise urwid.ExitMainLoop

        def exit_error() -> typing.NoReturn:
            1/0

        _handle = evl.alarm(0.01, exit_clean)
        _handle = evl.alarm(0.005, say_hello)
        idle_handle = evl.enter_idle(say_waiting)
        if self._expected_idle_handle is not None:
            self.assertEqual(idle_handle, 1)

        evl.run()
        self.assertTrue("waiting" in out, out)
        self.assertTrue("hello" in out, out)
        self.assertTrue("clean exit" in out, out)
        handle = evl.watch_file(rd, exit_clean)
        del out[:]

        evl.run()
        self.assertEqual(["clean exit"], out)
        self.assertTrue(evl.remove_watch_file(handle))
        _handle = evl.alarm(0, exit_error)
        self.assertRaises(ZeroDivisionError, evl.run)
        _handle = evl.watch_file(rd, exit_error)
        self.assertRaises(ZeroDivisionError, evl.run)


class SelectEventLoopTest(unittest.TestCase, EventLoopTestMixin):
    def setUp(self):
        self.evl = urwid.SelectEventLoop()


try:
    import gi.repository
except ImportError:
    pass
else:
    class GLibEventLoopTest(unittest.TestCase, EventLoopTestMixin):
        def setUp(self):
            self.evl = urwid.GLibEventLoop()

        def test_error(self):
            evl = self.evl
            evl.alarm(0, lambda: 1 / 0)  # Simulate error in event loop
            self.assertRaises(ZeroDivisionError, evl.run)


try:
    import tornado
except ImportError:
    pass
else:
    class TornadoEventLoopTest(unittest.TestCase, EventLoopTestMixin):
        def setUp(self):
            from tornado.ioloop import IOLoop
            self.evl = urwid.TornadoEventLoop(IOLoop())

        _expected_idle_handle = None


try:
    import twisted
except ImportError:
    pass
else:
    class TwistedEventLoopTest(unittest.TestCase, EventLoopTestMixin):
        def setUp(self):
            self.evl = urwid.TwistedEventLoop()

        # can't restart twisted reactor, so use shortened tests
        def test_event_loop(self):
            pass

        def test_remove_alarm(self):
            pass

        def test_remove_watch_file(self):
            pass

        def test_run(self):
            evl = self.evl
            out = []
            rd, wr = os.pipe()
            self.assertEqual(os.write(wr, b"data"), 4)

            def step2():
                out.append(os.read(rd, 2).decode('ascii'))

            def say_hello():
                out.append("hello")

            def say_waiting():
                out.append("waiting")

            def test_remove_alarm():
                handle = evl.alarm(50, lambda: None)
                self.assertTrue(evl.remove_alarm(handle))
                self.assertFalse(evl.remove_alarm(handle))
                out.append("remove_alarm ok")

            def test_remove_watch_file():
                fd_r, fd_w = os.pipe()
                try:
                    handle = evl.watch_file(fd_r, lambda: None)
                    self.assertTrue(evl.remove_watch_file(handle))
                    self.assertFalse(evl.remove_watch_file(handle))
                finally:
                    os.close(fd_r)
                    os.close(fd_w)
                out.append("remove_watch_file ok")

            def exit_clean() -> typing.NoReturn:
                out.append("clean exit")
                raise urwid.ExitMainLoop

            def exit_error() -> typing.NoReturn:
                1/0

            _handle = evl.watch_file(rd, step2)
            _handle = evl.alarm(0.1, exit_clean)
            _handle = evl.alarm(0.05, say_hello)
            _handle = evl.alarm(0.06, test_remove_alarm)
            _handle = evl.alarm(0.07, test_remove_watch_file)
            self.assertEqual(evl.enter_idle(say_waiting), 1)
            evl.run()
            self.assertTrue("da" in out, out)
            self.assertTrue("ta" in out, out)
            self.assertTrue("hello" in out, out)
            self.assertTrue("remove_alarm ok" in out, out)
            self.assertTrue("clean exit" in out, out)

        def test_error(self):
            evl = self.evl
            evl.alarm(0, lambda: 1 / 0)  # Simulate error in event loop
            self.assertRaises(ZeroDivisionError, evl.run)


class AsyncioEventLoopTest(unittest.TestCase, EventLoopTestMixin):
    def setUp(self):
        self.evl = urwid.AsyncioEventLoop()

    _expected_idle_handle = None

    def test_error(self):
        evl = self.evl
        evl.alarm(0, lambda: 1 / 0)  # Simulate error in event loop
        self.assertRaises(ZeroDivisionError, evl.run)

    @unittest.skipIf(
        sys.implementation.name == "pypy",
        "Well known dead wait (lock?) on pypy.",
    )
    def test_coroutine_error(self):
        evl = self.evl

        async def error_coro():
            result = 1 / 0  # Simulate error in coroutine
            return result

        asyncio.ensure_future(error_coro(), loop=asyncio.get_event_loop_policy().get_event_loop())
        self.assertRaises(ZeroDivisionError, evl.run)


try:
    import trio
except ImportError:
    pass
else:
    class TrioEventLoopTest(unittest.TestCase, EventLoopTestMixin):
        def setUp(self):
            self.evl = urwid.TrioEventLoop()

        _expected_idle_handle = None

        def test_error(self):
            evl = self.evl
            evl.alarm(0, lambda: 1 / 0)  # Simulate error in event loop
            self.assertRaises(ZeroDivisionError, evl.run)


try:
    import zmq
except ImportError:
    pass
else:
    class ZMQEventLoopTest(unittest.TestCase, EventLoopTestMixin):
        def setUp(self):
            self.evl = urwid.ZMQEventLoop()
