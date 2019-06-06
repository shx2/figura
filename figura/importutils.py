"""
Module-importing related tools, used for loading figura config files,
and inspecting packages containing them.
"""

import sys
import six
import functools
import imp
import importlib
import pkgutil
import figura.polyloader as polyloader  # TODO: figura.polyloader -> polyloader
try:
    # py3
    from importlib.util import find_spec as _find_module
except ImportError:
    # py2
    from pkgutil import find_loader as _find_module

from .settings import get_setting
from .errors import ConfigParsingError

################################################################################

class _NoImportSideEffectsContext(object):
    
    def __init__(self, cleanup_import_caches = True):
        self.cleanup_import_caches = cleanup_import_caches
        self._backup = {}
    
    def __enter__(self):
        # suppress writing of .pyc files:
        self.prev_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        
        if self.cleanup_import_caches:
            # remember which modules were already loaded before we run the import.
            self._backup_dict(sys.modules, 'modules', run_with_empty = False)
            self._backup_dict(sys.path_importer_cache, 'path_importer_cache', run_with_empty = True)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_import_caches:
            # remove all modules which got added to sys.modules in this import, to
            # ensure the next time we are here, they get reloaded.
            self._restore_dict(sys.modules, 'modules')
            self._restore_dict(sys.path_importer_cache, 'path_importer_cache')

        sys.dont_write_bytecode = self.prev_dont_write_bytecode
    
    def _backup_dict(self, dct, name, run_with_empty = False):
        if run_with_empty:
            self._backup[name] = ( True, dict(dct) )
            dct.clear()
        else:
            self._backup[name] = ( False, set(dct.keys()) )
    
    def _restore_dict(self, dct, name):
        run_with_empty, dct_backup = self._backup.pop(name)
        if run_with_empty:
            # restore dict values
            dct.clear()
            dct.update(dct_backup)
        else:
            # remove newly added keys
            for newkey in set(dct.keys()) - dct_backup:
                dct.pop(newkey, None)

class _FiguraImportContext(_NoImportSideEffectsContext):
    
    def __enter__(self):
        super(_FiguraImportContext, self).__enter__()
        self.should_uninstall = False
        fig_ext = get_setting('CONFIG_FILE_EXT')
        if fig_ext != '.py' and not polyloader.is_installed(fig_ext):
            polyloader.install(_figura_compile, fig_ext)
            self.should_uninstall = True
            self.fig_ext = fig_ext

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_uninstall:
            polyloader.uninstall(self.fig_ext)
        super(_FiguraImportContext, self).__exit__(exc_type, exc_val, exc_tb)


class _ImpLock(object):
    def acquire(self):
        imp.acquire_lock()
    def release(self):
        imp.release_lock()
    def __enter__(self):
        self.acquire()
    def __exit__(self, *a, **kw):
        self.release()

_implock = _ImpLock()

def figura_implocked(func):
    @functools.wraps(func)
    def f(*a, **kw):
        with _implock:
            with _FiguraImportContext():
                return func(*a, **kw)
    return f

def _figura_compile(source_bytes, source_path, fullname):
    """
    Just the standard python-file compiler (non-standard stuff might be added in the future).
    """
    return compile(source_bytes, source_path, 'exec', dont_inherit = True)

################################################################################

def _import_module_no_side_effects(path):
    """
    Similar to ``importlib.import_module(path)``, but with a few differences:
    
    - ``*.pyc`` files are not created as part of importing
    - the module imported isn't added to ``sys.modules``
    - calling this function multiple times with the same value will actually
      import the module multiple times (whereas standard importing caches the
      module in ``sys.modules``). this also applies for modules being imported
      indirectly during the importing of ``path``.
    """
    return _raw_import(path)

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

@figura_implocked
def import_figura_file(path):
    """
    Import a figura config file (with no side affects).
    
    :param path: a python import path
    :return: a python module object
    :raise ConfigParsingError: if importing fails
    """
    try:
        return _import_module_no_side_effects(path)
    except Exception as e:
        if six.PY2:
            # no exception chaining in python2
            #raise ConfigParsingError('Failed parsing "%s": %r' % (path, e)), None, sys.exc_info()[2]  # not a valid py3 syntax
            raise ConfigParsingError('Failed parsing config "%s": %r' % (path, e))
        else:
            #raise ConfigParsingError('Failed parsing config "%s"' % path) from e  # not a valid py2 syntax
            six.raise_from(ConfigParsingError('Failed parsing config "%s"' % path), e)

@figura_implocked
def is_importable_path(path, with_ext = None):
    """
    Does ``path`` point to a module which can be imported?

    :param path: a python import path
    """
    try:
        module_spec = _find_module(path)
    except (ImportError, AttributeError):
        module_spec = None
    if module_spec is None:
        return False
    if with_ext is not None:
        try:
            # py3
            filepath = module_spec.origin
        except AttributeError:
            try:
                # py2
                filepath = module_spec.get_filename()
            except AttributeError:
                # py2, but with polyloader
                filepath = module_spec.path
        if not filepath.endswith('.' + with_ext):
            return False
    return True

@figura_implocked
def walk_packages(file_path, prefix = '', skip_private = True):
    """
    Same as ``pkgutil.walk_packages``, except that it really does work recursively.
    """
    mod = import_figura_file(file_path)
    if hasattr(mod, '__path__'):
        
        # *PREFIX HACK*: for some reason, if we pass an empty prefix, walk_packages() can
        # yield packages not under the path we provide (this is probably a bug in walk_packages()).
        # E.g. if there's a "test" package under the __path__ passed, it can yield python's own
        # "test" package (e.g. (FileFinder('/usr/lib/python3.4/test'), 'test.pystone', False))
        # To bypass this bug, we make sure to always pass a non-empty prefix (and strip it back later).
        DUMMY_PREFIX = 'FIGURA___DUMMY___PREFIX.'
        tmp_prefix = DUMMY_PREFIX + prefix
        
        for importer, modname, ispkg in pkgutil.walk_packages(mod.__path__, prefix = tmp_prefix):

            # *PREFIX HACK* (continued)
            assert modname.startswith(DUMMY_PREFIX), modname
            modname = modname[len(DUMMY_PREFIX):]

            if skip_private and modname.startswith('_'):
                continue
            yield importer, modname, ispkg
            if ispkg:
                if prefix and modname.startswith(prefix):
                    modname = modname[len(prefix):]
                pref = '%s%s.' % (prefix, modname) if prefix else '%s.' % (modname,)
                for x in walk_packages('%s.%s' % (file_path, modname), prefix = pref):
                    yield x


################################################################################
