Importing Definitions From Other Files
================================================

Config params and containers defined in other figura files can be imported using Python's import mechanism.

:note: just importing a definition automatically causes it to be included in your config (because it is part of module's
    namespace). If you want to "hide" an imported definition, rename it to a name starting with ``_``.
