"""
Module-importing related tools, used for loading figura config files,
and inspecting packages containing them.
"""

import sys
import six
import imp
import importlib
import pkgutil
try:
    # py3
    from importlib.util import find_spec as _find_module
except ImportError:
    # py2
    from pkgutil import find_loader as _find_module

from .errors import ConfigParsingError

################################################################################

REMOVE_FROM_SYS_MODULES = True

################################################################################

def import_module_no_side_effects(path):
    """
    Similar to ``importlib.import_module(path)``, but with a few differences:
    
    - ``*.pyc`` files are not created as part of importing
    - the module imported isn't added to ``sys.modules``
    - calling this function multiple times with the same value will actually
      import the module multiple times (whereas standard importing caches the
      module in ``sys.modules``). this also applies for modules being imported
      indirectly during the importing of ``path``.
    """
    try:
        
        imp.acquire_lock()

        # suppress writing of .pyc files:
        # NOTE this part isn't thread safe
        prev_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True

        if REMOVE_FROM_SYS_MODULES:
            # remember which modules were already loaded before we
            # run the import.
            # This is only required in py2, because py3 has importlib.reload().
            oldmods = set(sys.modules.keys())
        
        # do the actual parsing:
        modobj = _raw_import(path)
        
        if REMOVE_FROM_SYS_MODULES:
            # remove all modules which got added to sys.modules in this import, to
            # ensure the next time we are here, they get reloaded.
            # NOTE this part isn't thread safe
            newmods = set(sys.modules.keys()) - oldmods
            for newmod in newmods:
                sys.modules.pop(newmod, None)

        return modobj
    finally:
        sys.dont_write_bytecode = prev_dont_write_bytecode
        imp.release_lock()

def _raw_import(path):
    # First, invalidate caches!
    # From the docs:
    # "If you are dynamically importing a module that was created since the interpreter began execution
    # (e.g., created a Python source file), you may need to call invalidate_caches() in order for the
    # new module to be noticed by the import system."
    # Since we're dealing with config files, we need to support re-reading config files
    # which are modified after the interpreter started.
    # See:
    # https://docs.python.org/3/library/importlib.html#importlib.import_module
    # https://docs.python.org/3/library/importlib.html#importlib.invalidate_caches
    try:
        invalidate_caches = importlib.invalidate_caches
    except AttributeError:
        # python2
        pass
    else:
        # python3
        invalidate_caches()
    # Now can safely import the module
    return importlib.import_module(path)

def import_figura_file(path):
    """
    Import a figura config file (with no side affects).
    
    :param path: a python import path
    :return: a python module object
    :raise ConfigParsingError: if importing fails
    """
    try:
        return import_module_no_side_effects(path)
    except Exception as e:
        if six.PY2:
            # no exception chaining in python2
            #raise ConfigParsingError('Failed parsing "%s": %r' % (path, e)), None, sys.exc_info()[2]  # not a valid py3 syntax
            raise ConfigParsingError('Failed parsing config "%s": %r' % (path, e))
        else:
            #raise ConfigParsingError('Failed parsing config "%s"' % path) from e  # not a valid py2 syntax
            six.raise_from(ConfigParsingError('Failed parsing config "%s"' % path), e)

def is_importable_path(path):
    """
    Does ``path`` point to a module which can be imported?

    :param path: a python import path
    """
    try:
        return _find_module(path) is not None
    except (ImportError, AttributeError):
        return False

def walk_packages(file_path, prefix = ''):
    """
    Same as ``pkgutil.walk_packages``, except that it really does work recursively.
    """
    mod = import_figura_file(file_path)
    if hasattr(mod, '__path__'):
        for importer, modname, ispkg in pkgutil.walk_packages(mod.__path__, prefix = prefix):
            yield importer, modname, ispkg
            if ispkg:
                pref = '%s.%s.' % (prefix, modname) if prefix else '%s.' % (modname,)
                for x in walk_packages('%s.%s' % (file_path, modname), prefix = pref):
                    yield x


################################################################################
