"""
Unit-tests of the high-level config reading/building functionality.
"""

import unittest
from figura import read_config

################################################################################

# Tests use ".fig" extension. Enable it:
from figura.settings import set_extension_fig as _setfig
_setfig()

################################################################################

class BasicTest(unittest.TestCase):

    #===================================================================================================================
    # read_config
    #===================================================================================================================

    def test_read_config(self):
        c = read_config('figura.tests.config.basic1')
        self.assertEqual(2, c.some_params.b)
    
    def test_read_config_directory(self):
        c = read_config('figura.tests.config')
        self.assertEqual(2, c.basic1.some_params.b)
        self.assertEqual('baz', c.more.xxx.foo.bar)

    def test_read_config_deep(self):
        c = read_config('figura.tests.config.basic1.some_params')
        self.assertEqual(2, c.b)

    #===================================================================================================================
    # build_config
    #===================================================================================================================
    
    # Tests to be added
    

################################################################################

if __name__ == '__main__':
    unittest.main()

################################################################################
