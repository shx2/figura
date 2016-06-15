Overlaying
================

We already covered two important features of the figura language: it supports nesting of config-containers, and 
defining new containers based on others.

However, when using the two together, the results might seem ambiguous. Consider the following example::

    class a:
        class b:
            x = 1
            y = 2
    class a2(a):
        class b:
            y = 3
            
In theory, this could mean two different thing:

1. ``a2.b`` *overshadows* ``a.b``, resulting with: ``a2.b = { 'y': 3 }``
2. ``a2.b`` *overlays* ``a.b``, resulting with: ``a2.b = { 'y': 3, 'x': 1 }``

The notion of *overlay* can be thought of as ``a2.b`` being a transparent layer overlayed upon ``a.b``, not overshadowing
its contents.

When working with configuration files, it is almost always the case that overlaying is desired, and for this reason
Figura treats such cases as overlays.

:note: This is one case where the analogy with OOP breaks. In pure Python, for example, the example above would be
    interpreted as "overshadow": class ``a2`` extends class `a`, therefore when we define `b` inside ``a2``, it *overrides* (meaning
    *overshadows*) ``a.b``.
