Entry Points
=================

:In this section: We learn how to define config file's *entry point* (and why).

You might have noticed a small repetition or awkwardness in the examples so far.
The identifier ``saw`` is repeated. It appear both in the config file name (and the
figura path used for pointing to it), and the top-level config container defined in
the config file.  The code which uses the config definitions will have to be aware of
both.

To avoid this, we could just avoid the ``class saw:`` container and put the nested definitions
at file's top level directly.  However, this has the disadvantage that it prevents us from
extending the ``saw`` container if we ever want to. In other words, this will no longer be possible::

    from .saw import saw
    class experimental_saw(saw):
        ...

Instead, we can define file's *entry point*, using the ``__entry_point__`` directive.

::

    ...
    class saw:
        ...
    __entry_point__ = saw
