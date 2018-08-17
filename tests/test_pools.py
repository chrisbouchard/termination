"""Unit tests for the termination.pools module."""


from unittest import TestCase

from termination.pools import VariablePool, fresh_variable
from termination.terms import IndexedVariable, Variable


class TestPool(TestCase):
    """Test case for the VariblePool class."""

    def test_create(self):
        """A variable pool can be instantiated."""
        VariablePool()

    def test_get(self):
        """A VariablePool can get variables."""
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
        """A VariablePool can get variables using bracket ['x'] notation."""
        pool = VariablePool()

        x = pool['x']
        y = pool['y']

        self.assertIsInstance(x, Variable)
        self.assertEqual('x', x.name)
        self.assertIsInstance(y, Variable)
        self.assertEqual('y', y.name)

    def test_getitem_singleton(self):
        """A VariablePool returns the same variable instance."""
        pool = VariablePool()

        x1 = pool['x']
        y1 = pool['y']
        x2 = pool['x']
        y2 = pool['y']

        self.assertIs(x1, x2)
        self.assertIs(y1, y2)

    def test_fresh(self):
        """A VariablePool can generate "fresh" variables.

        Fresh variables have a unique index from any other index of a variable
        with the same name returned from that VariablePool.
        """
        pool = VariablePool()

        x1 = pool.get_fresh('x')
        x2 = pool.get_fresh('x')
        y1 = pool.get_fresh('y')
        x3 = pool.get_fresh('x')
        y2 = pool.get_fresh('y')

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

    def test_independent_pools(self):
        """Different VariablePools have independent fresh indices."""
        pool1 = VariablePool()
        pool2 = VariablePool()

        x1_1 = pool1.get_fresh('x')
        x1_2 = pool1.get_fresh('x')
        x2_1 = pool2.get_fresh('x')
        x1_3 = pool1.get_fresh('x')
        x2_2 = pool2.get_fresh('x')

        self.assertEqual(1, x1_1.index)
        self.assertEqual(2, x1_2.index)
        self.assertEqual(3, x1_3.index)
        self.assertEqual(1, x2_1.index)
        self.assertEqual(2, x2_2.index)


class TestFreshVariable(TestCase):
    """Test case for the fresh_variabe function."""

    def test_fresh_variable(self):
        """The fresh_variable function works on variables from a pool."""
        pool = VariablePool()
        x = pool['x']

        x1 = fresh_variable(x)
        x2 = fresh_variable(x)

        self.assertIsInstance(x1, IndexedVariable)
        self.assertEqual('x', x1.name)
        self.assertEqual(1, x1.index)
        self.assertIsInstance(x2, IndexedVariable)
        self.assertEqual('x', x2.name)
        self.assertEqual(2, x2.index)

    def test_indexed_variable(self):
        """The fresh_variable function works on indexed variables from a pool."""
        pool = VariablePool()
        x = pool['x']

        x1 = fresh_variable(x)
        x2 = fresh_variable(x1)

        pool.get('x', 10)

        x11 = fresh_variable(x1)

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
        """The fresh_variable function works on a VariablePool."""
        pool = VariablePool()

        v1 = fresh_variable(pool)
        v2 = fresh_variable(pool)

        self.assertIsInstance(v1, IndexedVariable)
        self.assertEqual('', v1.name)
        self.assertEqual(1, v1.index)
        self.assertIsInstance(v2, IndexedVariable)
        self.assertEqual('', v2.name)
        self.assertEqual(2, v2.index)

    def test_fresh_throws(self):
        """The fresh_variable function throws for non-pool objects.

        For variables that were not generated by a VariablePool, and for other
        random objects, fresh_variable should raise a ValueError.
        """
        x = Variable('x')
        y1 = IndexedVariable('y', 1)
        z = 5

        with self.assertRaises(ValueError):
            fresh_variable(x)

        with self.assertRaises(ValueError):
            fresh_variable(y1)

        with self.assertRaises(ValueError):
            fresh_variable(z)

    def test_fresh_shares_index(self):
        """The fresh_variable function uses the same fresh index as get_fresh."""
        pool = VariablePool()
        x = pool['x']

        x1 = fresh_variable(x)
        x2 = pool.get_fresh('x')
        x3 = fresh_variable(x)

        self.assertEqual(1, x1.index)
        self.assertEqual(2, x2.index)
        self.assertEqual(3, x3.index)
