:note: When given multiple arguments, ``figura_print`` interprets all arguments which come after the first
    as override sets to be applied to the first. It is therefore useful for flexibly constructing configs, by
    combining the main config with one or more override sets.  Here, we make use of this flexibility.

Overlay vs. Overshadow
-----------------------------

Note the use of the ``__opaque_override__`` directive.  What does it do?

The Writer module may support new outputs in the future, which will cause new configs to be added
to the ``outputs`` container.
In offline mode, we know we only want one ("file").
The default semantic of override sets is to **overlay**, which means that if we had this::

    ...
    class outputs:
        class file:
            ...

other output types (e.g. ``db``) would not be affected. Only the container defining the ``file`` output
type will get new values.

Instead, when we do this::

    ...
    class outputs:
        __opaque_override__ = True
        class file:
            ...

we employ the **overshadow** semantics, which simply sets the value of ``outputs`` to the definitions
included, hiding existing definitions in the overridee.  This ensures we write to only one place.
