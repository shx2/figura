"""
Running the self-contained unit-tests, i.e. config files containing
sections which are marked with is_unittest=True, which define what tests
to run on the configs in that file.
"""

import copy
import unittest

from figura import read_config, ConfigContainer

################################################################################

UNITTEST_FILE_PATH_PREFIX = 'figura.tests.config.'

################################################################################

class BasicTest(unittest.TestCase):
    
    # make sure assertion messages include both the default message, and the
    # specialized message we pass along.
    longMessage = True
    
    #===================================================================================================================
    # utility functions
    #===================================================================================================================
    
    def assertConfigEqual(self, config1, config2, testname, key = 'ROOT'):
        #print(config1)
        if isinstance(config1, ConfigContainer) and isinstance(config2, ConfigContainer):
            self.assertSetEqual(
                set(config1.keys()), set(config2.keys()),
                msg = '[{%s} set of params at key=%s]' % (testname, key)
            )
            # recursively apply to sub containers
            for k in config1.keys():
                subkey = '%s.%s' % (key, k) if key else k
                self.assertConfigEqual(config1[k], config2[k], testname, key = subkey)
        else:
            self.assertEqual(config1, config2, '[{%s} value of param at key=%s]' % (testname, key))
    
    #===================================================================================================================
    # The main functions running the self-contained tests
    #===================================================================================================================
    
    def run_self_contained(self, path):
        # parse the figura file
        tests, data = self.parse(path)
        assert tests
        # run each test:
        for test in tests:
            #print('RUNNING %s / %s' % (path, test.name))
            self.run_single_test(test, data)

    def run_single_test(self, test, data):
        data = copy.deepcopy(data)
        
        # construct
        test_input = data
        entry_point = test.construct.get('entry_point')
        if entry_point:
            test_input = test_input.deep_getattr(entry_point)
        for base_path, ov_path in test.construct.get('apply_overrides', []):
            data.deep_getattr(base_path).apply_overrides(data.deep_getattr(ov_path))
        
        # verify
        test_output = data.deep_getattr(test.verify.entry_point)
        self.assertConfigEqual(test_input, test_output, test.name)

    def parse(self, path):
        # load the figura file
        data = read_config(UNITTEST_FILE_PATH_PREFIX + path)
        # extract test definitions
        tests = []
        for k, v in list(data.items()):
            if getattr(v, 'is_unittest', False):
                v.name = k
                tests.append(v)
                data.pop(k)
        return tests, data
        
    
    #===================================================================================================================
    # A test method per self-contained unittest
    #===================================================================================================================
    
    def test_basic1(self):
        return self.run_self_contained('basic1')
    def test_overlay(self):
        return self.run_self_contained('overlay')
    def test_override(self):
        return self.run_self_contained('override')
    

################################################################################

if __name__ == '__main__':
    unittest.main()

################################################################################
