========================
Figura Reference Guide
========================

This is a reference guide of the `Figura`_ configuation language.

.. _Figura: index.html






Prerequisites
================

Below are the prerequisites to running the examples in this guide.

The source files can be found on `github`_, under ``docs/guide/``.

Every figura configuration file is a python module. When the file is processed,
the python interpreter is used to first import the module. This means that in order for the
python interpreter to find the modules, PYTHONPATH needs to be set accordingly.

In a \*nix system (using ``bash``), you can set PYTHONPATH like this::

    export PYTHONPATH=/PATH/TO/FIGURA/docs/guide/

Also, you can see that the ``guide/`` directory, under which the config files included in
this guide reside, contains a ``__init__.py`` file. This is required for the same reason --
to make the modules python-importable.

.. _github: https://github.com/shx2/figura.git





A Basic Figura File
================================

In its most basic form, a figura configuration file is just a python module, which contains
``param=value`` definitions.


::

    > cat sample_0020_basic.py
    greeting = 'Hello, World!'
    display_color = 'green'
    display_font = 'arial'

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0020_basic
    {
      "display_font": "arial", 
      "display_color": "green", 
      "greeting": "Hello, World!"
    }

:note: JSON structures are not ordered, and therefore the order here is not preserved. This is
    also true for figura configs in general, not only when formatted as JSON.




Config Containers
================================

You can define a config-container (e.g. for grouping some config params) using the ``class`` python construct.

Config container can also be nested.


::

    > cat sample_0030_containers.py
    class params1:
        a = 1
        b = 'two'
    
    class params2:
        x = 111
        class nested_params:
            y = 555
            z = 999
            class deeply_nested_params:
                z = 0

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0030_containers
    {
      "params1": {
        "a": 1, 
        "b": "two"
      }, 
      "params2": {
        "x": 111, 
        "nested_params": {
          "y": 555, 
          "z": 999, 
          "deeply_nested_params": {
            "z": 0
          }
        }
      }
    }

:note: Each figura config file *also* defines a config-container -- the top-level one.
    In the previous example, ``0020_basic`` defined a container with three params.





Reusing params and containers
================================

After defining config params, you can use them later when defining other params. The same is true for containers.

This is important for avoiding config/code duplication.


::

    > cat sample_0040_reusing.py
    _host = 'localhost' # params prefixed by underscore are hidden
    class http_connection:
        host = _host  # using the definition of _host above, instead of re-defining
        port = 80
    class ftp_connetion:
        host = _host  # using the definition of _host above, instead of re-defining
        port = 21
    
    class client:
        connection = http_connection  # config-containers (such as http_connection) can also be reused

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0040_reusing
    {
      "ftp_connetion": {
        "host": "localhost", 
        "port": 21
      }, 
      "http_connection": {
        "host": "localhost", 
        "port": 80
      }, 
      "client": {
        "connection": {
          "host": "localhost", 
          "port": 80
        }
      }
    }




Importing Definitions From Other Files
================================================

Config params and containers defined in other figura files can be imported using Python's import mechanism.

:note: just importing a definition automatically causes it to be included in your config (because it is part of module's
    namespace). If you want to "hide" an imported definition, rename it to a name starting with ``_``.


::

    > cat sample_0050_importing.py
    from sample_0020_basic import greeting  # greeting is included in top-level container
    from sample_0020_basic import display_color as _color  # display_color is not included in top-level container
    
    class my_favorites:
        color = _color
        greeting = greeting

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0050_importing
    {
      "my_favorites": {
        "color": "green", 
        "greeting": "Hello, World!"
      }, 
      "greeting": "Hello, World!"
    }

You can make use of all the nice features of Python's import mechanism, e.g. relative imports, ``from mod import *``, etc.




Extending a Base Container
================================

A config container can be used as the base of a new container, extending it with new definitions and overriding base definitions.
This is done using Python's inheritance syntax.

:note: For understanding how this works, it is useful to keep in mind the analogy between defining config containers and defining
    classes in OOP.

:note: The use of the term "override" above is inspired by the analogy to the OOP world. Not to be confused with *override sets*
    (described later). For clarity, the term "overshadow" could also be used here instead.



::

    > cat sample_0060_extending.py
    class debug_logging:
        # logger_name = log_level
        traffic = 'debug'
        engine = 'debug'
    class analysis_debug_logging(debug_logging):
        analyzer = 'debug'  # adding a new param
        traffic = 'warning'  # overshadowing base's traffic param

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0060_extending
    {
      "analysis_debug_logging": {
        "engine": "debug", 
        "traffic": "warning", 
        "analyzer": "debug"
      }, 
      "debug_logging": {
        "engine": "debug", 
        "traffic": "debug"
      }
    }




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


::

    > cat sample_0070_overlaying.py
    class a:
        class b:
            x = 1
            y = 2
    
    class a2(a):
        class b:  # overlaying a.b -- will include x=1
            y = 3

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0070_overlaying
    {
      "a": {
        "b": {
          "y": 2, 
          "x": 1
        }
      }, 
      "a2": {
        "b": {
          "y": 3, 
          "x": 1
        }
      }
    }




Overshadowing instead of Overlaying
-------------------------------------

For choosing the overshadow semantics over overlay, use the ``__opaque__=True`` metadata directive.


::

    > cat sample_0075_opaque.py
    class a:
        class b:
            x = 1
            y = 2
    
    class a2(a):
        class b:  # overshadowing, will not include any params from a.b
            __opaque__ = True
            y = 3

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0075_opaque
    {
      "a": {
        "b": {
          "y": 2, 
          "x": 1
        }
      }, 
      "a2": {
        "b": {
          "y": 3
        }
      }
    }




Override Sets
=================

Figura supports a special type of config containers: override sets. Override sets are config containers
which do not stand by themselves, but are meant to be applied to other config containers, overriding
some of their values (think: patches).

Override sets are defined using the ``__override__=True`` metadata directive.

As with extending containers, overriding deep values is done using deep override sets, reflecting the same
structure. Here too, nested containers are interpreted as overlays (not overshadows).

An override set ISA config container, thus it is just as flexible: you can define it by extending a base
override set, you can import it from another module, you can apply another override set to it, etc.


::

    > cat sample_0080_overrides.py
    __override__ = True
    class my_favorites:  # can be applied to: sample_0050_importing
        color = 'red'  # I don't know what they like, but I love red
        pet = 'dog'  # they don't like pets, but I *do* have a favorite

When applied to ``sample_0050_importing``::

    > figura_print sample_0050_importing sample_0080_overrides
    {
      "my_favorites": {
        "color": "red", 
        "pet": "dog", 
        "greeting": "Hello, World!"
      }, 
      "greeting": "Hello, World!"
    }

:note: When given multiple arguments, ``figura_print`` interprets all arguments which come after the first
    as override sets to be applied to the first. It is therefore useful for flexibly constructing configs, by
    combining the main config with one or more override sets.





Overshadowing Overrides
-------------------------------------

Similarly to extending configs, when overriding configs, override sets are treated as overlaying.

In cases where you want to *replace* (overshadow) a config container instead of overlaying it, use
the ``__opaque_override__=True`` metadata directive.


::

    > cat sample_0083_opaqueoverrides.py
    __override__ = True
    class my_favorites:  # can be applied to: sample_0050_importing
        __opaque_override__ = True  # I don't like anything else which might be included in overridee
        color = 'red'  # I don't know what they like, but I love red
        pet = 'dog'  # they don't like pets, but I *do* have a favorite

When applied to ``sample_0050_importing``, ``my_favorites.greeting`` is excluded::

    > figura_print sample_0050_importing sample_0083_opaqueoverrides
    {
      "my_favorites": {
        "color": "red", 
        "pet": "dog"
      }, 
      "greeting": "Hello, World!"
    }

:note: ``figura_print`` supports taking ``--override`` cli option, which demostrate how flat override sets are useful.





Flat Override Sets
---------------------

There is a special "flat" form for defining override sets.

Using this form, you specify a line for each param to override (no nesting structure), and going down the
nesting levels is indicated using a ``.``-delimiter.

This special form is supported because it is often useful, when running a program from command line, to
pass config-overrides as command line options.

In general, you should prefer the standard form over the flat form, because it is much more flexible (e.g.
it is not always possible to extend a flat override set using inheritance).


An example of applying overrides, passed from command line, to ``sample_0030_containers``::

    > figura_print sample_0030_containers --override params2.x=A_NEW_VALUE1 --override params2.nested_params.z=A_NEW_VALUE2
    {
      "params1": {
        "a": 1, 
        "b": "two"
      }, 
      "params2": {
        "x": "A_NEW_VALUE1", 
        "nested_params": {
          "y": 555, 
          "z": "A_NEW_VALUE2", 
          "deeply_nested_params": {
            "z": 0
          }
        }
      }
    }

:note: ``figura_print`` supports taking ``--override`` cli option. We used this option here to demostrate how
    flat override sets are useful.

:note: The figura Python package come with useful tools for scripts to support taking config overrides
    as command line options. Check out the `figura.cli <#module-figura.cli>`_ module.

:note: When passing overrides from command line, the values are always represented as strings.

:note: If you want to define a flat override set in a figura file, using the ``.``-delimiter will not work.
    For such cases, use the alternative ``__`` (double underscore) delimiter::
    
        class overrides:
            a__b__c = 42  # same meaning as: a.b.c = 42

    




Paths to Config Files
=========================

In most cases, the path you provide to indicate which config file to read is the Pythoh-import path.
E.g., reading config from path ``<<X>>`` roughly translates to the python statement ``import <<X>>``.

However, figura supports dealing with "deep" paths which go inside the config file.


Here we access a nested container::

    > figura_print sample_0030_containers.params2.nested_params
    {
      "y": 555, 
      "z": 999, 
      "deeply_nested_params": {
        "z": 0
      }
    }

It also works with a "leaf" value::

    > figura_print sample_0030_containers.params1.b
    two




Other
=================





Private Variables
------------------

Params prefixed with ``_`` (underscore) are considered "private" or "hidden", and will not be included
in the resulting config container.


::

    > cat sample_0910_hidden.py
    from sample_0020_basic import greeting as _hidden_greeting
    random_greeting = _hidden_greeting
    _my_private_greeting = 'yo'
    my_public_greeting = 'hey'

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0910_hidden
    {
      "random_greeting": "Hello, World!", 
      "my_public_greeting": "hey"
    }




Python Syntax
---------------

The fact that figura config files are valid Python files also means their syntax is as rich as Python's.

The Python syntax can be leveraged for making the config files more readable and manageable. E.g., by
using comments, docstrings, imports, expressions and arithmetics.





Expressions and Arithmetics
-------------------------------



::

    > cat sample_0930_arithmetics.py
    # Say we want to poll A every X seconds, B every 2*X seconds, and C
    # every 8*X seconds.
    # We sometimes change X, and rarely change the ratios between A, B, and C.
    # Written this way, when we want to change X, we only need to change the value
    # of _basic_polling_interval_seconds.
    # The rules about the default ratios are encoded here and not in the code
    # dealing with params, thus keeping it simple.
    _basic_polling_interval_seconds = 5 * 60  # every 5 minutes (more readable than _basic_polling_interval_seconds=300)
    class A:
        polling_interval = _basic_polling_interval_seconds
    class B:
        polling_interval = _basic_polling_interval_seconds * 2
    class C:
        polling_interval = _basic_polling_interval_seconds * 8

When processed and formatted as JSON::

    > /home/shx2/d/figura/figura/tools/figura_print.py sample_0930_arithmetics
    {
      "A": {
        "polling_interval": 300
      }, 
      "C": {
        "polling_interval": 2400
      }, 
      "B": {
        "polling_interval": 600
      }
    }




Reading Environment Variables
-------------------------------

It is sometimes useful to read environment variables from inside a figura file. As in any Python
code, this is done using ``os.environ``.


::

    > cat sample_0940_envvars.py
    from os import environ as _ENV
    contact_email = _ENV.get('EMAIL', 'nobody@nowhere.com')

When processed and formatted as JSON, with the env var set::

    > EMAIL=me@myself.com figura_print sample_0940_envvars
    {
      "contact_email": "me@myself.com"
    }

Using the default value when the env var is not defined::

    > figura_print sample_0940_envvars
    {
      "contact_email": "nobody@nowhere.com"
    }

:note: Simply writing ``from os import environ`` adds the variable ``environ`` to the namespace and
    ends up including the full environment in the config file (or barfing if it includes values which
    cannot be understood as valid figura constructs). To avoid this namespace pollution, we make it
    hidden: ``from os import environ as _ENV``.




