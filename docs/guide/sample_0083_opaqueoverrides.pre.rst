Overshadowing Overrides
-------------------------------------

Similarly to extending configs, when overriding configs, override sets are treated as overlaying.

In cases where you want to *replace* (overshadow) a config container instead of overlaying it, use
the ``__opaque_override__=True`` metadata directive.
