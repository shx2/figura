Flat Override Sets
---------------------

There is a special "flat" form for defining override sets.

Using this form, you specify a line for each param to override (no nesting structure), and going down the
nesting levels is indicated using a ``.``-delimiter.

This special form is supported because it is often useful, when running a program from command line, to
pass config-overrides as command line options.

In general, you should prefer the standard form over the flat form, because it is much more flexible (e.g.
it is not always possible to extend a flat override set using inheritance).
