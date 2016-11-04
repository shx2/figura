"""
Global settings of figura
"""

from os import environ as _ENV
from .misc import Struct

################################################################################
# Defaults

DEFAULT_CONFIG_FILE_EXT = 'fig'

################################################################################
# The SETTINGS

SETTINGS = Struct(
    CONFIG_FILE_EXT = _ENV.get('FIGURA_CONFIG_FILE_EXT', DEFAULT_CONFIG_FILE_EXT),
)

################################################################################

def set_setting(key, new_value):
    old_val = SETTINGS[key]
    SETTINGS[key] = new_value
    return old_val

def get_setting(key, *default):
    return getattr(SETTINGS, key, *default)

################################################################################
