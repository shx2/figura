"""
Unit-tests of the import and reloading functionality.
"""

import sys
import os
import shutil
import unittest
import tempfile
import errno

from figura import read_config

################################################################################

TEMPDIR_NAME = 'figura_%s'% os.getpid()
TEMPDIR = os.path.join(tempfile.gettempdir(), TEMPDIR_NAME)
BASEDIR = os.path.dirname(__file__)
CONFIGDIR = os.path.join(BASEDIR, 'config')

sys.path.append(TEMPDIR)

################################################################################

class BasicTest(unittest.TestCase):

    #===================================================================================================================
    # setup / teardown
    #===================================================================================================================
    
    def setup_temp_dir(self, tempdir):
        for dir in [ TEMPDIR, tempdir ]:
            # create temp dir
            mkdir_p(dir)
            # touch __init__.py
            with open(os.path.join(dir, '__init__.py'), 'w'):
                pass

    def tearDown(self):
        # delete temp dir
        shutil.rmtree(TEMPDIR)
    
    #===================================================================================================================
    # utility functions
    #===================================================================================================================
    
    def tempify_config(self, config_name, desc):
        config_name += '.py'
        tempdir = os.path.join(TEMPDIR, desc)
        self.setup_temp_dir(tempdir)
        src = os.path.join(CONFIGDIR, config_name)
        dst = os.path.join(tempdir, config_name)
        shutil.copyfile(src, dst)
        return dst
    
    #===================================================================================================================
    # reloading
    #===================================================================================================================
    
    def test_reload_import_path(self):
        desc = 'test_reload_import_path'
        config_name = 'importee'
        filepath = self.tempify_config(config_name, desc)
        importpath = '.'.join([desc, config_name])
        self._test_reload(importpath, filepath)

    def test_reload_indirect_import_path(self):
        desc = 'test_reload_indirect_import_path'
        # "importer" imports "importee" -- loading "importer", but modifying "importee"
        filepath1 = self.tempify_config('importee', desc)
        self.tempify_config('importer', desc)
        importpath2 = '.'.join((desc, 'importer'))
        self._test_reload(importpath2, filepath1)

    # NOTE: loading by file-path is currently not supported
    
    #def test_reload_file_path(self):
    #    config_name = 'importee'
    #    filepath = self.tempify_config(config_name, 'test_reload_file_path')
    #    self._test_reload(filepath, filepath)
    #
    #def test_reload_indirect_file_path(self):
    #    # "importer" imports "importee" -- loading "importer", but modifying "importee"
    #    filepath1 = self.tempify_config('importee', 'test_reload_indirect_file_path')
    #    filepath2 = self.tempify_config('importer', 'test_reload_indirect_file_path')
    #    self._test_reload(filepath2, filepath1)

    #===================================================================================================================

    def _test_reload(self, path_to_reload, filepath_to_modify):
        config = read_config(path_to_reload).some_params
        self.assertEqual(config.a, 1)
        self.assertRaises(KeyError, lambda: config['z'])
        self.assertRaises(AttributeError, lambda: config.z)
        self.assertRaises(AttributeError, lambda: config.zz)
        # inject a new value, and reload (indented, to put it inside some_params)
        append_line(filepath_to_modify, '    z = 999')
        config = read_config(path_to_reload).some_params
        self.assertEqual(config.a, 1)
        self.assertEqual(config.z, 999)
        self.assertRaises(AttributeError, lambda: config.zz)
        # inject yet another value, and reload (indented, to put it inside some_params)
        append_line(filepath_to_modify, '    zz = 555')
        config = read_config(path_to_reload).some_params
        self.assertEqual(config.a, 1)
        self.assertEqual(config.z, 999)
        self.assertEqual(config.zz, 555)
    
        
def append_line(filename, line):
    with open(filename, 'a') as f:
        f.write('\n' + line + '\n')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

################################################################################

if __name__ == '__main__':
    unittest.main()

################################################################################
