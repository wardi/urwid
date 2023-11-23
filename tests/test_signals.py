import sys
import unittest
from unittest.mock import Mock

from urwid import Edit, Signals, connect_signal, disconnect_signal, emit_signal, register_signal


class SiglnalsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.EmClass = type("EmClass", (object, ), {})
        register_signal(cls.EmClass, ["change", "test"])

    def test_connect(self):
        obj = Mock()
        handler = Mock()
        edit = Edit('')
        key = connect_signal(edit, 'change', handler, user_args=[obj])
        self.assertIsNotNone(key)
        edit.set_edit_text('long test text')
        handler.assert_called_once_with(obj, edit, 'long test text')

        handler.reset_mock()
        disconnect_signal(edit, 'change', handler, user_args=[obj])
        edit.set_edit_text('another text')
        handler.assert_not_called()

    @unittest.skipIf(sys.implementation.name == "pypy", "WeakRef works differently on PyPy")
    def test_weak_del(self):
        emitter = SiglnalsTest.EmClass()
        w1 = Mock(name="w1")
        w2 = Mock(name="w2")
        w3 = Mock(name="w3")

        handler1 = Mock(name="handler1")
        handler2 = Mock(name="handler2")

        k1 = connect_signal(emitter, 'test', handler1, weak_args=[w1], user_args=[42, "abc"])
        k2 = connect_signal(emitter, 'test', handler2, weak_args=[w2, w3], user_args=[8])
        self.assertIsNotNone(k2)

        emit_signal(emitter, 'test', "Foo")
        handler1.assert_called_once_with(w1, 42, "abc",  "Foo")
        handler2.assert_called_once_with(w2, w3, 8, "Foo")

        handler1.reset_mock()
        handler2.reset_mock()
        del w1
        self.assertEqual(
            len(getattr(emitter, Signals._signal_attr)['test']),
            1,
            getattr(emitter, Signals._signal_attr)['test']
        )
        emit_signal(emitter, 'test', "Bar")
        handler1.assert_not_called()
        handler2.assert_called_once_with(w2, w3, 8, "Bar")

        handler2.reset_mock()
        del w3
        emit_signal(emitter, 'test', "Baz")
        handler1.assert_not_called()
        handler2.assert_not_called()
        self.assertEqual(len(getattr(emitter, Signals._signal_attr)['test']), 0)
        del w2
