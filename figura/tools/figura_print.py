#! /usr/bin/env python
"""
Read a Figura config file, and print the config in JSON format.

Usage
------

By "python-import" path::
    
    % python figura_print.py figura.tests.config.basic1.some_params --override a=a_new_value

By file path: not support currently.

"""

import argparse

from figura import build_config, ConfigContainer
from figura.cli import add_override_argument

###############################################################################

FORMAT_MAP = dict(
    json = 'to_json',
    python = 'to_python_string',
)

###############################################################################
# MAIN

def main():
    args = getopt()
    paths = args.configfile + args.overridefile
    
    config = build_config(*paths, enforce_override_set = False)

    if args.override:
        config.apply_overrides(args.override)

    if isinstance(config, ConfigContainer):
        # format the container and print it:
        formatter_method = FORMAT_MAP[args.format]
        print(getattr(config, formatter_method)())
    else:
        # an atomic value. just print it:
        print(config)
            
###############################################################################

def getopt():

    parser = argparse.ArgumentParser(
        description='Read a figura file and print the configuration it defines')

    parser.add_argument('configfile', nargs = 1, help = \
                        '''a figura config file, or its python-import path''')

    parser.add_argument('overridefile', nargs = '*', help = \
                        '''figura files with override-sets, or their python-import path''')

    add_override_argument(parser)
    
    parser.add_argument('-f', '--format', default = 'json', choices = FORMAT_MAP.keys(),
                        help = '''The format of the output. defaults to 'json''')
    
    args = parser.parse_args()

    return args

###############################################################################

if __name__ == '__main__':
    main()
