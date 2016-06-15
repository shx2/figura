"""
A python package for parsing and working with `Figura <index.html>`_ config files.

This library also includes an executable ``figura_print`` command, for processing
your figura config files and generating your configuration, printing it as a JSON structure.
The generated JSON-structured configuration can then be read by programs written in
any other language (using its JSON parser).

In python code, simply use the `read_config <#figura.utils.read_config>`_ function for parsing
Figura config files into `ConfigContainer <#figura.container.ConfigContainer>`_ objects.
The `cli <#module-figura.cli>`_ module and the `build_config <#figura.utils.build_config>`_ function
are useful for integrating your python scripts with figura configurations and overrides, and combining
configurations and overrides into single ConfigContainer.

"""

from . import version

from .container import ConfigContainer
from .override import ConfigOverrideSet
from .errors import ConfigError, ConfigParsingError, ConfigValueError

from .utils import read_config, build_config
