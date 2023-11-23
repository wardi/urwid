#!/usr/bin/env python
#
# Urwid setup.py exports the useful bits
#    Copyright (C) 2004-2014  Ian Ward
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

from setuptools import Extension, setup

setup_d = {
    "name": "urwid",
    "ext_modules": [Extension("urwid.str_util", sources=["source/str_util.c"])],
    "url": "https://urwid.org/",
    "test_suite": "urwid.tests",
}

if __name__ == "__main__":
    try:
        setup(**setup_d)
    except (OSError, SystemExit) as e:
        import sys

        if "test" in sys.argv:
            raise
        import traceback

        traceback.print_exc()
        print("Couldn't build the extension module, trying without it...")
        del setup_d["ext_modules"]
        setup(**setup_d)
