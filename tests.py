""" Tests for configure"""
from datetime import timedelta
from unittest import TestCase as BaseTestCase

import os
from os import path

from configure import Configuration, ConfigurationError, Factory

TEST_CONCAT_STRING = "base_test"


class A(object):

    def __init__(self, a, b=3):
        self.a = a
        self.b = b


def a(a, b=4):
    return A(a, b=b)


def kw(**kw):
    return kw


class TestCase(BaseTestCase):

    def config(self, v, ctx=None):
        return Configuration.from_string(v.strip(), ctx=ctx)

    def test_interpolation(self):
        c = self.config("""
a: "%(a)s"
b: "%(b)s"
        """, {"a": "aa", "b": "bb"})
        self.assertEqual(c.a, "aa")
        self.assertEqual(c.b, "bb")

    def test_ref(self):
        c = self.config("""
a: 1
b:
    c: !ref:a
    d: !ref:..a
e: !ref:.b
        """)
        self.assertEqual(c.a, 1)
        # self.assertEqual(c.e(c), c.b)
        # self.assertEqual(c.b.c(c.b), c.a)
        # self.assertEqual(c.b.d(c.b), c.a)

    def test_factory(self):
        c = self.config("""
a1:
    a: 1
a2:
    a: 2
    b: 4
a3:
    a: 3
a4:
    a: 4
    b: 5
        """)
        o = Factory(A, c.a1)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 1)
        self.assertEqual(o.b, 3)

        o = Factory(A, c.a2)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 2)
        self.assertEqual(o.b, 4)

        o = Factory(a, c.a3)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 3)
        self.assertEqual(o.b, 4)

        o = Factory(a, c.a4)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 4)
        self.assertEqual(o.b, 5)

    def test_factory_kw(self):
        c = self.config("""
a: !factory:tests.kw
    a: 4
    b: 5
        """)
        c.configure()
        self.assertTrue('a' in c.a)
        self.assertTrue('b' in c.a)

    def test_graph(self):
        c = self.config("""
a: !factory:tests.A
    a: 1
    b: !ref:.b
b: !factory:tests.a
    a: 3
        """)
        c.configure()
        self.assertTrue(isinstance(c.a, A))
        self.assertEqual(c.a.a, 1)
        self.assertTrue(isinstance(c.b, A))
        self.assertEqual(c.b.a, 3)
        self.assertTrue(isinstance(c.a.b, A))
        self.assertEqual(c.a.b.a, c.b.a)
        self.assertEqual(c.a.b.b, c.b.b)
        self.assertTrue(c.a.b is c.b)

    def test_obj(self):
        c = self.config("""
a: !obj:tests.A
b: !obj:tests.a
        """)
        c.configure()
        self.assertTrue(c.a is A)
        self.assertTrue(c.b is a)

    def test_concat(self):
        os.environ['TEST_CONCAT_ENVVAR_1_1'] = 'test_1'
        os.environ['TEST_CONCAT_ENVVAR_1_2'] = 'test_2'

        c = self.config("""
a: !concat tests.TEST_CONCAT_STRING "/test1"
b: !concat ENV:TEST_CONCAT_ENVVAR_1_1  '/test2' "/test3/" ENV:TEST_CONCAT_ENVVAR_1_2
        """)
        c.configure()
        self.assertEqual(c.a, "base_test/test1")
        self.assertEqual(c.b, "test_1/test2/test3/test_2")

    def test_concat_implicit_resolver(self):
        os.environ['TEST_CONCAT_ENVVAR_2_1'] = 'test_1'
        os.environ['TEST_CONCAT_ENVVAR_2_2'] = 'test_2'

        c = self.config("""
a: tests.TEST_CONCAT_STRING "/test1"
b: ENV:TEST_CONCAT_ENVVAR_2_1 '/test2' "/test3/" ENV:TEST_CONCAT_ENVVAR_2_2
        """)
        c.configure()
        self.assertEqual(c.a, "base_test/test1")
        self.assertEqual(c.b, "test_1/test2/test3/test_2")

    def test_load_from_file(self):
        filename = path.join(path.dirname(__file__), 'examples', 'example.default.conf')
        c = Configuration.from_file(filename)
        c.configure()

        self.assertEqual(c.a, 1)
        self.assertIsInstance(c.b, timedelta)
        self.assertEqual(c.b, timedelta(days=1))

    def test_load_from_file_inheritance(self):
        filename = path.join(path.dirname(__file__), 'examples', 'example.conf')
        c = Configuration.from_file(filename)
        c.configure()

        self.assertEqual(c.a, 100)
        self.assertIsInstance(c.b, timedelta)
        self.assertEqual(c.b, timedelta(days=1))
        self.assertEqual(c.c, "value")

    def test_envvar(self):
        os.environ['TEST_ENVVAR_1_1'] = 'test_1'
        os.environ['TEST_ENVVAR_1_2'] = 'test_2'
        c = self.config("""
a: !envvar TEST_ENVVAR_1_1
b: !envvar TEST_ENVVAR_1_2
        """)
        c.configure()
        self.assertEqual(c.a, "test_1")
        self.assertEqual(c.b, "test_2")

    def test_envvar_implicit_resolver(self):
        os.environ['TEST_ENVVAR_2_1'] = 'test_1'
        os.environ['TEST_ENVVAR_2_2'] = 'test_2'
        c = self.config("""
a: ENV:TEST_ENVVAR_2_1
b: ENV:TEST_ENVVAR_2_2
        """)
        c.configure()
        self.assertEqual(c.a, "test_1")
        self.assertEqual(c.b, "test_2")

    def test_envvar_with_default(self):
        c = self.config("""
a: !envvar TEST_ENVVAR_DEF_1?=1
b: !envvar TEST_ENVVAR_DEF_2?="test 2"
        """)
        c.configure()
        self.assertEqual(c.a, "1")
        self.assertEqual(c.b, "test 2")

    def test_envvar_with_default_none(self):
        c = self.config("""
a: !envvar TEST_ENVVAR_DEF_NONE?=
b: !envvar TEST_ENVVAR_DEF_EMPTY?=""
        """)
        c.configure()
        self.assertIsNone(c.a)
        self.assertEqual(c.b, "")

    def test_envvar_with_no_default(self):
        with self.assertRaises(ConfigurationError):
            c = self.config("""
a: !envvar TEST_ENVVAR_NO_DEF
            """)

    def test_envvar_implicit_resolver_with_default(self):
        c = self.config("""
a: ENV:TEST_ENVVAR_IMP_RESOLVER_DEF_1?=1
b: ENV:TEST_ENVVAR_IMP_RESOLVER_DEF_2?="test_2"
        """)
        c.configure()
        self.assertEqual(c.a, "1")
        self.assertEqual(c.b, "test_2")
