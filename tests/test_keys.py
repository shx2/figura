"""
Unit-tests of config-container usages involving "weird" keys, e.g.
keys with periods in them.
"""

import unittest
from figura import read_config, ConfigContainer, ConfigOverrideSet

################################################################################

class BasicTest(unittest.TestCase):

    def test_period_attr_access(self):
        c = ConfigContainer()
        c['x.y'] = 5
        self.assertIn('x.y', c)
        self.assertNotIn('x', c)
        self.assertEqual(c['x.y'], 5)
    
    def test_period_escaping_override(self):
        c = ConfigContainer.from_dict({'a': {'b': {}}})
        ov = ConfigOverrideSet.from_dict({'x__y': 5})
        c.apply_overrides(ov)
        self.assertIn('x.y', c)
        self.assertNotIn('x', c)
        self.assertEqual(c['x.y'], 5)
        ov = ConfigOverrideSet.from_dict({'a.b.xx__yy': 55})
        c.apply_overrides(ov)
        self.assertIn('xx.yy', c.a.b)
        self.assertNotIn('xx', c.a.b)
        self.assertEqual(c.a.b['xx.yy'], 55)
        
    def test_period_escaping_config_file(self):
        c = read_config('figura.tests.config.escape')
        self.assertIn('a.b', c)
        self.assertNotIn('a', c)
        self.assertEqual(c['a.b'], 'x')
        self.assertIn('d.e', c.c)
        self.assertNotIn('d', c.c)
        self.assertEqual(c.c['d.e'], 'z')
        ov = ConfigOverrideSet.from_dict({'c.d__e': 'DE', 'c.d': 'D'})
        c.apply_overrides(ov)
        self.assertEqual(c.c['d.e'], 'DE')
        self.assertEqual(c.c.d, 'D')


################################################################################

if __name__ == '__main__':
    unittest.main()

################################################################################
