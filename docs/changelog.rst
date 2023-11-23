
Changelog
---------

.. changelog::
    :changelog-url: https://urwid.org/changelog.html
    :github: https://github.com/urwid/urwid/releases/
    :pypi: https://pypi.org/project/urwid/

Urwid 2.1.2
===========

2020-09-26

 * Add pack method to LineBox. Fixes: #346 (by Miguel de Dios)

 * Add a test to check the linebox.pack is good. (by Miguel de Dios)

 * Add bin/release.sh script to partially automate releases. (by Tony Cebzanov)

 * Add workaround for #386 (by Tony Cebzanov)

 * Fix curses_display python3 ord() (by Ya-Liang Chang (Allen))

 * Fix bumping to dev version in release.sh script (by Tony Cebzanov)

 * Fix focus_end on a collapsed tree (by Anonymous Maarten)

 * Fix crash with "ellipsis" clipping for py2 tour.py works with py2 now Typo in
   tour.py (by akorb)

 * Ignore resetting to invalid locale (Closes: #377) (by Jochen Sprickerhof)

 * Use ord2 for python2/3 compatibility (by Ya-Liang Chang (Allen))


Urwid 2.1.1
===========

2020-07-26

 * Add TrioEventLoop.run_async(), removed nursery constructor arg (#392) (by
   Tamás Nepusz)

 * Add py38 to Travis tests (by Andrey Semakin)

 * Add popular IDEs folders to .gitignore (by Andrey Semakin)

 * Add wrap_around kwarg to SimpleListWalkers (by Krzysztof Królczyk)

 * Change documentation on Terminal (by James Johnson)

 * Remove debug documentation change test (by James Johnson)

 * Remove support for py34 (by Andrey Semakin)

 * Remove invalid escape sequence (by Andrey Lebedev)

 * Fix GridFlow keypress handling when v_sep is 0 (by Aurelien Grenotton)

 * Fix Terminal in ListBox (#382) (by James Johnson)

 * Fix Crash on `fg`, SIGCONT (after Ctrl-Z, SIGSTOP, SIGTSTP) (by goncalopp)

 * Fix 256-color mode on some terminals. Addresses #404. (by Tony Cebzanov)

 * vterm: reduce __init__ boilerplate (by max ulidtko)

 * vterm: errno 5 is not EOF. (by max ulidtko)

 * Terminal: use UTF-8 by default. (by max ulidtko)

 * Instance of Terminal has no __super attr -- thanks pylint! (by max ulidtko)

 * Do not call wait_readable with a closed fd in TrioEventLoop (by Michael
   Hudson-Doyle)

 * Make options a static method where applicable (by Philip Matura)

 * Set up Travis to run py38, speed up build (by Andrey Semakin)
 
 * Use comparison with a string instead of "is" test with a literal (by Andrej
   Shadura)


Urwid 2.1.0
===========

2019-11-13

 * Add support for Python 3.7 and 3.8, drop support for Python 3.3

 * Add 24-bit (true color) support. (by Tony Cebzanov)

 * Add TrioEventLoop (by Tamas Nepusz)

 * Add support for input encoding in Terminal widget (by Tamas Nepusz)

 * Add ability to specify LineBox title attribute (by Tom Pickering)

 * Add custom checkbox symbol (by Krzysztof Królczyk)

 * Add installation instruction to README (by Patryk Niedźwiedziński)

 * Remove PollingListWalker class (by Heiko Noordhof)

 * Change SelectableIcon default cursor_position to 0. (by Werner Beroux)

 * Extended numerical editing: integers and floats (by hootnot)

 * Re-raise coroutine exceptions in AsyncioEventLoop properly (by nocarryr)

 * Fixed locale issue (by Andrew Dunai)

 * Gate SIGWINCH behind GLib 2.54+ (by Nick Chavez)

 * Remove method Text._calc_line_translation() (by rndusr)

 * Fix colon in HalfBlock5x4Font (by Alex Ozer)

 * Don't use deprecated inspect.getargspec() with python3 (by rndusr)

 * Fix issue "Non-integer division in bargraph when using set_bar_width(1)"
   (by Carlos Jenkins)

 * Fix misleading indentation in Screen._stop() (by Akos Kiss)

 * Fix crash on click-Esc & Esc-click (by Maxim Ivanov)

 * Use 'TimerHandle.cancelled()' if available (by Mohamed Seleem)

 * Break rather than raising exception on shard calculation bug. (by Tony
   Cebzanov)

 * Increase _idle_emulation_delay. (by Tony Cebzanov)

 * Fix EOF detection for the Terminal widget on Python 3 (by Tamas Nepusz)

 * Fix the asyncio example, and make the raw Screen work without real files (by
   Eevee)

 * Unbreak python ./examples/treesample HOME END keys. (by Dimitri John Ledkov)

 * Urwid.util: Fix bug in rle_append_beginning_modify (by BkPHcgQL3V)

 * Fix AttributeError on mouse click (by mbarkhau)

 * Fix ProgressBar smoothing on Python 3.x (by Tamas Nepusz)

 * Fix asyncio event loop test on py3.4 (by Maxim Ivanov)

 * Handle case where MainLoop._topmost_widget does not implement mouse_event (by
   Rasmus Bondesson)

 * Implement `ellipsis` wrapping mode for StandardTextLayout (by Philip Matura)

 * Fix .pack call in Columns.column_widths (by Philip Matura)

 * Use ._selectable member for Edit widget (by Philip Matura)

 * Fix use of ignore_focus, for widgets inheriting from Text (by Philip Matura)

 * Remove some special handling for TreeListBox (by Philip Matura)

 * Make Columns and Pile selectable when any child widget is (by Philip Matura)

 * Implement get_cursor_coords for Frame widget (by Philip Matura)

 * Fix Frame mouse_event when footer is trimmed (by Philip Matura)

 * Fix Python 3.8 SyntaxWarning: 'str' object is not callable (by Anders Kaseorg)

 * README: Use SVG build status badge (by Olle Jonsson)


Urwid 2.0.1
===========

2018-01-21

 * #275: Late fix for proper exception reraising from within main loop
   (by Andrew Dunai & Adam Sampson)

Urwid 2.0.0
===========

2018-01-17

 * Full Python 2.x/3.x support (by Andrew Dunai)

 * Proper handling & customization of OS signals by GLib event loop
   (by Federico T)

 * vterm: Fix handling of NUL characters (by aszlig)

 * Add 256-color support for fbterm (by Benjamin Yates)

 * Italics support (by Ian D. Scott)

 * Store envron's TERM value as a Screen attribute (by Benjamin Yates)

 * Replaced hashbangs to use proper Python binary (by Douglas La Rocca)

 * Post-change signal for Edit, CheckBox and RadioButton widgets
   (by Toshio Kuratomi)

 * ListBox.body update (by Random User)

 * SimpleListWalker is now default when setting ListBox.body (by Random User)

 * #246, #234: SelectEventLoop alarm improvements (by Dave Jones)

 * #211: Title align & borderless sides for LineBox (by Toshio Kuratomi)

 * Support for 'home' and 'end' keys in ListBox (by Random User)

 * Various code cleanups (by Jordan Speicher, Marin Atanasov Nikolov)

 * CI fixes (by Marlox, Ian Ward, Anatoly Techtonik, Tony Cebzanov &
   Ondřej Súkup)

 * Example fixes (by Kenneth Nielsen)

 * Documentation fixes (by anatoly techtonik, Marcin Kurczewski, mobyte0,
   Christian Geier & xndcn)

 * Code cleanup & typo fixes (by Jakub Wilk & Boris Feld)

 * Integration of tox for easier Python cross-version testing (by Andrew Dunai)

 * Test fixes (by Michael Hudson-Doyle, Mike Gilbert & Andrew Dunai)

 * Correct error messages in Decoration (by Marcin Kurczewski)

 * #141: Fix for StandardTextLayout.calculate_text_segments
   (by Grzegorz Aksamit)

 * #221: Fix for raw display should release file descriptors (by Alain Leufroy)

 * #261: Fix issues with unicode characters in ProgressBar (by Andrew Dunai)

 * Fix for 'page up' and 'page down' in ListBox when having focusable children
   (by Random User)

 * Fixes for examples compatibility with Python 3 (by Lars Kellogg-Stedman)

 * Fix default screen size on raw display (by Andreas Klöckner)

 * Fix underlining for padded text (by Random User)

 * Fix for terminal widget crash with Python 3 (by Sjc1000)

 * Fix for string formatting error (by Jakub Wilk)

 * Fix for iterator in WidgetContainerListContentsMixin (by Marlox)

 * Fix for missing `modified` signal in SimpleFocusListWalker
   (by Michael Hansen)

 * Dropped Python 3.2 support

 * Test coverage is now collected

Urwid 1.3.1
===========

2015-11-01

 * Fix for screen not getting reset on exception regression
   (by Rian Hunter)

 * AttrSpec objects are now comparable (by Random User)

 * MonitoredList now has a clear method if list has a clear method
   (by neumond)

 * Fix for BarGraph hlines sort order (by Heiko Noordhof)

 * Fix for final output not appearing on exit with some terminals
   now that extra newline was removed (by Jared Winborne)

 * Fix for a resizing bug in raw_display (by Esteban null)

Urwid 1.3.0
===========

2014-10-17

 * New AsyncioEventLoop for Python 3.4, Python 3.x with asyncio
   package or Python 2 with trollius package (by Alex Munroe,
   Jonas Wielicki, with earlier work by Kelketek Rritaa)

 * Screen classes now call back to MainLoop using event loop alarms
   instead of passing timeout values to MainLoop (by Alex Munroe)

 * Add support for bright backgrounds on linux console
   (by Russell Warren)

 * Allow custom sorting of MonitoredList (by Tony Cebzanov)

 * Fix support for negative indexes with MonitoredFocusList
   (by Heiko Noordhof)

 * Documentation fixes (by Ismail, Matthew Mosesohn)

 * SelectableIcon using cursor_position=0 by default instead of 1.

Urwid 1.2.2
===========

2014-10-05

 * Fix for a serious raw_display performance regression
   (by Anton Khirnov)

 * Fix for high color palette detection (by extempo)

 * Small changes to enable windows support (by Jeanpierre Devin)


Urwid 1.2.1
===========

2014-04-04

 * Fix false failures of event loop tests

 * Remove extra newline generated on exit of raw_display

 * Documentation fixes (by Paul Ivanov)


Urwid 1.2.0
===========

2014-02-09

 * Add support for PyPy, drop support for Python 2.4, 2.5

 * Signals now support using weakly referenced arguments to help
   avoid leaking objects when a signal consumer is no longer
   referenced (by Matthijs Kooijman)

 * Add TornadoEventLoop class (by Alexander Glyzov)

 * Update GlibEventLoop to use python-gi for Python3 compatibility
   (by Israel Garcia)

 * Automate testing with Python 2.6, 2.7, 3.2, 3.3 and PyPy using
   travis-ci

 * New container method get_focus_widgets() (by Matthijs Kooijman)

 * Add support for double and triple click mouse events
   (by Igor Kotrasiński)

 * Allow disabling and re-enabling of mouse tracking
   (by Jim Garrison)

 * Create section in docs for example program screenshots generated
   as images like the tutorial examples

 * Add suggested basic color combination images to manual

 * Fall back to 80x24 if screen size detection fails

 * Fix screen.stop(), screen.start() disabling mouse events

 * Fix to make GridFlow v_sep argument behave as documented

 * Fix for registering high palette entries in the form "hX" where
   X > 15 so that basic colors are applied in 88-color mode

 * Fix for raw_display clear-right escape not working with
   standout attribute on some terminals

 * Fix for Terminal widget select loop: retry when interrupted


Urwid 1.1.2
===========

2013-12-30

 * Move to urwid.org and use sphinx docs for generating whole site,
   move changelog to docs/changelog.rst

 * Fix encoding exceptions when unicode used on non-UTF-8 terminal

 * Fix for suspend and resume applications with ^Z

 * Fix for tmux and screen missing colors on right bug

 * Fix Pile zero-weighted items and mouse_event when empty

 * Fix Terminal select() not retrying when interrupted by signal

 * Fix for Padding.align and width change not invalidating


Urwid 1.1.1
===========

2012-11-15

 * Fix for Pile not changing focus on mouse events

 * Fix for Overlay.get_cursor_coords()


Urwid 1.1.0
===========

2012-10-23

 * New common container API: focus, focus_position, contents,
   options(), get_focus_path(), set_focus_path(), __getitem__,
   __iter__(), __reversed__() implemented across all included
   container widgets

   A full description doesn't fit here, see the Container Widgets
   section in the manual for details

 * New Sphinx-based documentation now included in source:
   Tutorial rewritten, manual revised and new reference based
   on updated docstrings (by Marco Giusti, Patrick Totzke)

 * New list walker SimpleFocusListWalker like SimpleListWalker but
   updates focus position as items are inserted or removed

 * New decoration widget WidgetDisable to disable interaction
   with the widgets it wraps

 * SelectableIcon selectable text widget used by button widgets is
   now documented (available since 0.9.9)

 * Columns widget now tries to keep column in focus visible, hiding
   columns on the left when necessary

 * Padding widget now defaults to ('relative', 100) instead of
   'pack' so that left and right parameters are more useful and more
   child widgets are supported

 * New list walker "API Version 2" that is simpler for many list
   walker uses; "API Version 1" will still continue to be supported

 * List walkers may now allow iteration from the absolute top or
   bottom of the list if they provide a positions() method

 * raw_display now erases to the end of the line with EL escape
   sequence to improve copy+paste behavior for some terminals

 * Filler now has top and bottom parameters like Padding's left and
   right parameters and accepts 'pack' instead of None as a height
   value for widgets that calculate their own number of rows

 * Pile and Columns now accepts 'pack' instead of 'flow' for widgets
   that calculate their own number of rows or columns

 * Pile and Columns now accept 'given' instead of 'fixed' for
   cases where the number of rows or columns are specified by the
   container options

 * Pile and Columns widgets now accept any iterable to their
   __init__() methods

 * Widget now has a default focus_position property that raises
   an IndexError when read to be consistent with new common container
   API

 * GridFlow now supports multiple cell widths within the same widget

 * BoxWidget, FlowWidget and FixedWidget are deprecated, instead
   use the sizing() function or _sizing attribute to specify the
   supported sizing modes for your custom widgets

 * Some new shift+arrow and numpad input sequences from RXVT and
   xterm are now recognized

 * Fix for alarms when used with a screen event loop (e.g.
   curses_display)

 * Fix for raw_display when terminal width is 1 column

 * Fixes for a Columns.get_cursor_coords() regression and a
   SelectableIcon.get_cursor_coords() bug

 * Fixes for incorrect handling of box columns in a number of
   Columns methods when that column is selectable

 * Fix for Terminal widget input handling with Python 3


Urwid 1.0.3
===========

2012-11-15

 * Fix for alarms when used with a screen event loop (e.g.
   curses_display)

 * Fix for Overlay.get_cursor_coords()


Urwid 1.0.2
===========

2012-07-13

 * Fix for bug when entering Unicode text into Edit widget with
   bytes caption

 * Fix a regression when not running in UTF-8 mode

 * Fix for a MainLoop.remove_watch_pipe() bug

 * Fix for a bug when packing empty Edit widgets

 * Fix for a ListBox "contents too long" error with very large
   Edit widgets

 * Prevent ListBoxes from selecting 0-height selectable widgets
   when moving up or down

 * Fix a number of bugs caused by 0-height widgets in a ListBox


Urwid 1.0.1
===========

2011-11-28

 * Fix for Terminal widget in BSD/OSX

 * Fix for a Filler mouse_event() position bug

 * Fix support for mouse positions up to x=255, y=255

 * Fixes for a number of string encoding issues under Python 3

 * Fix for a LineBox border __init__() parameters

 * Fix input of UTF-8 in tour.py example by converting captions
   to unicode

 * Fix tutorial examples' use of TextCanvas and switch to using
   unicode literals

 * Prevent raw_display from calling tcseattr() or tcgetattr() on
   non-ttys

 * Disable curses_display external event loop support: screen resizing
   and gpm events are not properly supported

 * Mark PollingListWalker as deprecated


Urwid 1.0.0
===========

2011-09-22

 * New support for Python 3.2 from the same 2.x code base,
   requires distribute instead of setuptools (by Kirk McDonald,
   Wendell, Marien Zwart) everything except TwistedEventLoop and
   GLibEventLoop is supported

 * New experimental Terminal widget with xterm emulation and
   terminal.py example program (by aszlig)

 * Edit widget now supports a mask (for passwords), has an
   insert_text_result() method for full-field validation and
   normalizes input text to Unicode or bytes based on the caption
   type used

 * New TreeWidget, TreeNode, ParentNode, TreeWalker
   and TreeListBox classes for lazy expanding/collapsing tree
   views factored out of browse.py example program, with new
   treesample.py example program (by Rob Lanphier)

 * MainLoop now calls draw_screen() just before going idle, so extra
   calls to draw_screen() in user code may now be removed

 * New MainLoop.watch_pipe() method for subprocess or threaded
   communication with the process/thread updating the UI, and new
   subproc.py example demonstrating its use

 * New PopUpLauncher and PopUpTarget widgets and MainLoop option
   for creating pop-ups and drop-downs, and new pop_up.py example
   program

 * New twisted_serve_ssh.py example (by Ali Afshar) that serves
   multiple displays over ssh from the same application using
   Twisted and the TwistedEventLoop

 * ListBox now includes a get_cursor_coords() method, allowing
   nested ListBox widgets

 * Columns widget contents may now be marked to always be treated
   as flow widgets for mixing flow and box widgets more easily

 * New lcd_display module with support for CF635 USB LCD panel and
   lcd_cf635.py example program with menus, slider controls and a custom
   font

 * Shared command_map instance is now stored as Widget._command_map
   class attribute and may be overridden in subclasses or individual
   widgets for more control over special keystrokes

 * Overlay widget parameters may now be adjusted after creation with
   set_overlay_parameters() method

 * New WidgetPlaceholder widget useful for swapping widgets without
   having to manipulate a container widget's contents

 * LineBox widgets may now include title text

 * ProgressBar text content and alignment may now be overridden

 * Use reactor.stop() in TwistedEventLoop and document that Twisted's
   reactor is not designed to be stopped then restarted

 * curses_display now supports AttrSpec and external event loops
   (Twisted or GLib) just like raw_display

 * raw_display and curses_display now support the IBMPC character
   set (currently only used by Terminal widget)

 * Fix for a gpm_mev bug preventing user input when on the console

 * Fix for leaks of None objects in str_util extension

 * Fix for WidgetWrap and AttrMap not working with fixed widgets

 * Fix for a lock up when attempting to wrap text containing wide
   characters into a single character column


Urwid 0.9.9.2
=============

2011-07-13

 * Fix for an Overlay get_cursor_coords(), and Text top-widget bug

 * Fix for a Padding rows() bug when used with width=PACK

 * Fix for a bug with large flow widgets used in an Overlay

 * Fix for a gpm_mev bug

 * Fix for Pile and GraphVScale when rendered with no contents

 * Fix for a Python 2.3 incompatibility (0.9.9 is the last release
   to claim support Python 2.3)


Urwid 0.9.9.1
=============

2010-01-25

 * Fix for ListBox snapping to selectable widgets taller than the
   ListBox itself

 * raw_display switching to alternate buffer now works properly with
   Terminal.app

 * Fix for BoxAdapter backwards incompatibility introduced in 0.9.9

 * Fix for a doctest failure under powerpc

 * Fix for systems with gpm_mev installed but not running gpm


Urwid 0.9.9
===========

2009-11-15

 * New support for 256 and 88 color terminals with raw_display
   and html_fragment display modules

 * New palette_test example program to demonstrate high color
   modes

 * New AttrSpec class for specifying specific colors instead of
   using attributes defined in the screen's palette

 * New MainLoop class ties together widgets, user input, screen
   display and one of a number of new event loops, removing the
   need for tedious, error-prone boilerplate code

 * New GLibEventLoop allows running Urwid applications with GLib
   (makes D-Bus integration easier)

 * New TwistedEventLoop allows running Urwid with a Twisted reactor

 * Added new docstrings and doctests to many widget classes

 * New AttrMap widget supports mapping any attribute to any other
   attribute, replaces AttrWrap widget

 * New WidgetDecoration base class for AttrMap, BoxAdapter, Padding,
   Filler and LineBox widgets creates a common method for accessing
   and updating their contained widgets

 * New left and right values may be specified in Padding widgets

 * New command_map for specifying which keys cause actions such as
   clicking Button widgets and scrolling ListBox widgets

 * New tty_signal_keys() method of raw_display.Screen and
   curses_display.Screen allows changing or disabling the keys used
   to send signals to the application

 * Added helpful __repr__ for many widget classes

 * Updated all example programs to use MainLoop class

 * Updated tutorial with MainLoop usage and improved examples

 * Renamed WidgetWrap.w to _w, indicating its intended use as a way
   to implement a widget with other widgets, not necessarily as
   a container for other widgets

 * Replaced all tabs with 4 spaces, code is now more aerodynamic
   (and PEP 8 compliant)

 * Added saving of stdin and stdout in raw_display module allowing
   the originals to be redirected

 * Updated BigText widget's HalfBlock5x4Font

 * Fixed graph example CPU usage when animation is stopped

 * Fixed a memory leak related to objects listening for signals

 * Fixed a Popen3 deprecation warning


Urwid 0.9.8.4
=============

2009-03-13

 * Fixed incompatibilities with Python 2.6 (by Friedrich Weber)

 * Fixed a SimpleListWalker with emptied list bug (found by Walter
   Mundt)

 * Fixed a curses_display stop()/start() bug (found by Christian
   Scharkus)

 * Fixed an is_wide_character() segfault on bad input data bug
   (by Andrew Psaltis)

 * Fixed a CanvasCache with render() used in both a widget and its
   superclass bug (found by Andrew Psaltis)

 * Fixed a ListBox.ends_visible() on empty list bug (found by Marc
   Hartstein)

 * Fixed a tutorial example bug (found by Kurtis D. Rader)

 * Fixed an Overlay.keypress() bug (found by Andreas Klöckner)

 * Fixed setuptools configuration (by Andreas Klöckner)


Urwid 0.9.8.3
=============

2008-07-14

 * Fixed a canvas cache memory leak affecting 0.9.8, 0.9.8.1 and
   0.9.8.2 (found by John Goodfellow)

 * Fixed a canvas fill_attr() bug (found by Joern Koerner)


Urwid 0.9.8.2
=============

2008-05-19

 * Fixed incompatibilities with Python 2.3

 * Fixed Pile cursor pref_col bug, WidgetWrap rows caching bug, Button
   mouse_event with no callback bug, Filler body bug triggered by the
   tutorial and a LineBox lline parameter typo.


Urwid 0.9.8.1
=============

2007-06-21

 * Fixed a Filler render() bug, a raw_display start()/stop() bug and a
   number of problems triggered by very small terminal window sizes.


Urwid 0.9.8
===========

2007-03-23

 * Rendering is now significantly faster.

 * New Widget base class for all widgets. It includes automatic caching
   of rows() and render() methods. It also adds a new __super attribute
   for accessing methods in superclasses.

   Widgets must now call self._invalidate() to notify the cache when
   their content has changed.

   To disable caching in a widget set the class variable no_cache to a
   list that includes the string "render".

 * Canvas classes have been reorganized: Canvas has been renamed to
   TextCanvas and Canvas is now the base class for all canvases. New
   canvas classes include BlankCanvas, SolidCanvas and CompositeCanvas.

 * External event loops may now be used with the raw_display module. The
   new methods get_input_descriptors() and get_input_nonblocking()
   should be used instead of get_input() to allow input processing
   without blocking.

 * The Columns, Pile and ListBox widgets now choose their first
   selectable child widget as the focus widget by default.

 * New ListWalker base class for list walker classes.

 * New Signals class that will be used to improve the existing event
   callbacks. Currently it is used for ListWalker objects to notify
   their ListBox when their content has changed.

 * SimpleListWalker now behaves as a list and supports all list
   operations. This class now detects when changes are made to the list
   and notifies the ListBox object. New code should use this class to
   wrap lists of widgets before passing them to the ListBox
   constructor.

 * New PollingListWalker class is now the default list walker that is
   used when passing a simple list to the ListBox constructor. This
   class is intended for backwards compatibility only. When this class
   is used the ListBox object is unable to cache its render() method.

 * The curses_display module can now draw in the lower-right corner of
   the screen.

 * All display modules now have start() and stop() methods that may be
   used instead of calling run_wrapper().

 * The raw_display module now uses an alternate buffer so that the
   original screen can be restored on exit. The old behaviour is
   available by setting the alternate_buffer parameter of start() or
   run_wrapper() to False.

 * Many internal string processing functions have been rewritten in C to
   improve their performance.

 * Compatible with Python >= 2.2. Python 2.1 is no longer supported.


Urwid 0.9.7.2
=============

2007-01-03

 * Improved performance in UTF-8 mode when ASCII text is used.

 * Fixed a UTF-8 input bug.

 * Added a clear() function to the display modules to force the
   screen to be repainted on the next draw_screen() call.


Urwid 0.9.7.1
=============

2006-10-03

 * Fixed bugs in Padding and Overlay widgets introduced in 0.9.7.


Urwid 0.9.7
===========

2006-10-01

 * Added initial support for fixed widgets - widgets that have a fixed
   size on screen. Fixed widgets expect a size parameter equal to ().
   Fixed widgets must implement the pack(..) function to return their
   size.

 * New BigText class that draws text with fonts made of grids of
   character cells. BigText is a fixed widget and doesn't do any
   alignment or wrapping. It is intended for banners and number readouts
   that need to stand out on the screen.

   Fonts: Thin3x3Font, Thin4x3Font, Thin6x6Font (full ascii)

   UTF-8 only fonts: HalfBlock5x4Font, HalfBlock6x5Font,
   HalfBlockHeavy6x5Font, HalfBlock7x7Font (full ascii)

   New function get_all_fonts() may be used to get a list of the
   available fonts.

 * New example program bigtext.py demonstrates use of BigText.

 * Padding class now has a clipping mode that pads or clips fixed
   widgets to make them behave as flow widgets.

 * Overlay class can now accept a fixed widget as the widget to display
   "on top".

 * New Canvas functions: pad_trim() and pad_trim_left_right().

 * Fixed a bug in Filler.get_cursor_coords() that causes a crash if the
   contained widget's get_cursor_coords() function returns None.

 * Fixed a bug in Text.pack() that caused an infinite loop when the text
   contained a newline. This function is not currently used by Urwid.

 * Edit.__init__() now calls set_edit_text() to initialize its text.

 * Overlay.calculate_padding_filler() and Padding.padding_values() now
   include focus parameters.


Urwid 0.9.6
===========

2006-08-22

 * Fixed Unicode conversion and locale issues when using Urwid with
   Python < 2.4. The graph.py example program should now work properly
   with older versions of Python.

 * The docgen_tutorial.py script can now write out the tutorial example
   programs as individual files.

 * Updated reference documentation table of contents to show which
   widgets are flow and/or box widgets.

 * Columns.set_focus(..) will now accept an integer or a widget as its
   parameter.

 * Added detection for rxvt's HOME and END escape sequences.

 * Added support for setuptools (improved distutils).


Urwid 0.9.5
===========

2006-06-14

 * Some Unicode characters are now converted to use the G1 alternate
   character set with DEC special and line drawing characters. These
   Unicode characters should now "just work" in almost all terminals and
   encodings.

   When Urwid is run with the UTF-8 encoding the characters are left as
   UTF-8 and not converted.

   The characters converted are:

   \u00A3 (£), \u00B0 (°), \u00B1 (±), \u00B7 (·), \u03C0 (π),
   \u2260 (≠), \u2264 (≤), \u2265 (≥), \u23ba (⎺), \u23bb (⎻),
   \u23bc (⎼), \u23bd (⎽), \u2500 (─), \u2502 (│), \u250c (┌),
   \u2510 (┐), \u2514 (└), \u2518 (┘), \u251c (├), \u2524 (┤),
   \u252c (┬), \u2534 (┴), \u253c (┼), \u2592 (▒), \u25c6 (◆)

 * New SolidFill class for filling an area with a single character.

 * New LineBox class for wrapping widgets in a box made of line- drawing
   characters. May be used as a box widget or a flow widget.

 * New example program graph.py demonstrates use of BarGraph, LineBox,
   ProgressBar and SolidFill.

 * Pile class may now be used as a box widget and contain a mix of box
   and flow widgets.

 * Columns class may now contain a mix of box and flow widgets. The box
   widgets will take their height from the maximum height of the flow
   widgets.

 * Improved the smoothness of resizing with raw_display module. The
   module will now try to stop updating the screen when a resize event
   occurs during the update.

 * The Edit and IntEdit classes now use their set_edit_text() and
   set_edit_pos() functions when handling keypresses, so those functions
   may be overridden to catch text modification.

 * The set_state() functions in the CheckBox and RadioButton classes now
   have a do_callback parameter that determines if the callback function
   registered will be called.

 * Fixed a newly introduced incompatibility with python < 2.3.

 * Fixed a missing symbol in curses_display when python is linked
   against libcurses.

 * Fixed mouse handling bugs in the Frame and Overlay classes.

 * Fixed a Padding bug when the left or right has no padding.


Urwid 0.9.4
===========

2006-05-30

 * Enabled mouse handling across the Urwid library.

   Added a new mouse_event() method to the Widget interface definition
   and to the following widgets: Edit, CheckBox, RadioButton, Button,
   GridFlow, Padding, Filler, Overlay, Frame, Pile, Columns, BoxAdapter
   and ListBox.

   Updated example programs browse.py, calc.py, dialog.py, edit.py and
   tour.py to support mouse input.

 * Released the files used to generate the reference and tutorial
   documentation: docgen_reference.py, docgen_tutorial.py and
   tmpl_tutorial.html. The "docgen" scripts write the documentation to
   stdout. docgen_tutorial.py requires the Templayer HTML templating
   library to run: http://excess.org/templayer/

 * Improved Widget and List Walker interface documentation.

 * Fixed a bug in the handling of invalid UTF-8 data. All invalid
   characters are now replaced with '?' characters when displayed.


Urwid 0.9.3
===========

2006-05-14

 * Improved mouse reporting.

   The raw_display module now detects gpm mouse events by reading
   /usr/bin/mev output. The curses_display module already supports gpm
   directly.

   Mouse drag events are now reported by raw_display in terminals that
   provide button event tracking and on the console with gpm. Note that
   gpm may report coordinates off the screen if the user drags the mouse
   off the edge.

   Button release events now report which button was released if that
   information is available, currently only on the console with gpm.

 * Added display of raw keycodes to the input_test.py example program.

 * Fixed a text layout bug affecting clipped text with blank lines, and
   another related to wrapped text starting with a space character.

 * Fixed a Frame.keypress() bug that caused it to call keypress on
   unselectable widgets.


Urwid 0.9.2
===========

2006-03-18

 * Preliminary mouse support was added to the raw_display and
   curses_display modules. A new Screen.set_mouse_tracking() method was
   added to enable mouse tracking. Mouse events are returned alongside
   keystrokes from the Screen.get_input() method.

   The widget interface does not yet include mouse handling. This will
   be addressed in the next release.

 * A new convenience function is_mouse_event() was added to help in
   separating mouse events from keystrokes.

 * Added a new example program input_test.py. This program displays the
   keyboard and mouse input it receives. It may be run as a CGI script
   or from the command line. On the command line it defaults to using
   the curses_display module, use input_test.py raw to use the
   raw_display module instead.

 * Fixed an Edit.render() bug that caused it to render the cursor in a
   different location than that reported by Edit.get_cursor_coords() in
   some circumstances.

 * Fixed a bug preventing use of UTF-8 characters with Divider widgets.


Urwid 0.9.1
===========

2006-03-06

 * BarGraph and ProgressBar can now display data more accurately by
   using the UTF-8 vertical and horizontal eighth characters. This
   behavior will be enabled when the UTF-8 encoding is detected and
   "smoothed" attributes are passed to the BarGraph or ProgressBar
   constructors.

 * New get_encoding_mode() function to determine how Urwid will treat
   raw string data.

 * New raw_display.signal_init() and raw_display.signal_restore()
   methods that may be overridden by threaded applications that need to
   call signal.signal() from their main thread.

 * Fixed a bug that prevented the use of UTF-8 strings in text markup.

 * Removed some forgotten asserts that broke 8-bit and CJK input.


Urwid 0.9.0
===========

2006-02-18

 * New support for UTF-8 encoding including input, display and editing
   of narrow and wide (CJK) characters.

   Preliminary combining (zero-width) character support is included, but
   full support will require terminal behavior detection.

   Right-to-Left input and display are not implemented.

 * New raw_display module that handles console display without relying
   on external libraries. This module was written as a work around for
   the lack of UTF-8 support in the standard version of ncurses.

   Eliminates "dead corner" in the bottom right of the screen.

   Avoids use of bold text in xterm and gnome-terminal for improved
   text legibility.

 * Fixed Overlay bug related to UTF-8 handling.

 * Fixed Edit.move_cursor_to_coords(..) bug related to wide characters
   in UTF-8 encoding.


Urwid 0.9.0-pre3
================

2006-02-13

 * Fixed Canvas attribute padding bug related to -pre1 changes.


Urwid 0.9.0-pre2
================

2006-02-10

 * Replaced the custom align and wrap modes in example program calc.py
   with a new layout class.

 * Fixed Overlay class call to Canvas.overlay() broken by -pre1 changes.

 * Fixed Padding bug related to Canvas -pre1 changes.


Urwid 0.9.0-pre1
================

2006-02-08

 * New support for UTF-8 encoding. Unicode strings may be used and will
   be converted to the current encoding when output. Regular strings in
   the current encoding may still be used.

   PLEASE NOTE: There are issues related to displaying UTF-8 characters
   with the curses_display module that have not yet been resolved.

 * New set_encoding() function replaces util.set_double_byte_encoding().

 * New supports_unicode() function to query if unicode strings with
   characters outside the ascii range may be used with the current
   encoding.

 * New TextLayout and StandardTextLayout classes to perform text
   wrapping and alignment. Text widgets now have a layout parameter to
   allow use of custom TextLayout objects.

 * New layout structure replaces line translation structure. Layout
   structure now allows arbitrary reordering/positioning of text
   segments, inclusion of UTF-8 characters and insertion of text not
   found in the original text string.

 * Removed util.register_align_mode() and util.register_wrap_mode().
   Their functionality has been replaced by the new layout classes.


Urwid 0.8.10
============

2005-11-27

 * Expanded tutorial to cover advanced ListBox usage, custom widget
   classes and the Pile, BoxAdapter, Columns, GridFlow and Overlay
   classes.

 * Added escape sequence for "shift tab" to curses_display.

 * Added ListBox.set_focus_valign() to allow positioning of the focus
   widget within the ListBox.

 * Added WidgetWrap class for extending existing widgets without
   inheriting their complete namespace.

 * Fixed web_display/mozilla breakage from 0.8.9. Fixed crash on invalid
   locale setting. Fixed ListBox slide-back bug. Fixed improper space
   trimming in calculate_alignment(). Fixed browse.py example program
   rows bug. Fixed sum definition, use of long ints for python2.1. Fixed
   warnings with python2.1. Fixed Padding.get_pref_col() bug. Fixed
   Overlay splitting CJK characters bug.


Urwid 0.8.9
===========

2005-10-21

 * New Overlay class for drawing widgets that obscure parts of other
   widgets. May be used for drop down menus, combo boxes, overlapping
   "windows", caption text etc.

 * New BarGraph, GraphVScale and ProgressBar classes for graphical
   display of data in Urwid applications.

 * New method for configuring keyboard input timeouts and delays:
   curses_display.Screen.set_input_timeouts().

 * Fixed a ListBox.set_focus() bug.


Urwid 0.8.8
===========

2005-06-13

 * New web_display module that emulates a console display within a web
   browser window. Application must be run as a CGI script under Apache.

   Supports font/window resizing, keepalive for long-lived connections,
   limiting maximum concurrent connections, polling and connected update
   methods. Tested with Mozilla Firefox and Internet Explorer.

 * New BoxAdapter class for using box widgets in places that usually
   expect flow widgets.

 * New curses_display input handling with better ESC key detection and
   broader escape code support.

 * Shortened resize timeout on gradual resize to improve responsiveness.


Urwid 0.8.7
===========

2005-05-21

 * New widget classes: Button, RadioButton, CheckBox.

 * New layout widget classes: Padding, GridFlow.

 * New dialog.py example program that behaves like dialog(1) command.

 * Pile widgets now support selectable items, focus changing with up and
   down keys and setting the cursor position.

 * Frame widgets now support selectable items in the header and footer.

 * Columns widgets now support fixed width and relative width columns, a
   minimum width for all columns, selectable items within columns
   containing flow widgets (already supported for box widgets), focus
   changing with left and right keys and setting the cursor position.

 * Filler widgets may now wrap box widgets and have more alignment options.

 * Updated tour.py example program to show new widget types and
   features.

 * Avoid hogging cpu on gradual window resize and fix for slow resize
   with cygwin's broken curses implementation.

 * Fixed minor CJK problem and curs_set() crash under MacOSX and Cygwin.

 * Fixed crash when deleting cells in calc.py example program.


Urwid 0.8.6
===========

2005-01-03

 * Improved support for CJK double-byte encodings: BIG5, UHC, GBK,
   GB2312, CN-GB, EUC-KR, EUC-CN, EUC-JP (JISX 0208 only) and EUC-TW
   (CNS 11643 plain 1 only)

 * Added support for ncurses' use_default_colors() function to
   curses_display module (Python >= 2.4).

   register_palette() and register_palette_entry() now accept "default"
   as foreground and/or background. If the terminal's default attributes
   cannot be detected black on light gray will be used to accommodate
   terminals with always-black cursors.

   "default" is now the default for text with no attributes. This means
   that areas with no attributes will change from light grey on black
   (curses default) to black on light gray or the terminal's default.

 * Modified examples to not use black as background of Edit widgets.

 * Fixed curses_display curs_set() call so that cursor is hidden when
   widget in focus has no cursor position.


Urwid 0.8.5
===========

2004-12-15

 * New tutorial covering basic operation of: curses_display.Screen,
   Canvas, Text, FlowWidget, Filler, BoxWidget, AttrWrap, Edit, ListBox
   and Frame classes

 * New widget class: Filler

 * New ListBox functions: get_focus(), set_focus()

 * Debian packages for Python 2.4.

 * Fixed curses_display bug affecting text with no attributes.


Urwid 0.8.4
===========

2004-11-20

 * Improved support for Cyrillic and other simple 8-bit encodings.

 * Added new functions to simplify taking screenshots:
   html_fragment.screenshot_init() and
   html_fragment.screenshot_collect()

 * Improved urwid/curses_display.py input debugging

 * Fixed cursor in screenshots of CJK text. Fixed "end" key in Edit
   boxes with CJK text.


Urwid 0.8.3
===========

2004-11-15

 * Added support for CJK double-byte encodings.

   Word wrapping mode "space" will wrap on edges of double width
   characters. Wrapping and clipping will not split double width
   characters.

   curses_display.Screen.get_input() may now return double width
   characters. Text and Edit classes will work with a mix of regular and
   double width characters.

 * Use new method Edit.set_edit_text() instead of Edit.update_text().

 * Minor improvements to edit.py example program.


Urwid 0.8.2
===========

2004-11-08

 * Re-released under GNU Lesser General Public License.


Urwid 0.8.1
===========

2004-10-29

 * Added support for monochrome terminals. see
   curses_display.Screen.register_palette_entry() and example programs.
   set TERM=xterm-mono to test programs in monochrome mode.

 * Added unit testing code test_urwid.py to the examples.

 * Can now run urwid/curses_display.py to test your terminal's input and
   colour rendering.

 * Fixed an OSX browse.py compatibility issue. Added some OSX keycodes.


Urwid 0.8.0
===========

2004-10-17

 * Initial Release
