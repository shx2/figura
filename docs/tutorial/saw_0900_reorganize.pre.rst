Reorganizing Files
============================================

:In this section: We admire Figura's flexibility while learning how our config-directory structure can be
    completely *reorganized without requiring a single change to the code* reading the config. (Now that's decoupling!)

Our SAW system proved a huge success over time, and over the years we added countless features to it.
Naturally, our config file grew very long.

It now makes sense to have a separate config file for each module in the system. There
are also common definitions which are used by multiple modules. We create another ``common.py``
file for including those.

We replace our existing directory structure::

    /systems/config
    ├── __init__.py
    ├── ...
    ├── saw.py
    └── ...
    
With this new one (note how ``saw.py`` is replaced with a directory named ``saw``)::

    /systems/config
    ├── __init__.py
    ├── ...
    ├── saw
    │   ├── __init__.py
    │   ├── analyzer.py
    │   ├── common.py
    │   ├── searcher.py
    │   └── writer.py
    └── ...

