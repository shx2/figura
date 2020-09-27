import unittest

import figura

class TestConfigContainer(unittest.TestCase):
    def setUp(self):
        self.config = figura.ConfigContainer.from_dict(dict(foo=dict(bar=dict())))

    def test__coerce_type(self):
        new_value = figura.misc.coerce_type(1, "2")
        self.assertEqual(new_value, 2)

    def test_deep_setting(self):
        self.config.deep_setattr('foo.bar.baz', 1)
        self.assertEqual(self.config.deep_getattr('foo.bar.baz'), 1)
        self.assertEqual(self.config.foo.bar.baz, 1)

    def test_type_coercing(self):
        # int
        self.config.deep_setattr('int', 1)
        self.assertEqual(self.config.deep_getattr('int'), 1)
        self.config.deep_setattr('int', "2")
        self.assertEqual(self.config.deep_getattr('int'), 2)

        # float
        self.config.deep_setattr('float', 1.2)
        self.assertEqual(self.config.deep_getattr('float'), 1.2)
        self.config.deep_setattr('float', "2.3")
        self.assertEqual(self.config.deep_getattr('float'), 2.3)

        # bool
        self.config.deep_setattr('bool', False)
        self.assertEqual(self.config.deep_getattr('bool'), False)
        self.config.deep_setattr('bool', "True")
        self.assertEqual(self.config.deep_getattr('bool'), True)

        # list
        self.config.deep_setattr('list', [])
        self.assertEqual(self.config.deep_getattr('list'), [])
        self.config.deep_setattr('list', '1@,2')
        self.assertEqual(self.config.deep_getattr('list'), '1@,2')

        # string
        self.config.deep_setattr('string', 'foobarbaz')
        self.assertEqual(self.config.deep_getattr('string'), 'foobarbaz')
        self.config.deep_setattr('string', 'bazbarquux')
        self.assertEqual(self.config.deep_getattr('string'), 'bazbarquux')

        # arbitrary objects
        class Foo(object):
            pass
        o = Foo()
        self.config.deep_setattr('arbitrary_object', o)
        self.assertEqual(self.config.deep_getattr('arbitrary_object'), o)
        self.config.deep_setattr('arbitrary_object', "foobar")
        self.assertEqual(self.config.deep_getattr('arbitrary_object'), "foobar")


if __name__ == '__main__':
    unittest.main()