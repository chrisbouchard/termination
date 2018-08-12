from unittest import TestCase

from termination.terms import Symbol, Term, Variable, variables

class TestTerm(TestCase):
    def test_symbol_call(self):
        f = Symbol('f', 2)
        x = Variable('x')
        y = Variable('y')
        z = Variable('z')
        t = f(x, f(y, z))

        self.assertIsInstance(t, Term)

    def test_subterms(self):
        f = Symbol('f', 2)
        x = Variable('x')
        y = Variable('y')
        z = Variable('z')
        t = f(x, f(y, z))

        expected_subterm_set = {
            ((), t),
            ((0,), x),
            ((1,), f(y, z)),
            ((1,0), y),
            ((1,1), z)
        }

        actual_subterm_set = set(t.subterms())

        self.assertEqual(expected_subterm_set, actual_subterm_set)

    def test_variables(self):
        f = Symbol('f', 2)
        x = Variable('x')
        y = Variable('y')
        z = Variable('z')
        t = f(x, f(y, z))

        expected_variables = { x, y, z }
        actual_variables = set(variables(t))

        self.assertEqual(expected_variables, actual_variables)
