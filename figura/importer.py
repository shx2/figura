"""
Low-level import-related tools.

This module includes tools for enabling and disabling imoprting files with custom suffixes
(e.g. ".fig") in python's import mechanism.
"""

import sys
import importlib
import importlib.machinery
import imp


################################################################################
# python version compatibility

FileFinder = importlib.machinery.FileFinder
SourceFileLoader = importlib.machinery.SourceFileLoader
try:
    _get_supported_file_loaders = importlib._bootstrap_external._get_supported_file_loaders
except AttributeError:
    _get_supported_file_loaders = importlib._bootstrap._get_supported_file_loaders


################################################################################
# lock

class _ImpLock:

    def acquire(self):
        imp.acquire_lock()

    def release(self):
        imp.release_lock()

    def __enter__(self):
        self.acquire()

    def __exit__(self, *a, **kw):
        self.release()


_implock = _ImpLock()


################################################################################
# install/uninstall global functions

_INSTALLED_SUFFIXES = []


def install_figura_importer(suffix):
    """
    Make files with given suffix visible to python ``import``.
    These file will take precedence over standard suffixes (".py", etc.).
    """
    with _implock:
        if suffix in _INSTALLED_SUFFIXES:
            # already installed
            return
        _INSTALLED_SUFFIXES.append(suffix)
        _refresh_hooks()


def uninstall_figura_importer(suffix):
    """
    Undo what `install_figura_importer`_ did.
    """
    with _implock:
        try:
            _INSTALLED_SUFFIXES.remove(suffix)
        except KeyError:
            # not currently installed
            pass
        else:
            _refresh_hooks()


def is_installed_figura_importer(suffix):
    with _implock:
        return suffix in _INSTALLED_SUFFIXES


def _refresh_hooks():
    hooks = sys.path_hooks
    for pos, hook in enumerate(hooks):
        if 'FileFinder' in str(hook):
            break
    else:
        assert 0, 'no FileFinder found in sys.path_hooks'

    # reconstruct the FileFinder path hook, but this time adding our loader+suffixes.
    # our importer is added first, to take precedence over standard suffixes (".py", etc.)
    figura_loader = (SourceFileLoader, list(_INSTALLED_SUFFIXES))
    orig_loaders = _get_supported_file_loaders()

    # replace FileFinder hook with the new one:
    hooks[pos] = FileFinder.path_hook(figura_loader, *orig_loaders)

    _clear_caches()


def _clear_caches():
    sys.path_importer_cache.clear()
    importlib.invalidate_caches()


################################################################################
