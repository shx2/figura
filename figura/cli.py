"""
Tools for supporting config- and config-overrides-related CLI options
for python scripts.

This module provides integration with the ``argparse`` python CLI parser.
``optparse`` is currently not supported.

Example::

    import argparse
    from figura import read_config
    from figura.cli import add_override_argument
    # create the parser object:
    parser = argparse.ArgumentParser()
    # define cli arguments for specifying config file and overrides to apply to it:
    parser.add_argument('config', nargs = 1)
    add_override_argument(parser)
    # parse some arguments:
    args = parser.parse_args(['--override', 'x=somevalue', 'figura.tests.config.basic1'])
    # read the config and apply the overrides to it:
    config = read_config(args.config[0])
    config.apply_overrides(args.override)
    print(config)
    
Another example, leveraging `build_config <#figura.cli.build_config_from_cli>`__::

    import argparse
    from figura import read_config
    from figura.cli import add_override_argument
    # create the parser object:
    parser = argparse.ArgumentParser()
    # define cli arguments for specifying config file and overrides to apply to it:
    default_config = 'figura.tests.config.basic1'
    parser.add_argument('config', nargs = '*')  # 0 or more configs
    add_override_argument(parser)
    # parse some arguments:
    args = parser.parse_args(['--override', 'x=somevalue'])
    # read the config and apply the overrides to it:
    config = build_config_from_cli(args, default_config = default_config)
    print(config)

"""

import argparse
import six

from .container import ConfigContainer
from .utils import build_config

################################################################################
# argparse
################################################################################

DEFAULT_OVERRIDE_OPTION_NAMES = ( '-O', '--override' )


def add_override_argument(parser, *names, **kwargs):
    """
    Add to the argument-parser an argument for taking config-overrides via CLI.

    :note: The values of the overrides are read from CLI as strings. The
        code using them is responsible for converting them to other types
        as needed. Some convenience functions are provided for this purpose
        (e.g. boolify_).
    
    :param parser: an ArgumentParser object.
    :param names: The `names` args to be passed on to `parser.add_argument`.
        Defaults to `DEFAULT_OVERRIDE_OPTION_NAMES`.
    :param kwargs: Extra kwargs to pass on to `parser.add_argument`.
        Supported kw arguments: dest, required, help.

    .. _boolify:

    """
    if not names:
        names = DEFAULT_OVERRIDE_OPTION_NAMES
    dest = kwargs.pop('dest', None)
    required = kwargs.pop('required', False)
    help = kwargs.pop('help', 'extra overrides to apply to the config')
    if kwargs:
        raise TypeError('add_override_argument() got an invalid keyword argument: %s' % list(kwargs)[0])

    ov_container = ConfigContainer()
    ov_container.get_metadata().is_override_set = True
    parser.add_argument(
        *names,
        dest = dest,
        default = ov_container,
        required = required,
        action = _add_to_override_set,
        type = _dict_from_string,
        help = help
    )

def _dict_from_string(overrides_string):
    dct = {}
    for part in split_list_value(overrides_string):
        if not '=' in part:
            raise ValueError(part)
        k, _, v = part.partition('=')
        dct[k] = v
    return dct

class _add_to_override_set(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        getattr(namespace, self.dest).update(values)

def build_config_from_cli(
        parsed_args,
        default_config = None,
        config_arg_name = 'config',
        override_arg_name = 'override',
        **kwargs):
    """
    A convenience function for combining configs and overrides from CLI.
    """
    configs = getattr(parsed_args, config_arg_name)
    overrides = getattr(parsed_args, override_arg_name)
    return build_config(
        *configs,
        extra_overrides = overrides,
        default_config = default_config,
        **kwargs
    )

################################################################################
# Escaping
################################################################################

OPTION_VALUE_ESCAPE_CHAR = '@'

def escape_list_value(value):
    """
    .. testsetup:: 
    
       from figura.cli import escape_list_value
       
    >>> escape_list_value('a')
    'a'
    >>> escape_list_value('a,b')
    'a@,b'
    >>> escape_list_value('@a@,b')
    '@@a@@@,b'
    """
    value = value.replace(OPTION_VALUE_ESCAPE_CHAR, OPTION_VALUE_ESCAPE_CHAR + OPTION_VALUE_ESCAPE_CHAR)
    value = value.replace(',', OPTION_VALUE_ESCAPE_CHAR + ',')
    return value

def split_list_value(value, delim = ','):
    """
    .. testsetup:: 
    
       from figura.cli import split_list_value
       
    >>> split_list_value('a,b,c')
    ['a', 'b', 'c']
    >>> split_list_value('a@,b@,c')
    ['a,b,c']
    >>> split_list_value('a@@,b@@,c')
    ['a@', 'b@', 'c']
    >>> split_list_value('@a,@b,@c@@')
    ['a', 'b', 'c@']
    >>> split_list_value('a,b,c@')
    ['a', 'b', 'c@']
    >>> split_list_value('')
    []
    """
    if not value:
        return []
    is_escaped = False
    tokens = ['']
    i = 0
    while i < len(value):
        c = value[i]
        if c == OPTION_VALUE_ESCAPE_CHAR and i < len(value) - 1:
            is_escaped = True
            i += 1
            c = value[i]
        else:
            is_escaped = False
        if c == delim and not is_escaped:
            tokens.append('')
        else:
            tokens[-1] += c
        i += 1
    return tokens

################################################################################
# Convenience functions for converting string values (from CLI) to other types
################################################################################

def _cast(v, t):
    if v is None:
        return None
    return t(v)

def intify(x):
    return _cast(x, int)

def floatify(x):
    return _cast(x, float)

_BOOLIFY_DICT = {
    0: False, 1: True,
    '0': False, '1': True,
    'no': False, 'yes': True,
    'n': False, 'y': True,
    'false': False, 'true': True,
    'disabled': False, 'enabled': True,
    'off': False, 'on': True,
}

def boolify(x):
    """
    Try to guess what boolean value ``x`` represents.
    
    :param x: could be a bool, string ("true", "yes", etc.), int (0 or 1)
    :raise ValueError: if can't determine bool-value from ``x``

    .. testsetup:: 
    
       from figura.cli import boolify
    
    >>> boolify(True)
    True
    >>> boolify(False)
    False
    >>> boolify('fAlse')
    False
    >>> boolify('yes')
    True
    >>> boolify(1)
    True
    >>> boolify(0)
    False
    
    """
    if isinstance(x, six.string_types):
        x = x.lower()
    try:
        return _BOOLIFY_DICT[x]
    except KeyError:
        raise ValueError('Can\'t boolify value: %r' % x)


################################################################################
