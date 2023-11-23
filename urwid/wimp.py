from __future__ import annotations

import warnings

from urwid.widget import Button, CheckBox, CheckBoxError, PopUpLauncher, PopUpTarget, RadioButton, SelectableIcon

__all__ = (
    "Button",
    "CheckBox",
    "CheckBoxError",
    "PopUpLauncher",
    "PopUpTarget",
    "RadioButton",
    "SelectableIcon",
)

warnings.warn(
    f"{__name__!r} is not expected to be imported directly. "
    'Please use public access from "urwid" package. '
    f"Module {__name__!r} is deprecated and will be removed in the future.",
    DeprecationWarning,
    stacklevel=3,
)
