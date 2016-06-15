#! /usr/bin/env python3
"""
A script for auto-generating guides, such as "guide" and "tutorial" from the
snippets contained in the guide directories (docs/guide/ and docs/tutorial).
"""

import os
import subprocess
import argparse
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    
###############################################################################
# functions

def process_part(guide_dir, part):
    OUT = StringIO()

    def echo(*args, **kwargs):
        print(*args, file=OUT, **kwargs)

    def add_raw(suffix):
        path = os.path.join(guide_dir, '%s.%s.rst' % (part, suffix))
        if os.path.exists(path):
            with open(path) as F:
                echo(F.read() + '\n')
    
    ############################
    # pre
    ############################
    add_raw('pre')

    ############################
    # config file
    ############################
    config_path = os.path.join(guide_dir, '%s.py' % part)
    cmd_path = os.path.join(guide_dir, '%s.cmd' % part)
    if os.path.exists(config_path) or os.path.exists(cmd_path):
        config_display_path = os.path.basename(config_path)
        config_import_path = config_display_path[:-3]  # strip ".py" suffix
        # show config file's contents:
        if os.path.exists(config_path):
            echo('::')
            echo('')
            echo(indent_lines('    ', '> cat %s' % config_display_path))
            with open(config_path) as F:
                echo(indent_lines('    ', F.read()))
                echo('')
        # show as json:
        if os.path.exists(cmd_path):
            with open(cmd_path) as F:
                lines = F.read().splitlines()
            msgs_and_cmds = list(zip(lines[::2], lines[1::2]))
        else:
            msg = 'When processed and formatted as JSON'
            cmd = 'figura_print %s' % config_import_path
            msgs_and_cmds = [ (msg, cmd) ]
        for msg, cmd in msgs_and_cmds:
            echo('%s::' % msg)
            echo('')
            echo(indent_lines('    ', '> %s' % cmd))
            echo(indent_lines('    ', run_cmd(cmd, pythonpath = guide_dir)))
            echo('')

    ############################
    # post
    ############################
    add_raw('post')
    
    return OUT.getvalue()
    
def indent_lines(indent, multiline_string):
    return '\n'.join( indent + line for line in multiline_string.splitlines() )

def run_cmd(cmd, pythonpath):
    out = subprocess.check_output('PYTHONPATH=%s %s' % (pythonpath, cmd), shell=True)
    return out.decode("utf-8") 
    

###############################################################################
# MAIN

def main():
    
    args = getopt()
    guide_type, = args.guide_type
    
    # figure out locations, and add to sys.path
    here = os.path.dirname(os.path.abspath(__file__))
    guide_dir = os.path.join(here, guide_type)
    output_file = args.output_file
    if not output_file:
        output_file = os.path.join(here, '%s.rst' % guide_type)
    
    # find files to process:
    part_names = sorted(set( f.split('.')[0] for f in os.listdir(guide_dir) if not f.startswith('_') ))
    with open(output_file, 'w') as OUT:
        for part in part_names:
            snippet = process_part(guide_dir, part)
            print(snippet + '\n\n', file = OUT)

###############################################################################

def getopt():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('guide_type', nargs = 1)
    parser.add_argument('-o', '--output-file', help = 'defaults to "<guide_type>.rst"')
    
    return parser.parse_args()

###############################################################################

if __name__ == '__main__':
    main()
