Extending Containers
============================================

:In this section: We learn how *basic config containers can be extended*.

Once again, you might have noticed that in the last example we had to repeat ourselves.
All modules contained the exact same definition, namely ``alert = _alert``.

`No way <index.html#the-zen-of-figura>`_.

Since there are parts which are common to all modules, it makes sense to define them once
in a *base-module config container*, and having each module extend it.

Here is how this is done.

