#! /usr/bin/env python
"""
Given a set of files, ensure they all have the same set of keys.

Usage
------

By "python-import" path::

    % python figura_consistency.py figura.tests.config

By file path::

    % python figura_consistency.py figura/tests/config
    % python figura_consistency.py *.fig
    % find figura/tests/config -name '*.fig' | python figura_consistency.py
"""

import os
import sys
import argparse
from collections import deque

from figura.importutils import is_importable_path
from figura.parser import ConfigParser
from figura.settings import get_setting
import importlib

###############################################################################


def to_flat_dict(d):
    """
    Convert a deep dictionary into a flat dictionary where the keys are the .-delimited path
    """
    result = {}
    items = deque(d.iteritems())
    while items:
        key, value = items.pop()
        if isinstance(value, dict):
            items.extend([
                ('.'.join((key, subkey)), subvalue)
                for subkey, subvalue in value.iteritems()
            ])
        else:
            result[key] = value

    return result


def base_paths(path, file):
    """
    Generate prefixes of path where the file exists

    Used to find the earliest ancestor of a path that has a file, for example a git repo or python package
    """
    chunks = path.split(os.path.sep)
    for i in range(1, len(chunks)):
        prefix = os.path.sep.join(chunks[:i+1])
        test_file = os.path.sep.join((prefix, file))
        if os.path.exists(test_file):
            yield prefix


def parse_path(path, py_ext=None):
    """
    Given either a python import path or a file path, return both the absolute file path and a python import path
    """
    if py_ext is None:
        py_ext = get_setting('CONFIG_FILE_EXT')

    if os.path.sep in path or path.count('.') == 1 and path.endswith(py_ext):
        return filepath_to_pypath(path, py_ext)
    else:
        return pypath_to_filepath(path, py_ext)


def pypath_to_filepath(pypath, py_ext=None):
    """
    convert a python import path to a file path
    """
    if py_ext is None:
        py_ext = get_setting('CONFIG_FILE_EXT')
    py_ext = os.path.extsep + py_ext

    # convert the config path to a real path
    config_path = pypath
    if config_path.endswith(py_ext):
        config_path = config_path[:-len(py_ext)]
    filepath = pypath.replace('.', os.path.sep)
    if not filepath.endswith(py_ext):
        filepath = filepath + py_ext

    for prefix in sys.path:
        candidate = os.path.join(prefix, filepath)
        if os.path.isfile(candidate):
            return candidate, config_path

    raise ValueError('%s is not importable' % pypath)


def get_relative_path(filepath, prefix):
    """
    Find a relative path from prefix to filepath
    """
    real_prefix = os.path.realpath(prefix)
    filepath_prefix = filepath

    segments = []
    while True:
        filepath_real_prefix = os.path.realpath(filepath_prefix)
        if os.path.samefile(filepath_real_prefix, real_prefix):
            relative_path = os.path.sep.join(reversed(segments))
            assert os.path.samefile(filepath, os.path.sep.join((prefix, relative_path)))
            return relative_path

        next_prefix, next_segment = os.path.split(filepath_prefix)
        segments.append(next_segment)
        if next_prefix == filepath_prefix:
            return None
        filepath_prefix = next_prefix


def filepath_to_pypath(filepath, py_ext=None):
    """
    Convert a filepath into a python import path
    """
    if py_ext is None:
        py_ext = get_setting('CONFIG_FILE_EXT')
    py_ext = os.path.extsep + py_ext

    filepath = os.path.abspath(filepath)
    for prefix in sys.path:
        relative_path = get_relative_path(filepath, prefix)
        if relative_path is not None:
            break

    if relative_path is None:
        raise ValueError('%s is not importable', filepath)

    config_path = relative_path
    if config_path.endswith(py_ext):
        config_path = config_path[:-len(py_ext)]
    config_path = config_path.replace(os.path.sep, '.')
    if config_path.endswith('__init__'):
        config_path = config_path[:-len('__init__')]
    return filepath, config_path


def walk_packages(path, py_ext=None):
    """
    Generate a list of config files contained in a path
    """
    if py_ext is None:
        py_ext = get_setting('CONFIG_FILE_EXT')

    _, import_path = parse_path(path)
    init_file = '__init__.%s' % py_ext
    for root, dirs, files in os.walk(path):
        import_rel_path = get_relative_path(root, path)
        import_root = ('%s.%s' % (import_path, import_rel_path.replace(os.path.sep, '.'))).strip('.')
        for file in files:
            if file == init_file:
                continue
            file_path = os.path.join(root, file)

            import_path = '%s.%s' % (import_root, file[:-(len(py_ext) + 1)])
            if not is_importable_path(import_path, with_ext=py_ext):
                continue

            yield file_path, import_path


def read_configs(path):
    """
    Generate the files and the figura configurations given by a path (python or file)
    """
    file_path, config_path = parse_path(path)

    # import the base path to avoid warnings about not finding a parent module
    for base_path in base_paths(file_path, '__init__.py'):
        base_file_path, base_python_path = parse_path(base_path, py_ext='py')
        importlib.import_module(base_python_path)
        break

    parser = ConfigParser()
    config = parser.parse(config_path)
    if config:
        yield path, config
        return

    for full_path, full_config_path in walk_packages(file_path):
        config = parser.parse(full_config_path)
        yield full_path, config


###############################################################################
# MAIN

def main():
    args = getopt()
    if not args.py_ext:
        from figura.settings import set_extension_fig
        set_extension_fig()

    paths = args.configfile

    if not paths:
        import sys
        paths = sys.stdin

    minimal_keys = None
    maximal_keys = set()
    configs = {}
    for path in paths:
        for config_path, config in read_configs(path):
            config_paths = set(
                k
                for k in to_flat_dict(config).iterkeys()
                if not any(k.startswith(prefix) for prefix in args.exclude)
            )
            configs[config_path] = (config, config_paths)
            if minimal_keys is None:
                minimal_keys = config_paths
            minimal_keys.intersection_update(config_paths)
            maximal_keys.update(config_paths)

    for path, (config, config_paths) in configs.iteritems():
        extra_keys = config_paths.difference(minimal_keys)
        missing_keys = maximal_keys.difference(config_paths)
        if args.extra and extra_keys:
            print('%s is inconsistent:' % (path))
            print('Extra keys:\n%s' % '\n'.join(extra_keys))

        if args.missing and missing_keys:
            print('%s is inconsistent:' % (path))
            print('Missing keys:\n%s' % '\n'.join(missing_keys))

###############################################################################


def getopt():
    parser = argparse.ArgumentParser(description='Read a set of figura files and output inconsistent keys')

    parser.add_argument('configfile', nargs='*', help='''a figura config file, or its python-import path''')
    parser.add_argument('-p', '--py-ext', action='store_true', help='''use the legacy .py extension for figura config files''')

    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument('-e', '--extra', action='store_true')
    output_options.add_argument('-m', '--missing', action='store_true')

    parser.add_argument('-x', '--exclude', action='append', default=[], help='''exclude keys with this prefix from being considered''')

    # TODO: add filter arguments to skip envvars

    args = parser.parse_args()

    if not args.extra and not args.missing:
        args.missing = True

    return args

###############################################################################


if __name__ == '__main__':
    main()
