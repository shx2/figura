"""
Unit-tests of the high-level config reading/building functionality.
"""

import unittest
from figura import read_config


################################################################################

class BasicTest(unittest.TestCase):

    # ============================================================================================
    # read_config
    # ============================================================================================

    def test_read_config(self):
        c = read_config('figura.tests.config.basic1')
        self.assertEqual(2, c.some_params.b)

    def test_read_config_directory(self):
        c = read_config('figura.tests.config')
        self.assertEqual(2, c.basic1.some_params.b)
        self.assertEqual('baz', c.more.xxx.foo.bar)
        self.assertEqual(1, c.deep1.conf1.attr1)
        self.assertEqual(2, c.deep1.deep2.conf2.attr2)

    def test_read_config_deep(self):
        c = read_config('figura.tests.config.basic1.some_params')
        self.assertEqual(2, c.b)

    # ============================================================================================
    # build_config
    # ============================================================================================

    # TBD Tests to be added


################################################################################
