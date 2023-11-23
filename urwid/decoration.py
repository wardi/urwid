# Urwid widget decoration classes
#    Copyright (C) 2004-2012  Ian Ward
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

import warnings

from urwid.widget import (
    AttrMap,
    AttrMapError,
    AttrWrap,
    BoxAdapter,
    BoxAdapterError,
    Filler,
    FillerError,
    Padding,
    PaddingError,
    WidgetDecoration,
    WidgetDisable,
    WidgetPlaceholder,
    calculate_top_bottom_filler,
    normalize_valign,
)

__all__ = (
    "AttrMap",
    "AttrMapError",
    "AttrWrap",
    "BoxAdapter",
    "BoxAdapterError",
    "Filler",
    "FillerError",
    "Padding",
    "PaddingError",
    "WidgetDecoration",
    "WidgetDisable",
    "WidgetPlaceholder",
    "calculate_top_bottom_filler",
    "normalize_valign",
)

warnings.warn(
    f"{__name__!r} is not expected to be imported directly. "
    'Please use public access from "urwid" package. '
    f"Module {__name__!r} is deprecated and will be removed in the future.",
    DeprecationWarning,
    stacklevel=3,
)
