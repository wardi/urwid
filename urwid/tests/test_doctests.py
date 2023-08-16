from __future__ import annotations

import doctest
import unittest

import urwid
import urwid.numedit


def load_tests(loader, tests, ignore):
    module_doctests = [
        urwid.wimp,
        urwid.widget.attr_map,
        urwid.widget.attr_wrap,
        urwid.widget.box_adapter,
        urwid.widget.columns,
        urwid.widget.constants,
        urwid.widget.container,
        urwid.widget.divider,
        urwid.widget.edit,
        urwid.widget.filler,
        urwid.widget.frame,
        urwid.widget.grid_flow,
        urwid.widget.overlay,
        urwid.widget.padding,
        urwid.widget.pile,
        urwid.widget.solid_fill,
        urwid.widget.text,
        urwid.widget.widget,
        urwid.widget.widget_decoration,
        urwid.display_common,
        urwid.event_loop.main_loop,
        urwid.numedit,
        urwid.monitored_list,
        urwid.raw_display,
        'urwid.split_repr',  # override function with same name
        urwid.util,
        urwid.signals,
        urwid.graphics,
        ]
    for m in module_doctests:
        tests.addTests(doctest.DocTestSuite(m,
            optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL))
    return tests
