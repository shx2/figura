"""
Global settings of figura
"""

from os import environ as _ENV
from .misc import Struct

################################################################################
# Defaults

DEFAULT_CONFIG_FILE_EXT = 'py'  # This is currently the default, in V1
#DEFAULT_CONFIG_FILE_EXT = 'fig'  # This will be enabled in V2.0 -- see set_extension_fig()

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

def set_extension_fig():
    """
    Use this for forward-compatibility.  This enables the ".fig" extension
    (which will be the default in V2) while using Figura V1.
    
    Use like::
    
        from figura.settings import set_extension_fig; set_extension_fig()
     
    """
    return set_setting('CONFIG_FILE_EXT', 'fig')

################################################################################
