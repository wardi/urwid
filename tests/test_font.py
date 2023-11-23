from __future__ import annotations

import unittest

import urwid


class TestFontRender(unittest.TestCase):
    def setUp(self) -> None:
        self.old_encoding = urwid.util._target_encoding
        urwid.set_encoding("utf-8")

    def tearDown(self) -> None:
        urwid.set_encoding(self.old_encoding)

    def test_001_basic(self):
        font = urwid.Thin3x3Font()
        rendered = b'\n'.join(font.render("1").text).decode()
        expected = ' ┐ \n │ \n ┴ '
        self.assertEqual(expected, rendered)

    def test_002_non_rect(self):
        """Test non rect symbol, which causes spaces based padding.

        Lines as bytes should be not equal length.
        """
        font = urwid.Thin3x3Font()
        rendered = b'\n'.join(font.render("2").text).decode()
        expected = '┌─┐\n┌─┘\n└─ '
        self.assertEqual(expected, rendered)
