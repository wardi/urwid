# Urwid split_repr helper functions
#    Copyright (C) 2004-2011  Ian Ward
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

from inspect import getfullargspec


def split_repr(self):
    """
    Return a helpful description of the object using
    self._repr_words() and self._repr_attrs() to add
    to the description.  This function may be used by
    adding code to your class like this:

    >>> class Foo(object):
    ...     __repr__ = split_repr
    ...     def _repr_words(self):
    ...         return ["words", "here"]
    ...     def _repr_attrs(self):
    ...         return {'attrs': "appear too"}
    >>> Foo()
    <Foo words here attrs='appear too'>
    >>> class Bar(Foo):
    ...     def _repr_words(self):
    ...         return Foo._repr_words(self) + ["too"]
    ...     def _repr_attrs(self):
    ...         return dict(Foo._repr_attrs(self), barttr=42)
    >>> Bar()
    <Bar words here too attrs='appear too' barttr=42>
    """
    alist = sorted((str(k), normalize_repr(v)) for k, v in self._repr_attrs().items())

    words = self._repr_words()
    if not words and not alist:
        # if we're just going to print the classname fall back
        # to the previous __repr__ implementation instead
        return super(self.__class__, self).__repr__()
    if words and alist:
        words.append("")
    return f"<{self.__class__.__name__} {' '.join(words) + ' '.join([f'{k}={v}' for k, v in alist])}>"


def normalize_repr(v):
    """
    Return dictionary repr sorted by keys, leave others unchanged

    >>> normalize_repr({1:2,3:4,5:6,7:8})
    '{1: 2, 3: 4, 5: 6, 7: 8}'
    >>> normalize_repr('foo')
    "'foo'"
    """
    if isinstance(v, dict):
        items = sorted((repr(k), repr(v)) for k, v in v.items())

        return f"{{{', '.join(f'{k}: {v}' for k, v in items)}}}"

    return repr(v)


def remove_defaults(d, fn):
    """
    Remove keys in d that are set to the default values from
    fn.  This method is used to unclutter the _repr_attrs()
    return value.

    d will be modified by this function.

    Returns d.

    >>> class Foo(object):
    ...     def __init__(self, a=1, b=2):
    ...         self.values = a, b
    ...     __repr__ = split_repr
    ...     def _repr_words(self):
    ...         return ["object"]
    ...     def _repr_attrs(self):
    ...         d = dict(a=self.values[0], b=self.values[1])
    ...         return remove_defaults(d, Foo.__init__)
    >>> Foo(42, 100)
    <Foo object a=42 b=100>
    >>> Foo(10, 2)
    <Foo object a=10>
    >>> Foo()
    <Foo object>
    """
    args, varargs, varkw, defaults, _, _, _ = getfullargspec(fn)

    # ignore *varargs and **kwargs
    if varkw:
        del args[-1]
    if varargs:
        del args[-1]

    # create a dictionary of args with default values
    ddict = dict(zip(args[len(args) - len(defaults) :], defaults))

    for k in list(d.keys()):
        if k in ddict and ddict[k] == d[k]:
            # remove values that match their defaults
            del d[k]

    return d


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
