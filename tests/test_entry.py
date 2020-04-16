"""
Unit-tests of the __entry_point__ directive.
"""

import unittest
from figura import read_config


################################################################################

class BasicTest(unittest.TestCase):

    def test_entry_point_by_ref(self):
        c = read_config('figura.tests.config.entry1')
        self.assertEqual(2, c.b)  # __entry_point__ skips the some_params name

    def test_entry_point_by_name(self):
        c = read_config('figura.tests.config.entry2')
        self.assertEqual(2, c.b)  # __entry_point__ skips the some_params name

    def test_entry_point_by_explicity_definition(self):
        c = read_config('figura.tests.config.entry3')
        self.assertEqual(2, c.b)


################################################################################

if __name__ == '__main__':
    unittest.main()

################################################################################
