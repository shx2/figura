:note: ``figura_print`` supports taking ``--override`` cli option. We used this option here to demostrate how
    flat override sets are useful.

:note: The figura Python package come with useful tools for scripts to support taking config overrides
    as command line options. Check out the `figura.cli <#module-figura.cli>`_ module.

:note: When passing overrides from command line, the values are always represented as strings.

:note: If you want to define a flat override set in a figura file, using the ``.``-delimiter will not work.
    For such cases, use the alternative ``__`` (double underscore) delimiter::
    
        class overrides:
            a__b__c = 42  # same meaning as: a.b.c = 42

    