from unittest import TestCase

from termination.terms import Symbol, Term, Variable, variables


class TestSymbol(TestCase):
    def test_call(self):
        f = Symbol('f', 2)
        x = Variable('x')
        y = Variable('y')
        term = f(x, y)

        self.assertIsInstance(term, Term)


class TestVariable(TestCase):
    def test_str(self):
        x = Variable('x')
        self.assertEqual(str(x), '?x')

    def test_getitem_root(self):
        x = Variable('x')
        self.assertEqual(x[()], x)

    def test_getitem_invalid(self):
        x = Variable('x')
        with self.assertRaises(IndexError):
            x[(0,)]


class TestTerm(TestCase):
    def setUp(self):
        self.symbols = {
            'f': Symbol('f', 2),
            'g': Symbol('g', 1),
            'a': Symbol('a'),
            'b': Symbol('b')
        }
        self.vars = {
            'x': Variable('x'),
            'y': Variable('y'),
            'z': Variable('z')
        }
        self.g_subterm = Term(
            root=self.symbols['g'],
            children=(self.vars['x'],)
        )
        self.f_subterm = Term(
            root=self.symbols['f'],
            children=(self.vars['y'], self.vars['z'])
        )
        self.term = Term(
            root=self.symbols['f'],
            children=(self.g_subterm, self.f_subterm)
        )

    def test_getitem_root(self):
        self.assertEqual(self.term[()], self.term)

    def test_getitem_subterm(self):
        self.assertEqual(self.term[(0,)], self.g_subterm)
        self.assertEqual(self.term[(0,0)], self.vars['x'])
        self.assertEqual(self.term[(1,)], self.f_subterm)
        self.assertEqual(self.term[(1,0)], self.vars['y'])
        self.assertEqual(self.term[(1,1)], self.vars['z'])

    def test_getitem_invalid(self):
        with self.assertRaises(IndexError):
            self.term[(2,)]
        with self.assertRaises(IndexError):
            self.term[(0,1)]
        with self.assertRaises(IndexError):
            self.term[(1,2)]
        with self.assertRaises(IndexError):
            self.term[(0,0,1)]

    def test_subterms(self):
        expected_subterm_set = {
            ((), self.term),
            ((0,), self.g_subterm),
            ((0,0), self.vars['x']),
            ((1,), self.f_subterm),
            ((1,0), self.vars['y']),
            ((1,1), self.vars['z'])
        }

        actual_subterm_set = set(self.term.subterms())

        self.assertEqual(expected_subterm_set, actual_subterm_set)

    def test_variables(self):
        expected_variables = {
            self.vars['x'],
            self.vars['y'],
            self.vars['z']
        }
        actual_variables = set(variables(self.term))

        self.assertEqual(expected_variables, actual_variables)
