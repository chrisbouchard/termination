from unittest import TestCase

from termination.pools import VariablePool, fresh
from termination.terms import IndexedVariable, Variable


class TestPool(TestCase):
    def test_create(self):
        pool = VariablePool()

    def test_get(self):
        pool = VariablePool()

        x = pool.get('x')
        y = pool.get('y')
        z1 = pool.get('z', 1)
        z2 = pool.get('z', 2)

        self.assertIsInstance(x, Variable)
        self.assertEqual('x', x.name)
        self.assertIsInstance(y, Variable)
        self.assertEqual('y', y.name)
        self.assertIsInstance(z1, IndexedVariable)
        self.assertEqual('z', z1.name)
        self.assertEqual(1, z1.index)
        self.assertIsInstance(z2, IndexedVariable)
        self.assertEqual('z', z2.name)
        self.assertEqual(2, z2.index)

    def test_getitem(self):
        pool = VariablePool()

        x = pool['x']
        y = pool['y']

        self.assertIsInstance(x, Variable)
        self.assertEqual('x', x.name)
        self.assertIsInstance(y, Variable)
        self.assertEqual('y', y.name)

    def test_getitem_singleton(self):
        pool = VariablePool()

        x1 = pool['x']
        y1 = pool['y']
        x2 = pool['x']
        y2 = pool['y']

        self.assertIs(x1, x2)
        self.assertIs(y1, y2)

    def test_fresh(self):
        pool = VariablePool()

        x1 = pool.fresh('x')
        x2 = pool.fresh('x')
        y1 = pool.fresh('y')
        x3 = pool.fresh('x')
        y2 = pool.fresh('y')

        self.assertIsInstance(x1, IndexedVariable)
        self.assertEqual('x', x1.name)
        self.assertEqual(1, x1.index)
        self.assertIsInstance(x2, IndexedVariable)
        self.assertEqual('x', x2.name)
        self.assertEqual(2, x2.index)
        self.assertIsInstance(x3, IndexedVariable)
        self.assertEqual('x', x3.name)
        self.assertEqual(3, x3.index)
        self.assertIsInstance(y1, IndexedVariable)
        self.assertEqual('y', y1.name)
        self.assertEqual(1, y1.index)
        self.assertIsInstance(y2, IndexedVariable)
        self.assertEqual('y', y2.name)
        self.assertEqual(2, y2.index)


class TestFresh(TestCase):
    def test_fresh_variable(self):
        pool = VariablePool()
        x = pool['x']

        x1 = fresh(x)
        x2 = fresh(x)

        self.assertIsInstance(x1, IndexedVariable)
        self.assertEqual('x', x1.name)
        self.assertEqual(1, x1.index)
        self.assertIsInstance(x2, IndexedVariable)
        self.assertEqual('x', x2.name)
        self.assertEqual(2, x2.index)

    def test_indexed_variable(self):
        pool = VariablePool()
        x = pool['x']

        x1 = fresh(x)
        x2 = fresh(x1)

        x10 = pool.get('x', 10)

        x11 = fresh(x1)

        self.assertIsInstance(x1, IndexedVariable)
        self.assertEqual('x', x1.name)
        self.assertEqual(1, x1.index)
        self.assertIsInstance(x2, IndexedVariable)
        self.assertEqual('x', x2.name)
        self.assertEqual(2, x2.index)
        self.assertIsInstance(x11, IndexedVariable)
        self.assertEqual('x', x11.name)
        self.assertEqual(11, x11.index)

    def test_fresh_pool(self):
        pool = VariablePool()

        v1 = fresh(pool)
        v2 = fresh(pool)

        self.assertIsInstance(v1, IndexedVariable)
        self.assertEqual('', v1.name)
        self.assertEqual(1, v1.index)
        self.assertIsInstance(v2, IndexedVariable)
        self.assertEqual('', v2.name)
        self.assertEqual(2, v2.index)

    def test_fresh_throws(self):
        x = Variable('x')
        y1 = IndexedVariable('y', 1)
        z = 5

        with self.assertRaises(ValueError):
            fresh(x)

        with self.assertRaises(ValueError):
            fresh(y1)

        with self.assertRaises(ValueError):
            fresh(z)
