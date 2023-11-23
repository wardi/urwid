# Urwid __init__.py - all the stuff you're likely to care about
#
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

from urwid import raw_display
from urwid.canvas import (
    BlankCanvas,
    Canvas,
    CanvasCache,
    CanvasCombine,
    CanvasError,
    CanvasJoin,
    CanvasOverlay,
    CompositeCanvas,
    SolidCanvas,
    TextCanvas,
)
from urwid.command_map import (
    ACTIVATE,
    CURSOR_DOWN,
    CURSOR_LEFT,
    CURSOR_MAX_LEFT,
    CURSOR_MAX_RIGHT,
    CURSOR_PAGE_DOWN,
    CURSOR_PAGE_UP,
    CURSOR_RIGHT,
    CURSOR_UP,
    REDRAW_SCREEN,
    CommandMap,
    command_map,
)
from urwid.display_common import (
    BLACK,
    BROWN,
    DARK_BLUE,
    DARK_CYAN,
    DARK_GRAY,
    DARK_GREEN,
    DARK_MAGENTA,
    DARK_RED,
    DEFAULT,
    LIGHT_BLUE,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_MAGENTA,
    LIGHT_RED,
    UPDATE_PALETTE_ENTRY,
    WHITE,
    YELLOW,
    AttrSpec,
    AttrSpecError,
    BaseScreen,
    RealTerminal,
    ScreenError,
)
from urwid.event_loop import AsyncioEventLoop, EventLoop, ExitMainLoop, MainLoop, SelectEventLoop
from urwid.font import (
    Font,
    FontRegistry,
    HalfBlock5x4Font,
    HalfBlock6x5Font,
    HalfBlock7x7Font,
    HalfBlockHeavy6x5Font,
    Sextant2x2Font,
    Sextant3x3Font,
    Thin3x3Font,
    Thin4x3Font,
    Thin6x6Font,
    get_all_fonts,
)
from urwid.listbox import ListBox, ListBoxError, ListWalker, ListWalkerError, SimpleFocusListWalker, SimpleListWalker
from urwid.monitored_list import MonitoredFocusList, MonitoredList
from urwid.signals import MetaSignals, Signals, connect_signal, disconnect_signal, emit_signal, register_signal
from urwid.text_layout import LayoutSegment, StandardTextLayout, TextLayout, default_layout
from urwid.util import (
    MetaSuper,
    TagMarkupException,
    apply_target_encoding,
    calc_text_pos,
    calc_trim_text,
    calc_width,
    decompose_tagmarkup,
    detected_encoding,
    get_encoding_mode,
    int_scale,
    is_mouse_event,
    is_wide_char,
    move_next_char,
    move_prev_char,
    set_encoding,
    supports_unicode,
    within_double_byte,
)
from urwid.version import version as __version__
from urwid.version import version_tuple as __version_tuple__
from urwid.vterm import TermCanvas, TermCharset, Terminal, TermModes, TermScroller
from urwid.widget import (
    ANY,
    BOTTOM,
    BOX,
    CENTER,
    CLIP,
    ELLIPSIS,
    FIXED,
    FLOW,
    GIVEN,
    LEFT,
    MIDDLE,
    PACK,
    RELATIVE,
    RELATIVE_100,
    RIGHT,
    SPACE,
    TOP,
    WEIGHT,
    Align,
    AttrMap,
    AttrMapError,
    AttrWrap,
    BarGraph,
    BarGraphError,
    BarGraphMeta,
    BigText,
    BoxAdapter,
    BoxAdapterError,
    BoxWidget,
    Button,
    CheckBox,
    CheckBoxError,
    Columns,
    ColumnsError,
    Divider,
    Edit,
    EditError,
    Filler,
    FillerError,
    FixedWidget,
    FlowWidget,
    Frame,
    FrameError,
    GraphVScale,
    GridFlow,
    GridFlowError,
    IntEdit,
    LineBox,
    Overlay,
    OverlayError,
    Padding,
    PaddingError,
    Pile,
    PileError,
    PopUpLauncher,
    PopUpTarget,
    ProgressBar,
    RadioButton,
    SelectableIcon,
    Sizing,
    SolidFill,
    Text,
    TextError,
    VAlign,
    WHSettings,
    Widget,
    WidgetContainerMixin,
    WidgetDecoration,
    WidgetDisable,
    WidgetError,
    WidgetMeta,
    WidgetPlaceholder,
    WidgetWrap,
    WidgetWrapError,
    WrapMode,
    delegate_to_widget_mixin,
    fixed_size,
    scale_bar_values,
)

from . import event_loop, widget

from urwid.treetools import ParentNode, TreeListBox, TreeNode, TreeWalker, TreeWidget, TreeWidgetError  # isort: skip

# Optional event loops with external dependencies

try:
    from urwid.event_loop import TornadoEventLoop
except ImportError:
    pass

try:
    from urwid.event_loop import GLibEventLoop
except ImportError:
    pass

try:
    from urwid.event_loop import TwistedEventLoop
except ImportError:
    pass

try:
    from urwid.event_loop import TrioEventLoop
except ImportError:
    pass

try:
    from urwid.event_loop import ZMQEventLoop
except ImportError:
    pass

# Backward compatibility
VERSION = __version_tuple__
