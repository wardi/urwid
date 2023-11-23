# Urwid terminal emulation widget unit tests
#    Copyright (C) 2010  aszlig
#    Copyright (C) 2011  Ian Ward
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

import errno
import os
import sys
import typing
import unittest
from itertools import dropwhile
from time import sleep

from urwid import BoxAdapter, Widget, signals, vterm
from urwid.listbox import ListBox


class DummyCommand:
    QUITSTRING = b'|||quit|||'

    def __init__(self) -> None:
        self.reader, self.writer = os.pipe()

    def __call__(self) -> None:
        # reset
        stdout = getattr(sys.stdout, 'buffer', sys.stdout)
        stdout.write(b'\x1bc')

        while True:
            data = self.read(1024)
            if self.QUITSTRING == data:
                break
            stdout.write(data)
            stdout.flush()

    def read(self, size: int) -> bytes:
        while True:
            try:
                return os.read(self.reader, size)
            except OSError as e:
                if e.errno != errno.EINTR:
                    raise

    def write(self, data: bytes) -> None:
        os.write(self.writer, data)
        sleep(0.025)

    def quit(self) -> None:
        self.write(self.QUITSTRING)


class TermTest(unittest.TestCase):
    def setUp(self) -> None:
        self.command = DummyCommand()

        self.term = vterm.Terminal(self.command)
        self.resize(80, 24)

    def tearDown(self) -> None:
        self.command.quit()

    def connect_signal(self, signal: str):
        self._sig_response = None

        def _set_signal_response(widget: Widget, *args, **kwargs) -> None:
            self._sig_response = (args, kwargs)
        self._set_signal_response = _set_signal_response

        signals.connect_signal(self.term, signal, self._set_signal_response)

    def expect_signal(self, *args, **kwargs):
        self.assertEqual(self._sig_response, (args, kwargs))

    def disconnect_signal(self, signal: str) -> None:
        signals.disconnect_signal(self.term, signal, self._set_signal_response)

    def caught_beep(self, obj):
        self.beeped = True

    def resize(self, width: int, height: int, soft: bool = False) -> None:
        self.termsize = (width, height)
        if not soft:
            self.term.render(self.termsize, focus=False)

    def write(self, data: str) -> None:
        data = data.encode('iso8859-1')
        self.command.write(data.replace(br'\e', b'\x1b'))

    def flush(self) -> None:
        self.write(chr(0x7f))

    @typing.overload
    def read(self, raw: bool = False, focus: bool = ...) -> bytes:
        ...

    @typing.overload
    def read(self, raw: bool = True, focus: bool = ...) -> list[list[bytes, typing.Any, typing.Any]]:
        ...

    def read(self, raw: bool = False, focus: bool = False) -> bytes | list[list[bytes, typing.Any, typing.Any]]:
        self.term.wait_and_feed()
        rendered = self.term.render(self.termsize, focus=focus)
        if raw:
            is_empty = lambda c: c == (None, None, b' ')
            content = list(rendered.content())
            lines = (tuple(dropwhile(is_empty, reversed(line))) for line in content)
            return [list(reversed(line)) for line in lines if line]
        else:
            content = rendered.text
            lines = (line.rstrip() for line in content)
            return b'\n'.join(lines).rstrip()

    def expect(
        self,
        what: str | list[tuple[typing.Any, str | None, bytes]],
        desc: str | None = None, raw: bool = False,
        focus: bool = False,
    ) -> None:
        if not isinstance(what, list):
            what = what.encode('iso8859-1')
        got = self.read(raw=raw, focus=focus)
        if desc is None:
            desc = ''
        else:
            desc += '\n'
        desc += f'Expected:\n{what!r}\nGot:\n{got!r}'
        self.assertEqual(got, what, desc)

    def test_simplestring(self):
        self.write('hello world')
        self.expect('hello world')

    def test_linefeed(self):
        self.write('hello\x0aworld')
        self.expect('hello\nworld')

    def test_linefeed2(self):
        self.write('aa\b\b\\eDbb')
        self.expect('aa\nbb')

    def test_carriage_return(self):
        self.write('hello\x0dworld')
        self.expect('world')

    def test_insertlines(self):
        self.write('\\e[0;0flast\\e[0;0f\\e[10L\\e[0;0ffirst\nsecond\n\\e[11D')
        self.expect('first\nsecond\n\n\n\n\n\n\n\n\nlast')

    def test_deletelines(self):
        self.write('1\n2\n3\n4\\e[2;1f\\e[2M')
        self.expect('1\n4')

    def test_nul(self):
        self.write('a\0b')
        self.expect('ab')

    def test_movement(self):
        self.write(r'\e[10;20H11\e[10;0f\e[20C\e[K')
        self.expect('\n' * 9 + ' ' * 19 + '1')
        self.write('\\e[A\\e[B\\e[C\\e[D\b\\e[K')
        self.expect('')
        self.write(r'\e[50A2')
        self.expect(' ' * 19 + '2')
        self.write('\b\\e[K\\e[50B3')
        self.expect('\n' * 23 + ' ' * 19 + '3')
        self.write('\b\\e[K' + r'\eM' * 30 + r'\e[100C4')
        self.expect(' ' * 79 + '4')
        self.write(r'\e[100D\e[K5')
        self.expect('5')

    def edgewall(self):
        edgewall = '1-\\e[1;%(x)df-2\\e[%(y)d;1f3-\\e[%(y)d;%(x)df-4\x0d'
        self.write(edgewall % {'x': self.termsize[0] - 1,
                               'y': self.termsize[1] - 1})

    def test_horizontal_resize(self):
        self.resize(80, 24)
        self.edgewall()
        self.expect('1-' + ' ' * 76 + '-2' + '\n' * 22
                         + '3-' + ' ' * 76 + '-4')
        self.resize(78, 24, soft=True)
        self.flush()
        self.expect('1-' + '\n' * 22 + '3-')
        self.resize(80, 24, soft=True)
        self.flush()
        self.expect('1-' + '\n' * 22 + '3-')

    def test_vertical_resize(self):
        self.resize(80, 24)
        self.edgewall()
        self.expect('1-' + ' ' * 76 + '-2' + '\n' * 22
                         + '3-' + ' ' * 76 + '-4')
        for y in range(23, 1, -1):
            self.resize(80, y, soft=True)
            self.write(r'\e[%df\e[J3-\e[%d;%df-4' % (y, y, 79))
            desc = "try to rescale to 80x%d." % y
            self.expect('\n' * (y - 2) + '3-' + ' ' * 76 + '-4', desc)
        self.resize(80, 24, soft=True)
        self.flush()
        self.expect('1-' + ' ' * 76 + '-2' + '\n' * 22
                         + '3-' + ' ' * 76 + '-4')

    def write_movements(self, arg):
        fmt = 'XXX\n\\e[faaa\\e[Bccc\\e[Addd\\e[Bfff\\e[Cbbb\\e[A\\e[Deee'
        self.write(fmt.replace(r'\e[', r'\e['+arg))

    def test_defargs(self):
        self.write_movements('')
        self.expect('aaa   ddd      eee\n   ccc   fff bbb')

    def test_nullargs(self):
        self.write_movements('0')
        self.expect('aaa   ddd      eee\n   ccc   fff bbb')

    def test_erase_line(self):
        self.write('1234567890\\e[5D\\e[K\n1234567890\\e[5D\\e[1K\naaaaaaaaaaaaaaa\\e[2Ka')
        self.expect('12345\n      7890\n               a')

    def test_erase_display(self):
        self.write(r'1234567890\e[5D\e[Ja')
        self.expect('12345a')
        self.write(r'98765\e[8D\e[1Jx')
        self.expect('   x5a98765')

    def test_scrolling_region_simple(self):
        # TODO(Aleksei): Issue #544
        self.write('\\e[10;20r\\e[10f1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\\e[faa')
        self.expect('aa' + '\n' * 9 + '2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12')

    def test_scrolling_region_reverse(self):
        self.write('\\e[2J\\e[1;2r\\e[5Baaa\r\\eM\\eM\\eMbbb\nXXX')
        self.expect('\n\nbbb\nXXX\n\naaa')

    def test_scrolling_region_move(self):
        self.write('\\e[10;20r\\e[2J\\e[10Bfoo\rbar\rblah\rmooh\r\\e[10Aone\r\\eM\\eMtwo\r\\eM\\eMthree\r\\eM\\eMa')
        self.expect('ahree\n\n\n\n\n\n\n\n\n\nmooh')

    def test_scrolling_twice(self):
        self.write(r'\e[?6h\e[10;20r\e[2;5rtest')
        self.expect('\ntest')

    def test_cursor_scrolling_region(self):
        # TODO(Aleksei): Issue #544
        self.write('\\e[?6h\\e[10;20r\\e[10f1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\\e[faa')
        self.expect('\n' * 9 + 'aa\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12')

    def test_scrolling_region_simple_with_focus(self):
        # TODO(Aleksei): Issue #544
        self.write('\\e[10;20r\\e[10f1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\\e[faa')
        self.expect('aa' + '\n' * 9 + '2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12', focus=True)

    def test_scrolling_region_reverse_with_focus(self):
        self.write('\\e[2J\\e[1;2r\\e[5Baaa\r\\eM\\eM\\eMbbb\nXXX')
        self.expect('\n\nbbb\nXXX\n\naaa', focus=True)

    def test_scrolling_region_move_with_focus(self):
        self.write('\\e[10;20r\\e[2J\\e[10Bfoo\rbar\rblah\rmooh\r\\e[10Aone\r\\eM\\eMtwo\r\\eM\\eMthree\r\\eM\\eMa')
        self.expect('ahree\n\n\n\n\n\n\n\n\n\nmooh', focus=True)

    def test_scrolling_twice_with_focus(self):
        self.write(r'\e[?6h\e[10;20r\e[2;5rtest')
        self.expect('\ntest', focus=True)

    def test_cursor_scrolling_region_with_focus(self):
        # TODO(Aleksei): Issue #544
        self.write('\\e[?6h\\e[10;20r\\e[10f1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\\e[faa')
        self.expect('\n' * 9 + 'aa\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12', focus=True)

    def test_relative_region_jump(self):
        self.write(r'\e[21H---\e[10;20r\e[?6h\e[18Htest')
        self.expect('\n' * 19 + 'test\n---')

    def test_set_multiple_modes(self):
        self.write(r'\e[?6;5htest')
        self.expect('test')
        self.assertTrue(self.term.term_modes.constrain_scrolling)
        self.assertTrue(self.term.term_modes.reverse_video)
        self.write(r'\e[?6;5l')
        self.expect('test')
        self.assertFalse(self.term.term_modes.constrain_scrolling)
        self.assertFalse(self.term.term_modes.reverse_video)

    def test_wrap_simple(self):
        self.write(r'\e[?7h\e[1;%dHtt' % self.term.width)
        self.expect(' ' * (self.term.width - 1) + 't\nt')

    def test_wrap_backspace_tab(self):
        self.write('\\e[?7h\\e[1;%dHt\b\b\t\ta' % self.term.width)
        self.expect(' ' * (self.term.width - 1) + 'a')

    def test_cursor_visibility(self):
        self.write(r'\e[?25linvisible')
        self.expect('invisible', focus=True)
        self.assertEqual(self.term.term.cursor, None)
        self.write('\rvisible\\e[?25h\\e[K')
        self.expect('visible', focus=True)
        self.assertNotEqual(self.term.term.cursor, None)

    def test_get_utf8_len(self):
        length = self.term.term.get_utf8_len(int("11110000", 2))
        self.assertEqual(length, 3)
        length = self.term.term.get_utf8_len(int("11000000", 2))
        self.assertEqual(length, 1)
        length = self.term.term.get_utf8_len(int("11111101", 2))
        self.assertEqual(length, 5)

    def test_encoding_unicode(self):
        vterm.util._target_encoding = 'utf-8'
        self.write('\\e%G\xe2\x80\x94')
        self.expect('\xe2\x80\x94')

    def test_encoding_unicode_ascii(self):
        vterm.util._target_encoding = 'ascii'
        self.write('\\e%G\xe2\x80\x94')
        self.expect('?')

    def test_encoding_wrong_unicode(self):
        vterm.util._target_encoding = 'utf-8'
        self.write('\\e%G\xc0\x99')
        self.expect('')

    def test_encoding_vt100_graphics(self):
        vterm.util._target_encoding = 'ascii'
        self.write('\\e)0\\e(0\x0fg\x0eg\\e)Bn\\e)0g\\e)B\\e(B\x0fn')
        self.expect([[
            (None, '0', b'g'), (None, '0', b'g'),
            (None, None, b'n'), (None, '0', b'g'),
            (None, None, b'n')
        ]], raw=True)

    def test_ibmpc_mapping(self):
        vterm.util._target_encoding = 'ascii'

        self.write('\\e[11m\x18\\e[10m\x18')
        self.expect([[(None, 'U', b'\x18')]], raw=True)

        self.write('\\ec\\e)U\x0e\x18\x0f\\e[3h\x18\\e[3l\x18')
        self.expect([[(None, None, b'\x18')]], raw=True)

        self.write('\\ec\\e[11m\xdb\x18\\e[10m\xdb')
        self.expect([[
            (None, 'U', b'\xdb'), (None, 'U', b'\x18'),
            (None, None, b'\xdb')
        ]], raw=True)

    def test_set_title(self):
        self._the_title = None

        def _change_title(widget, title):
            self._the_title = title

        self.connect_signal('title')
        self.write('\\e]666parsed right?\\e\\te\\e]0;test title\007st1')
        self.expect('test1')
        self.expect_signal('test title')
        self.write('\\e];stupid title\\e\\\\e[0G\\e[2Ktest2')
        self.expect('test2')
        self.expect_signal('stupid title')
        self.disconnect_signal('title')

    def test_set_leds(self):
        self.connect_signal('leds')
        self.write(r'\e[0qtest1')
        self.expect('test1')
        self.expect_signal('clear')
        self.write(r'\e[3q\e[H\e[Ktest2')
        self.expect('test2')
        self.expect_signal('caps_lock')
        self.disconnect_signal('leds')

    def test_in_listbox(self):
        listbox = ListBox([BoxAdapter(self.term, 80)])
        rendered = listbox.render((80, 24))

    def test_bracketed_paste_mode_on(self):
        self.write(r'\e[?2004htest')
        self.expect('test')
        self.assertTrue(self.term.term_modes.bracketed_paste)
        self.term.keypress(None, 'begin paste')
        self.term.keypress(None, 'A')
        self.term.keypress(None, 'end paste')
        sleep(0.1)
        self.expect(r'test^[[200~A^[[201~')

    def test_bracketed_paste_mode_off(self):
        self.write(r'\e[?2004ltest')
        self.expect('test')
        self.assertFalse(self.term.term_modes.bracketed_paste)
        self.term.keypress(None, 'begin paste')
        self.term.keypress(None, 'B')
        self.term.keypress(None, 'end paste')
        sleep(0.1)
        self.expect(r'testB')
