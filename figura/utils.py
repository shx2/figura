"""
Useful tools when working with Figura configs.
"""

import os

from .settings import get_setting
from .errors import ConfigError, ConfigParsingError, ConfigValueError
from .path import to_figura_path
from .container import ConfigContainer
from .parser import ConfigParser
from .importutils import is_importable_path, figura_importing


################################################################################
# convenience functions

@figura_importing
def read_config(path, enable_path_spliting=True, should_step_in_package=True):
    """
    Flexibly read/process a Figura config file.

    The path can point to:

    - a config file. E.g. ``figura.tests.config.basic1``
    - a config directory. E.g. ``figura.tests.config``
    - a value (or section) inside a config. E.g. ``figura.tests.config.basic1.some_params.a``

    :param path: a string or a `FiguraPath <#figura.path.FiguraPath>`_.
    :param enable_path_spliting: set to False if the path points to a file (as opposed to
        PATH.TO.FILE.PATH.TO.ATTR), if you want to suppress auto-splitting.
    :return: a `ConfigContainer <#figura.container.ConfigContainer>`_.
        In case of a deep path, the return value is the value from inside the
        conainer, which is not necessarilly a ConfigContainer.

    .. testsetup::

        from figura.utils import read_config

    >>> read_config('figura.tests.config.basic1').some_params.a  # read a config file
    1
    >>> read_config('figura.tests.config.basic1.some_params.a')  # read a value inside a config
    1
    >>> read_config('figura.tests.config').basic1.some_params.a  # read a dir of config files
    1
    """
    return _read_config(
        path,
        enable_path_spliting=enable_path_spliting,
        should_step_in_package=should_step_in_package,
    )


def _read_config(path, enable_path_spliting=True, should_step_in_package=True):
    """
    Should be called from inside a FiguraImportContext_.
    """

    if enable_path_spliting:
        # process the path, split into file-path and attr-path
        file_path, attr_path = to_figura_path(path).split_parts()
    else:
        # path is known to be a file-path, so avoid the lookups
        file_path = path
        attr_path = ''
    if not file_path:
        raise ConfigParsingError('No config file found for path: %r' % str(path))

    # parse the path:
    parser = ConfigParser()
    config = parser.parse(file_path)

    is_pkg = config.__package__ == path
    if should_step_in_package and is_pkg:
        # support reading all modules under a package, and create a ConfigContainer
        # reflecting the structure:
        pkg_module = _get_module_of_config_container(config)
        for filename, rel_mod_path, ispkg in _figura_walk_packages(pkg_module):
            mod_path = '%s.%s' % (file_path, rel_mod_path)
            sub_config = parser.parse(mod_path)
            config.deep_setattr(rel_mod_path, sub_config)

    # apply the attr-path:
    if attr_path:
        try:
            config = config.deep_getattr(attr_path)
        except AttributeError:
            raise ConfigValueError('Attribute %r is missing from config loaded from %r' % (
                attr_path, config.__file__))

    return config


def _figura_walk_packages(pkg_module, prefix=''):
    """
    ``pkgutil.walk_packages`` is completely broken, so we use our own implementation.
    """
    fig_ext = get_setting('CONFIG_FILE_EXT')
    base_path = pkg_module.__name__
    base_dir = os.path.dirname(pkg_module.__file__)
    suffix = '.%s' % fig_ext
    for rel_filename in os.listdir(base_dir):

        if rel_filename.startswith('_'):
            # private, skip.
            # NOTE: this captures both ``__init__.fig`` and ``_privateconf.fig``.
            continue

        abs_filename = os.path.join(base_dir, rel_filename)

        if os.path.isdir(abs_filename):
            # a sub-directory
            # check if it contains configs:
            rel_mod_path = rel_filename
            full_mod_path = '%s.%s' % (base_path, rel_mod_path)
            if is_importable_path(full_mod_path, with_ext=fig_ext):
                yield (abs_filename, rel_mod_path, True)
                parser = ConfigParser()
                subpkg_config = parser.parse(full_mod_path)
                subpkg_module = _get_module_of_config_container(subpkg_config)
                yield from _figura_walk_packages(subpkg_module, prefix=rel_mod_path + '.')

        elif rel_filename.endswith(suffix):
            # a config file
            rel_mod_path = rel_filename[:-len(suffix)]
            if rel_mod_path:
                yield (abs_filename, prefix + rel_mod_path, False)


def _get_module_of_config_container(conf):
    parser = ConfigParser()
    return parser.get_module(conf.__name__)


@figura_importing
def build_config(*paths, **kwargs):
    """
    Build a configuration by reading Figura configs and optional
    override sets, and combining them into a final configuration.

    `read_config <#figura.utils.read_config>`_ is called for processing each path.

    :param paths: paths (strings or FiguraPaths) to config files. All but the first are
        treated as override-sets, and are applied to the base config.
        The first may also be an override-set, in which case,
        ``default_config`` must be specified, and is used as the base
        config.
    :param kwargs['default_config']: if the first path in ``paths`` is an overridet-set,
        default_config is used as the base config
    :param kwargs['extra_overrides']: a ConfigContainer of extra overrides to
        be applied to the config. ``extra_overrides`` are applied last.
    :param kwargs['enforce_override_set']:
        ensure that an override-sets is not used as base-config, and that a non-override-set
        is not used for overriding.
    :return: a `ConfigContainer <#figura.container.ConfigContainer>`_
    """

    default_config = kwargs.pop('default_config', None)
    extra_overrides = kwargs.pop('extra_overrides', None)
    enforce_override_set = kwargs.pop('enforce_override_set', True)
    if kwargs:
        raise TypeError('build_config() got an invalid keyword argument: %s' % list(kwargs)[0])

    configs = [_to_config(conf) for conf in paths]

    # using the default_config if the first config passed is an overrideset
    use_default = (len(configs) == 0) or \
        (isinstance(configs[0], ConfigContainer) and configs[0].get_metadata().is_override_set)
    if default_config is not None and use_default:
        configs = [_to_config(default_config)] + configs

    # read each config and combine them:
    is_first = True
    config = ConfigContainer()
    for cur_config in configs:
        if is_first:
            # This is the base config
            if enforce_override_set and cur_config.get_metadata().is_override_set:
                raise ConfigError('Attempting to use an override-set as a base config', cur_config)
            config = cur_config
            is_first = False
        else:
            # This is an override set to apply to the config
            config.apply_overrides(cur_config, enforce_override_set=enforce_override_set)
    if extra_overrides:
        config.apply_overrides(extra_overrides, enforce_override_set=enforce_override_set)
    return config


def _to_config(x):
    if isinstance(x, ConfigContainer):
        return x
    else:
        return _read_config(x)


################################################################################
