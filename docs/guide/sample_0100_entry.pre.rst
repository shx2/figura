Entry Points
=========================

There can be cases where you'd want to define config params at the top-level of
your config file (so that your program can access the values without extra nesting levels),
but at the same time to be able to use it as a base container elsewhere (e.g. to extend it
in another config file).

Use the ``__entry_point__`` directive for this.
