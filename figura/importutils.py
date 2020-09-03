"""
Module-importing related tools, used for loading figura config files,
and inspecting packages containing them.
"""

import sys
import copy
import functools
import importlib
from importlib.util import find_spec as _find_spec

from .importer import (
    install_figura_importer, uninstall_figura_importer, is_installed_figura_importer,
    _ImpLockedContext)
from .settings import get_setting
from .errors import ConfigParsingError


################################################################################

class _SysModuleRestoringContext(_ImpLockedContext):
    """
    A context manager which reverts any changes to ``sys.modules`` done by the enclosing block.
    """

    def __init__(self):
        self._sys_modules = None

    def __enter__(self):
        super().__enter__()
        self._backup()

    def __exit__(self, *a, **kw):
        self._restore()
        super().__exit__(*a, **kw)

    def _backup(self):
        self._sys_modules = copy.copy(sys.modules)

    def _restore(self):
        sys.modules.clear()
        sys.modules.update(self._sys_modules)


class FiguraImportContext(_SysModuleRestoringContext):
    """
    A context manager to be used for surrounding code which makes use of python's
    import mechanism for the purpose of loading (or finding, inspecting, etc.) figura
    config files.

    It takes care of several things:

    - acquires the figura-importer lock, for (partial) concurrency protection (releases on exit)
      (implemented in baseclass)
    - enables custom figura importer, for loading figura config files with the custom extension
      (disable on exit)
    - modules imported (directly and indirectly) are not added to ``sys.modules``
      (implemented in baseclass)
    - cache files (``*.pyc``) are not created

    Nesting a ``FiguraImportContext`` inside another is supported, but will incur unnecessary
    runtime overhead.
    """

    def __enter__(self):
        super().__enter__()

        # don't cache it:
        self._disable_write_bytecode()

        # make config files visible to import mechanism:
        self._enable_figura_importer()

    def __exit__(self, *a, **kw):
        # make config files invisible again to import mechanism:
        self._disable_figura_importer()

        # restore original module-caching behavior:
        self._restore_write_bytecode()

        super().__exit__(*a, **kw)

    def _enable_figura_importer(self):
        self.should_uninstall = False
        fig_ext = get_setting('CONFIG_FILE_EXT')
        fig_suffix = '.%s' % fig_ext
        if not is_installed_figura_importer(fig_suffix):
            install_figura_importer(fig_suffix)
            self.should_uninstall = True
            self.fig_ext = fig_ext

    def _disable_figura_importer(self):
        if self.should_uninstall:
            fig_suffix = '.%s' % self.fig_ext
            uninstall_figura_importer(fig_suffix)

    def _disable_write_bytecode(self):
        self.prev_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True

    def _restore_write_bytecode(self):
        sys.dont_write_bytecode = self.prev_dont_write_bytecode


def figura_importing(func):
    """
    A function-decorator for running the function inside a ``FiguraImportContext``.
    """

    @functools.wraps(func)
    def f(*a, **kw):
        with FiguraImportContext():
            return func(*a, **kw)

    return f


################################################################################

def import_figura_file(path):
    """
    Import a figura config file (with no side affects).

    Should be called from inside a ``FiguraImportContext``.

    :param path: a python import path
    :return: a python module object
    :raise ConfigParsingError: if importing fails
    """
    try:
        return importlib.import_module(path)
    except Exception as e:
        raise ConfigParsingError('Failed parsing config "%s"' % path) from e


def is_importable_path(path, with_ext=None):
    """
    Does ``path`` point to a module which can be imported?

    Should be called from inside a ``FiguraImportContext``.

    :param path: a python import path
    """
    try:
        module_spec = _find_spec(path)
    except (ImportError, AttributeError):
        module_spec = None
    if module_spec is None:
        return False
    if with_ext is not None:
        filepath = module_spec.origin
        if not filepath.endswith('.' + with_ext):
            return False
    return True


################################################################################
