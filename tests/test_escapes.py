#!/usr/bin/python

""" Tests covering escape sequences processing """

from __future__ import annotations

import unittest

import urwid.escape


class InputEscapeSequenceParserTest(unittest.TestCase):
    """ Tests for parser of input escape sequences """

    def test_bare_escape(self):
        codes = [27]
        expected = ['esc']
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)

    def test_meta(self):
        codes = [27, ord('4'), ord('2')]
        expected = ['meta 4']
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([ord('2')], rest)

    def test_shift_arrows(self):
        codes = [27, ord('['), ord('a')]
        expected = ['shift up']
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)

    def test_ctrl_pgup(self):
        codes = [27, 91, 53, 59, 53, 126]
        expected = ['ctrl page up']
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)

    def test_esc_meta_1(self):
        codes = [27, 27, 49]
        expected = ['esc', 'meta 1']
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)

    def test_midsequence(self):
        # '[11~' is F1, '[12~' is F2, etc
        codes = [27, ord('['), ord('1')]

        with self.assertRaises(urwid.escape.MoreInputRequired):
            urwid.escape.process_keyqueue(codes, more_available=True)

        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(['meta ['], actual)
        self.assertListEqual([ord('1')], rest)

    def test_mouse_press(self):
        codes = [27, 91, 77, 32, 41, 48]
        expected = [('mouse press', 1.0, 8, 15)]
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)

    def test_bug_104(self):
        """ GH #104: click-Esc & Esc-click crashes urwid apps """
        codes = [27, 27, 91, 77, 32, 127, 59]
        expected = ['esc', ('mouse press', 1.0, 94, 26)]
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)

        codes = [27, 27, 91, 77, 35, 120, 59]
        expected = ['esc', ('mouse release', 0, 87, 26)]
        actual, rest = urwid.escape.process_keyqueue(codes, more_available=False)
        self.assertListEqual(expected, actual)
        self.assertListEqual([], rest)
