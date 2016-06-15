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
