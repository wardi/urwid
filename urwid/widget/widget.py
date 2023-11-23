# Urwid basic widget classes
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

import functools
import typing
import warnings
from operator import attrgetter

from urwid import signals
from urwid.canvas import CanvasCache, CompositeCanvas
from urwid.command_map import command_map
from urwid.split_repr import split_repr
from urwid.util import MetaSuper

from .constants import Sizing

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable


class WidgetMeta(MetaSuper, signals.MetaSignals):
    """
    Bases: :class:`MetaSuper`, :class:`MetaSignals`

    Automatic caching of render and rows methods.

    Class variable *no_cache* is a list of names of methods to not cache
    automatically.  Valid method names for *no_cache* are ``'render'`` and
    ``'rows'``.

    Class variable *ignore_focus* if defined and set to ``True`` indicates
    that the canvas this widget renders is not affected by the focus
    parameter, so it may be ignored when caching.
    """

    def __init__(cls, name, bases, d):
        no_cache = d.get("no_cache", [])

        super().__init__(name, bases, d)

        if "render" in d:
            if "render" not in no_cache:
                render_fn = cache_widget_render(cls)
            else:
                render_fn = nocache_widget_render(cls)
            cls.render = render_fn

        if "rows" in d and "rows" not in no_cache:
            cls.rows = cache_widget_rows(cls)
        if "no_cache" in d:
            del cls.no_cache
        if "ignore_focus" in d:
            del cls.ignore_focus


class WidgetError(Exception):
    pass


def validate_size(widget, size, canv):
    """
    Raise a WidgetError if a canv does not match size.
    """
    if (size and size[1:] != (0,) and size[0] != canv.cols()) or (len(size) > 1 and size[1] != canv.rows()):
        raise WidgetError(
            f"Widget {widget!r} rendered ({canv.cols():d} x {canv.rows():d}) canvas when passed size {size!r}!"
        )


def cache_widget_render(cls):
    """
    Return a function that wraps the cls.render() method
    and fetches and stores canvases with CanvasCache.
    """
    ignore_focus = bool(getattr(cls, "ignore_focus", False))
    fn = cls.render

    @functools.wraps(fn)
    def cached_render(self, size, focus=False):
        focus = focus and not ignore_focus
        canv = CanvasCache.fetch(self, cls, size, focus)
        if canv:
            return canv

        canv = fn(self, size, focus=focus)
        validate_size(self, size, canv)
        if canv.widget_info:
            canv = CompositeCanvas(canv)
        canv.finalize(self, size, focus)
        CanvasCache.store(cls, canv)
        return canv

    cached_render.original_fn = fn
    return cached_render


def nocache_widget_render(cls):
    """
    Return a function that wraps the cls.render() method
    and finalizes the canvas that it returns.
    """
    fn = cls.render
    if hasattr(fn, "original_fn"):
        fn = fn.original_fn

    @functools.wraps(fn)
    def finalize_render(self, size, focus=False):
        canv = fn(self, size, focus=focus)
        if canv.widget_info:
            canv = CompositeCanvas(canv)
        validate_size(self, size, canv)
        canv.finalize(self, size, focus)
        return canv

    finalize_render.original_fn = fn
    return finalize_render


def nocache_widget_render_instance(self):
    """
    Return a function that wraps the cls.render() method
    and finalizes the canvas that it returns, but does not
    cache the canvas.
    """
    fn = self.render.original_fn

    @functools.wraps(fn)
    def finalize_render(size, focus=False):
        canv = fn(self, size, focus=focus)
        if canv.widget_info:
            canv = CompositeCanvas(canv)
        canv.finalize(self, size, focus)
        return canv

    finalize_render.original_fn = fn
    return finalize_render


def cache_widget_rows(cls):
    """
    Return a function that wraps the cls.rows() method
    and returns rows from the CanvasCache if available.
    """
    ignore_focus = bool(getattr(cls, "ignore_focus", False))
    fn = cls.rows

    @functools.wraps(fn)
    def cached_rows(self, size, focus=False):
        focus = focus and not ignore_focus
        canv = CanvasCache.fetch(self, cls, size, focus)
        if canv:
            return canv.rows()

        return fn(self, size, focus)

    return cached_rows


class Widget(metaclass=WidgetMeta):
    """
    Widget base class

    .. attribute:: _selectable
       :annotation: = False

       The default :meth:`.selectable` method returns this
       value.

    .. attribute:: _sizing
       :annotation: = frozenset(['flow', 'box', 'fixed'])

       The default :meth:`.sizing` method returns this value.

    .. attribute:: _command_map
       :annotation: = urwid.command_map

       A shared :class:`CommandMap` instance. May be redefined
       in subclasses or widget instances.

    .. method:: render(size, focus=False)

       .. note::

          This method is not implemented in :class:`.Widget` but
          must be implemented by any concrete subclass

       :param size: One of the following,
                    *maxcol* and *maxrow* are integers > 0:

                    (*maxcol*, *maxrow*)
                      for box sizing -- the parent chooses the exact
                      size of this widget

                    (*maxcol*,)
                      for flow sizing -- the parent chooses only the
                      number of columns for this widget

                    ()
                      for fixed sizing -- this widget is a fixed size
                      which can't be adjusted by the parent
       :type size: widget size
       :param focus: set to ``True`` if this widget or one of its children
                     is in focus
       :type focus: bool

       :returns: A :class:`Canvas` subclass instance containing the
                 rendered content of this widget

       :class:`Text` widgets return a :class:`TextCanvas` (arbitrary text and
       display attributes), :class:`SolidFill` widgets return a
       :class:`SolidCanvas` (a single character repeated across
       the whole surface) and container widgets return a
       :class:`CompositeCanvas` (one or more other canvases
       arranged arbitrarily).

       If *focus* is ``False``, the returned canvas may not have a cursor
       position set.

       There is some metaclass magic defined in the :class:`Widget`
       metaclass :class:`WidgetMeta` that causes the
       result of this method to be cached by :class:`CanvasCache`.
       Later calls will automatically look up the value in the cache first.

       As a small optimization the class variable :attr:`ignore_focus`
       may be defined and set to ``True`` if this widget renders the same
       canvas regardless of the value of the *focus* parameter.

       Any time the content of a widget changes it should call
       :meth:`_invalidate` to remove any cached canvases, or the widget
       may render the cached canvas instead of creating a new one.


    .. method:: rows(size, focus=False)

       .. note::

          This method is not implemented in :class:`.Widget` but
          must be implemented by any flow widget.  See :meth:`.sizing`.

       See :meth:`Widget.render` for parameter details.

       :returns: The number of rows required for this widget given a number
                 of columns in *size*

       This is the method flow widgets use to communicate their size to other
       widgets without having to render a canvas. This should be a quick
       calculation as this function may be called a number of times in normal
       operation. If your implementation may take a long time you should add
       your own caching here.

       There is some metaclass magic defined in the :class:`Widget`
       metaclass :class:`WidgetMeta` that causes the
       result of this function to be retrieved from any
       canvas cached by :class:`CanvasCache`, so if your widget
       has been rendered you may not receive calls to this function. The class
       variable :attr:`ignore_focus` may be defined and set to ``True`` if this
       widget renders the same size regardless of the value of the *focus*
       parameter.


    .. method:: keypress(size, key)

       .. note::

          This method is not implemented in :class:`.Widget` but
          must be implemented by any selectable widget.
          See :meth:`.selectable`.

       :param size: See :meth:`Widget.render` for details
       :type size: widget size
       :param key: a single keystroke value; see :ref:`keyboard-input`
       :type key: bytes or unicode

       :returns: ``None`` if *key* was handled by this widget or
                 *key* (the same value passed) if *key* was not handled
                 by this widget

       Container widgets will typically call the :meth:`keypress` method on
       whichever of their children is set as the focus.

       The standard widgets use :attr:`_command_map` to
       determine what action should be performed for a given *key*. You may
       modify these values to your liking globally, at some level in the
       widget hierarchy or on individual widgets. See :class:`CommandMap`
       for the defaults.

       In your own widgets you may use whatever logic you like: filtering or
       translating keys, selectively passing along events etc.



    .. method:: mouse_event(size, event, button, col, row, focus)

       .. note::

          This method is not implemented in :class:`.Widget` but
          may be implemented by a subclass.  Not implementing this
          method is equivalent to having a method that always returns
          ``False``.

       :param size: See :meth:`Widget.render` for details.
       :type size: widget size
       :param event: Values such as ``'mouse press'``, ``'ctrl mouse press'``,
                     ``'mouse release'``, ``'meta mouse release'``,
                     ``'mouse drag'``; see :ref:`mouse-input`
       :type event: mouse event
       :param button: 1 through 5 for press events, often 0 for release events
                      (which button was released is often not known)
       :type button: int
       :param col: Column of the event, 0 is the left edge of this widget
       :type col: int
       :param row: Row of the event, 0 it the top row of this widget
       :type row: int
       :param focus: Set to ``True`` if this widget or one of its children
                     is in focus
       :type focus: bool

       :returns: ``True`` if the event was handled by this widget, ``False``
                 otherwise

       Container widgets will typically call the :meth:`mouse_event` method on
       whichever of their children is at the position (*col*, *row*).


    .. method:: get_cursor_coords(size)

       .. note::

          This method is not implemented in :class:`.Widget` but
          must be implemented by any widget that may return cursor
          coordinates as part of the canvas that :meth:`render` returns.

       :param size: See :meth:`Widget.render` for details.
       :type size: widget size

       :returns: (*col*, *row*) if this widget has a cursor, ``None`` otherwise

       Return the cursor coordinates (*col*, *row*) of a cursor that will appear
       as part of the canvas rendered by this widget when in focus, or ``None``
       if no cursor is displayed.

       The :class:`ListBox` widget
       uses this method to make sure a cursor in the focus widget is not
       scrolled out of view.  It is a separate method to avoid having to render
       the whole widget while calculating layout.

       Container widgets will typically call the :meth:`.get_cursor_coords`
       method on their focus widget.


    .. method:: get_pref_col(size)

       .. note::

          This method is not implemented in :class:`.Widget` but
          may be implemented by a subclass.

       :param size: See :meth:`Widget.render` for details.
       :type size: widget size

       :returns: a column number or ``'left'`` for the leftmost available
                 column or ``'right'`` for the rightmost available column

       Return the preferred column for the cursor to be displayed in this
       widget. This value might not be the same as the column returned from
       :meth:`get_cursor_coords`.

       The :class:`ListBox` and :class:`Pile`
       widgets call this method on a widget losing focus and use the value
       returned to call :meth:`.move_cursor_to_coords` on the widget becoming
       the focus. This allows the focus to move up and down through widgets
       while keeping the cursor in approximately the same column on screen.


    .. method:: move_cursor_to_coords(size, col, row)

       .. note::

          This method is not implemented in :class:`.Widget` but
          may be implemented by a subclass.  Not implementing this
          method is equivalent to having a method that always returns
          ``False``.

       :param size: See :meth:`Widget.render` for details.
       :type size: widget size
       :param col: new column for the cursor, 0 is the left edge of this widget
       :type col: int
       :param row: new row for the cursor, 0 it the top row of this widget
       :type row: int

       :returns: ``True`` if the position was set successfully anywhere on
                 *row*, ``False`` otherwise
    """

    _selectable = False
    _sizing = frozenset([Sizing.FLOW, Sizing.BOX, Sizing.FIXED])
    _command_map = command_map

    def _invalidate(self) -> None:
        """
        Mark cached canvases rendered by this widget as dirty so that
        they will not be used again.
        """
        CanvasCache.invalidate(self)

    def _emit(self, name: Hashable, *args):
        """
        Convenience function to emit signals with self as first
        argument.
        """
        signals.emit_signal(self, name, self, *args)

    def selectable(self):
        """
        :returns: ``True`` if this is a widget that is designed to take the
                  focus, i.e. it contains something the user might want to
                  interact with, ``False`` otherwise,

        This default implementation returns :attr:`._selectable`.
        Subclasses may leave these is if the are not selectable,
        or if they are always selectable they may
        set the :attr:`_selectable` class variable to ``True``.

        If this method returns ``True`` then the :meth:`.keypress` method
        must be implemented.

        Returning ``False`` does not guarantee that this widget will never be in
        focus, only that this widget will usually be skipped over when changing
        focus. It is still possible for non selectable widgets to have the focus
        (typically when there are no other selectable widgets visible).
        """
        return self._selectable

    def sizing(self):
        """
        :returns: A frozenset including one or more of ``'box'``, ``'flow'`` and
                  ``'fixed'``.  Default implementation returns the value of
                  :attr:`._sizing`, which for this class includes all three.

        The sizing modes returned indicate the modes that may be
        supported by this widget, but is not sufficient to know
        that using that sizing mode will work.  Subclasses should
        make an effort to remove sizing modes they know will not
        work given the state of the widget, but many do not yet
        do this.

        If a sizing mode is missing from the set then the widget
        should fail when used in that mode.

        If ``'flow'`` is among the values returned then the other
        methods in this widget must be able to accept a
        single-element tuple (*maxcol*,) to their ``size``
        parameter, and the :meth:`rows` method must be defined.

        If ``'box'`` is among the values returned then the other
        methods must be able to accept a two-element tuple
        (*maxcol*, *maxrow*) to their size parameter.

        If ``'fixed'`` is among the values returned then the other
        methods must be able to accept an empty tuple () to
        their size parameter, and the :meth:`pack` method must
        be defined.
        """
        return self._sizing

    def pack(self, size: tuple[()] | tuple[int] | tuple[int, int], focus: bool = False) -> tuple[int, int]:
        """
        See :meth:`Widget.render` for parameter details.

        :returns: A "packed" size (*maxcol*, *maxrow*) for this widget

        Calculate and return a minimum
        size where all content could still be displayed. Fixed widgets must
        implement this method and return their size when ``()`` is passed as the
        *size* parameter.

        This default implementation returns the *size* passed, or the *maxcol*
        passed and the value of :meth:`rows` as the *maxrow* when (*maxcol*,)
        is passed as the *size* parameter.

        .. note::

           This is a new method that hasn't been fully implemented across the
           standard widget types. In particular it has not yet been
           implemented for container widgets.

        :class:`Text` widgets have implemented this method.
        You can use :meth:`Text.pack` to calculate the minimum
        columns and rows required to display a text widget without wrapping,
        or call it iteratively to calculate the minimum number of columns
        required to display the text wrapped into a target number of rows.
        """
        if not size:
            if Sizing.FIXED in self.sizing():
                raise NotImplementedError("Fixed widgets must override Widget.pack()")
            raise WidgetError(f"Cannot pack () size, this is not a fixed widget: {self!r}")

        if len(size) == 1:
            if Sizing.FLOW in self.sizing():
                return (*size, self.rows(size, focus))

            raise WidgetError(f"Cannot pack (maxcol,) size, this is not a flow widget: {self!r}")

        return size

    @property
    def base_widget(self) -> Widget:
        """
        Read-only property that steps through decoration widgets
        and returns the one at the base.  This default implementation
        returns self.
        """
        return self

    @property
    def focus(self) -> Widget | None:
        """
        Read-only property returning the child widget in focus for
        container widgets.  This default implementation
        always returns ``None``, indicating that this widget has no children.
        """
        return None

    def _not_a_container(self, val=None):
        raise IndexError(f"No focus_position, {self!r} is not a container widget")

    focus_position = property(
        _not_a_container,
        _not_a_container,
        doc="""
        Property for reading and setting the focus position for
        container widgets. This default implementation raises
        :exc:`IndexError`, making normal widgets fail the same way
        accessing :attr:`.focus_position` on an empty container widget would.
        """,
    )

    def __repr__(self):
        """
        A friendly __repr__ for widgets, designed to be extended
        by subclasses with _repr_words and _repr_attr methods.
        """
        return split_repr(self)

    def _repr_words(self):
        words = []
        if self.selectable():
            words = ["selectable", *words]
        if self.sizing() and self.sizing() != frozenset([Sizing.FLOW, Sizing.BOX, Sizing.FIXED]):
            words.append("/".join(sorted(self.sizing())))
        return [*words, "widget"]

    def _repr_attrs(self):
        return {}


class FlowWidget(Widget):
    """
    Deprecated.  Inherit from Widget and add:

        _sizing = frozenset(['flow'])

    at the top of your class definition instead.

    Base class of widgets that determine their rows from the number of
    columns available.
    """

    _sizing = frozenset([Sizing.FLOW])

    def __init__(self, *args, **kwargs):
        warnings.warn(
            """
            FlowWidget is deprecated. Inherit from Widget and add:

                _sizing = frozenset(['flow'])

            at the top of your class definition instead.""",
            DeprecationWarning,
            stacklevel=3,
        )

    def rows(self, size: int, focus: bool = False) -> int:
        """
        All flow widgets must implement this function.
        """
        raise NotImplementedError()

    def render(self, size: tuple[int], focus: bool = False):
        """
        All widgets must implement this function.
        """
        raise NotImplementedError()


class BoxWidget(Widget):
    """
    Deprecated.  Inherit from Widget and add:

        _sizing = frozenset(['box'])
        _selectable = True

    at the top of your class definition instead.

    Base class of width and height constrained widgets such as
    the top level widget attached to the display object
    """

    _selectable = True
    _sizing = frozenset([Sizing.BOX])

    def __init__(self, *args, **kwargs):
        warnings.warn(
            """
            BoxWidget is deprecated. Inherit from Widget and add:

                _sizing = frozenset(['box'])
                _selectable = True

            at the top of your class definition instead.""",
            DeprecationWarning,
            stacklevel=3,
        )

    def render(self, size: tuple[int, int], focus: bool = False):
        """
        All widgets must implement this function.
        """
        raise NotImplementedError()


def fixed_size(size):
    """
    raise ValueError if size != ().

    Used by FixedWidgets to test size parameter.
    """
    if size != ():
        raise ValueError(f"FixedWidget takes only () for size.passed: {size!r}")


class FixedWidget(Widget):
    """
    Deprecated.  Inherit from Widget and add:

        _sizing = frozenset(['fixed'])

    at the top of your class definition instead.

    Base class of widgets that know their width and height and
    cannot be resized
    """

    _sizing = frozenset([Sizing.FIXED])

    def __init__(self, *args, **kwargs):
        warnings.warn(
            """
            FixedWidget is deprecated. Inherit from Widget and add:

                _sizing = frozenset(['fixed'])

            at the top of your class definition instead.""",
            DeprecationWarning,
            stacklevel=3,
        )

    def render(self, size, focus=False):
        """
        All widgets must implement this function.
        """
        raise NotImplementedError()

    def pack(self, size=None, focus=False):
        """
        All fixed widgets must implement this function.
        """
        raise NotImplementedError()


def delegate_to_widget_mixin(attribute_name: str):
    """
    Return a mixin class that delegates all standard widget methods
    to an attribute given by attribute_name.

    This mixin is designed to be used as a superclass of another widget.
    """
    # FIXME: this is so common, let's add proper support for it
    # when layout and rendering are separated

    get_delegate = attrgetter(attribute_name)

    class DelegateToWidgetMixin(Widget):
        no_cache: typing.ClassVar[list[str]] = ["rows"]  # crufty metaclass work-around

        def render(self, size, focus: bool = False) -> CompositeCanvas:
            canv = get_delegate(self).render(size, focus=focus)
            return CompositeCanvas(canv)

        @property
        def selectable(self) -> Callable[[], bool]:
            return get_delegate(self).selectable

        @property
        def get_cursor_coords(self):
            return get_delegate(self).get_cursor_coords

        @property
        def get_pref_col(self):
            return get_delegate(self).get_pref_col

        @property
        def keypress(self):
            return get_delegate(self).keypress

        @property
        def move_cursor_to_coords(self):
            return get_delegate(self).move_cursor_to_coords

        @property
        def rows(self):
            return get_delegate(self).rows

        @property
        def mouse_event(
            self,
        ) -> Callable[[tuple[()] | tuple[int] | tuple[int, int], str, int, int, int, bool], bool | None,]:
            return get_delegate(self).mouse_event

        @property
        def sizing(self):
            return get_delegate(self).sizing

        @property
        def pack(self):
            return get_delegate(self).pack

    return DelegateToWidgetMixin


class WidgetWrapError(Exception):
    pass


class WidgetWrap(delegate_to_widget_mixin("_wrapped_widget"), Widget):
    def __init__(self, w: Widget):
        """
        w -- widget to wrap, stored as self._w

        This object will pass the functions defined in Widget interface
        definition to self._w.

        The purpose of this widget is to provide a base class for
        widgets that compose other widgets for their display and
        behaviour.  The details of that composition should not affect
        users of the subclass.  The subclass may decide to expose some
        of the wrapped widgets by behaving like a ContainerWidget or
        WidgetDecoration, or it may hide them from outside access.
        """
        self._wrapped_widget = w

    @property
    def _w(self) -> Widget:
        return self._wrapped_widget

    @_w.setter
    def _w(self, new_widget: Widget) -> None:
        """
        Change the wrapped widget.  This is meant to be called
        only by subclasses.

        >>> size = (10,)
        >>> ww = WidgetWrap(Edit("hello? ","hi"))
        >>> ww.render(size).text # ... = b in Python 3
        [...'hello? hi ']
        >>> ww.selectable()
        True
        >>> ww._w = Text("goodbye") # calls _set_w()
        >>> ww.render(size).text
        [...'goodbye   ']
        >>> ww.selectable()
        False
        """
        self._wrapped_widget = new_widget
        self._invalidate()

    def _set_w(self, w):
        """
        Change the wrapped widget.  This is meant to be called
        only by subclasses.
        >>> from urwid import Edit, Text
        >>> size = (10,)
        >>> ww = WidgetWrap(Edit("hello? ","hi"))
        >>> ww.render(size).text # ... = b in Python 3
        [...'hello? hi ']
        >>> ww.selectable()
        True
        >>> ww._w = Text("goodbye") # calls _set_w()
        >>> ww.render(size).text
        [...'goodbye   ']
        >>> ww.selectable()
        False
        """
        warnings.warn(
            "_set_w is deprecated. Please use 'WidgetWrap._w' property directly",
            DeprecationWarning,
            stacklevel=2,
        )
        self._wrapped_widget = w
        self._invalidate()


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
