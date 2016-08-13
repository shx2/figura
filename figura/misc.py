"""
Generally useful functions and classes used in this package.
"""

import copy
from collections import OrderedDict

################################################################################
# dict related

def merge_dicts(*args, **kwargs):
    """
    Merge dictionaries. Values in later args override former with the same key.
    kwargs always override.

    .. testsetup:: 

       from figura.misc import merge_dicts
    
    >>> sorted(merge_dicts({'a':1, 'b':2}, {'b':22, 'c':33, 'd':44}, d=444).items())
    [('a', 1), ('b', 22), ('c', 33), ('d', 444)]
     
    """
    if not args:
        args = ( {}, )
    d = copy.copy(args[0])
    for arg in args[1:]:
        
        # order-perserving: if type(arg)==OrderedDict, we assume the
        # caller wants to preserve the order of the items in the ordered dict
        if isinstance(arg, OrderedDict) and not isinstance(d, OrderedDict):
            d = OrderedDict(d)  # preserve order from now on
        
        d.update(arg)

    d.update(kwargs)
    return d

class Struct(dict):
    """
    A struct-like object. Can be thought of as a dict which also allows
    accessing its items using attribute-access::
    
        > x = Struct(a=3, b='bbb')
        > x
        {'a': 3, 'b': 'bbb'}
        > x.a
        3
        > x.a = 5
        > x.a
        5
        > x.c
        AttributeError: 'Struct' object has no attribute 'c'
        > x.c = 5
        > x.c
        5    
    """

    # a simpler implementation would use:
    #   self.__dict__ = self
    # but this can potentially leak memory under some python versions
    # (http://stackoverflow.com/questions/8687904/circular-referenced-objects-not-getting-garbage-collected)

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)
    
    def __setattr__(self, k, v):
        self[k] = v        
    
    def __delattr__(self, k):
        del self[k]        
    
    def __dir__(self):
        return dir({}) + list(self.keys())

################################################################################
# attribute access tricks

def deep_getattr(x, attr_path, *args, **kwargs):
    """
    ``deep_getattr(x, 'a.b.c')`` -->
    ``getattr(getattr(getattr(x, 'a'), 'b'), 'c')``
    """
    try:
        return _deep_attr_operator(getattr, x, attr_path, *args, **kwargs)
    except AttributeError:
        # if a default value is provided, return it
        if args:
            default_value, = args
            return default_value
        raise

def deep_setattr(x, attr_path, value, **kwargs):
    """
    ``deep_setattr(x, 'a.b.c', y)`` -->
    ``setattr(getattr(getattr(x, 'a'), 'b'), 'c', y)``
    """
    return _deep_attr_operator(setattr, x, attr_path, value, **kwargs)

def _deep_attr_operator(func, x, attr_path, *args, **kwargs):
    auto_constructor = kwargs.pop('auto_constructor', None)
    key_normalizer = kwargs.pop('key_normalizer', lambda x: x)
    assert not kwargs, kwargs
    while True:
        attr, delim, rest = attr_path.partition('.')
        attr = key_normalizer(attr)
        if not delim:
            # deepest level -- apply func:
            return func(x, attr, *args)
        # go one level deeper:
        try:
            x = getattr(x, attr)
        except AttributeError:
            if auto_constructor is not None:
                setattr(x, attr, auto_constructor())
                x = getattr(x, attr)
            else:
                raise
        attr_path = rest

################################################################################
