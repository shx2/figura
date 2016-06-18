:note: Simply writing ``from os import environ`` adds the variable ``environ`` to the namespace and
    ends up including the full environment in the config file (or barfing if it includes values which
    cannot be understood as valid figura constructs). To avoid this namespace pollution, we make it
    hidden: ``from os import environ as _ENV``.