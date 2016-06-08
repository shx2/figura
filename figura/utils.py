"""
Useful tools when working with Figura configs.
"""

from .errors import ConfigError, ConfigParsingError
from .path import to_figura_path
from .container import ConfigContainer
from .parser import ConfigParser
from .importutils import walk_packages

################################################################################
# convenience functions

def read_config(path):
    """
    Flexibly read/process a Figura config file.
    
    The path can point to:
    
    - a config file. E.g. ``figura.tests.config.basic1``
    - a config directory. E.g. ``figura.tests.config``
    - a value (or section) inside a config. E.g. ``figura.tests.config.basic1.some_params.a``
    
    :param path: a string or a `FiguraPath <#figura.path.FiguraPath>`_.
    :return: a `ConfigContainer <#figura.container.ConfigContainer>`_.
        In case of a deep path, the return value is the value from inside the
        conainer, which is not necessarilly a ConfigContainer.
        
    .. testsetup:: 

        from figura.utils import read_config
        
    >>> read_config('figura.tests.config.basic1').some_params.a  # read a config file
    1
    >>> read_config('figura.tests.config.basic1.some_params.a')  # read a value inside a config file
    1
    >>> read_config('figura.tests.config').basic1.some_params.a  # read a directory of config files
    1
    """
    
    # process the pass, split into file-path and attr-path
    file_path, attr_path = to_figura_path(path).split_parts()
    if not file_path:
        raise ConfigParsingError('No config file found for path: %r' % str(path))
    
    # parse the path:
    parser = ConfigParser()
    config = parser.parse(file_path)

    # support reading all modules under a package, and create a ConfigContainer
    # reflecting the structure:
    for rel_mod_path in _gen_modules(file_path):
        mod_path = '%s.%s' % ( file_path, rel_mod_path )
        cur_config = parser.parse(mod_path)
        config.deep_setattr(rel_mod_path, cur_config)
    
    # apply the attr-path:
    if attr_path:
        config = config.deep_getattr(attr_path)

    return config

def _gen_modules(file_path):
    for importer, modname, ispkg in walk_packages(file_path):
        yield modname
    
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
    
    configs = [ _to_config(conf) for conf in paths ]
    
    # using the default_config if the first config passed is an overrideset
    use_default = (len(configs) == 0) or configs[0].get_metadata().is_override_set
    if default_config is not None and use_default:
        configs = [ _to_config(default_config) ] + configs
    
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
            config.apply_overrides(cur_config, enforce_override_set = enforce_override_set)
    if extra_overrides:
        config.apply_overrides(extra_overrides, enforce_override_set = enforce_override_set)
    return config

def _to_config(x):
    if isinstance(x, ConfigContainer):
        return x
    else:
        return read_config(x)

################################################################################
