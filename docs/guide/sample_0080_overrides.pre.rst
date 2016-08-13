Override Sets
=================

Figura supports a special type of config containers: override sets. Override sets are config containers
which do not stand by themselves, but are meant to be applied to other config containers, overriding
some of their values (think: patches).

Override sets are defined using the ``__override__=True`` metadata directive.  This definition propagates
down to nested containers.

As with extending containers, overriding deep values is done using deep override sets, reflecting the same
structure. Here too, nested containers are interpreted as overlays (not overshadows).

An override set *is-a* config container, thus it is just as flexible: you can define it by extending a base
override set, you can import it from another module, you can apply another override set to it, etc.
