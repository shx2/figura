"""
Low-level import-related tools.

This module includes tools for enabling and disabling imoprting files with custom suffixes
(e.g. ".fig") in python's import mechanism.
"""

import sys
import importlib
import importlib.machinery
import imp

SourceFileLoader = importlib.machinery.SourceFileLoader


################################################################################

_HOOKS_PATCHED = False
_INSTALLED_LOADERS = []


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

def install_figura_importer(suffix):
    """
    Make files with given suffix visible to python ``import``.
    These file will take precedence over standard suffixes (".py", etc.).
    """
    with _implock:
        _patch_hooks()
        if is_installed_figura_importer(suffix):
            # already installed
            return
        _INSTALLED_LOADERS.append((suffix, SourceFileLoader))


def uninstall_figura_importer(suffix):
    """
    Undo what `install_figura_importer`_ did.
    """
    with _implock:
        for i, (sfx, loader) in enumerate(_INSTALLED_LOADERS):
            if suffix == sfx:
                break
        else:
            # not currently installed
            return
        del _INSTALLED_LOADERS[i]


def is_installed_figura_importer(suffix):
    with _implock:
        return any(suffix == sfx for (sfx, loader) in _INSTALLED_LOADERS)


################################################################################
# privates

class _ConcatenatedSequence:
    # we only need to defined __iter__, because finder._loaders is only used by iterating over

    def __init__(self, *seqs):
        self.seqs = seqs

    def __iter__(self):
        for seq in self.seqs:
            yield from seq


def _patch_finder(finder):
    if not isinstance(getattr(finder, '_loaders', None), list):
        return False
    finder._loaders = _ConcatenatedSequence(_INSTALLED_LOADERS, finder._loaders)
    return True


def _patch_path_hook(hook):

    def path_hook(*a, **kw):
        finder = hook(*a, **kw)
        _patch_finder(finder)
        return finder

    return path_hook


def _patch_hooks():
    # only runs once
    global _HOOKS_PATCHED
    if _HOOKS_PATCHED:
        return

    # patch hooks in sys.path_hook, so that our patched finder is created from now on:
    for i, hook in enumerate(sys.path_hooks):
        if 'path_hook_for_FileFinder' in str(hook):
            patched_hook = _patch_path_hook(hook)
            sys.path_hooks[i] = patched_hook
            break
    else:
        assert 0, 'no FileFinder found in sys.path_hooks'

    # patch finders already created and cached:
    for key, finder in sys.path_importer_cache.items():
        _patch_finder(finder)

    _HOOKS_PATCHED = True


################################################################################
