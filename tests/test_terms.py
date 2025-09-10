"""Unit tests for the termination.terms module."""
# TODO: Test substitutions on different objects
# TODO: Test len() on different objects
# TODO: Test in on different objects
# TODO: Test Constant

from unittest import TestCase

from termination.terms import (
    Constant,
    Function,
    IndexedVariable,
    Substitution,
    Term,
    Variable,
    variables,
)


class TestFunction(TestCase):
    """Test case for the Function class."""

    def test_call(self):
        """A Function symbol can be called to create a Term."""
        f = Function(name="f", arity=2)
        x = Variable(name="x")
        y = Variable(name="y")
        term = f(x, y)

        self.assertIsInstance(term, Term)


class TestVariable(TestCase):
    """Test case for the Variable class."""

    def test_str(self):
        """A Variable formats as a string."""
        x = Variable(name="x")
        self.assertEqual(str(x), "?x")

    def test_getitem_root(self):
        """A Variable is its own root subterm."""
        x = Variable(name="x")
        self.assertIs(x[()], x)

    def test_getitem_invalid(self):
        """A Variable has no non-root position."""
        x = Variable(name="x")
        with self.assertRaises(KeyError):
            x[(0,)]

    def test_subterms(self):
        """A Variable supports iterating its subterms."""
        x = Variable(name="x")
        expected_subterm_set = {((), x)}
        actual_subterm_set = set(x.subterms())

        self.assertEqual(expected_subterm_set, actual_subterm_set)

    def test_positions(self):
        """A Variable supports iterating its positions."""
        x = Variable(name="x")
        expected_position_set = {()}
        actual_position_set = set(x.positions())

        self.assertEqual(expected_position_set, actual_position_set)

    def test_variables(self):
        """A Variable supports iterating its variables."""
        x = Variable(name="x")
        expected_variables = {x}
        actual_variables = set(variables(x))

        self.assertEqual(expected_variables, actual_variables)


class TestIndexedVariable(TestCase):
    """Test case for the IndexedVariable class."""

    def test_str(self):
        """An IndexedVariable formats as a string."""
        x = IndexedVariable(name="x", index=1)
        self.assertEqual(str(x), "?x#1")

    def test_getitem_root(self):
        """An IndexedVariable is its own root subterm."""
        x = IndexedVariable(name="x", index=1)
        self.assertIs(x[()], x)

    def test_getitem_invalid(self):
        """An IndexedVariable has no non-root position."""
        x = IndexedVariable(name="x", index=1)
        with self.assertRaises(KeyError):
            x[(0,)]

    def test_subterms(self):
        """An IndexedVariable supports iterating its subterms."""
        x = IndexedVariable(name="x", index=1)
        expected_subterm_set = {((), x)}
        actual_subterm_set = set(x.subterms())

        self.assertEqual(expected_subterm_set, actual_subterm_set)

    def test_positions(self):
        """An IndexedVariable supports iterating its positions."""
        x = IndexedVariable(name="x", index=1)
        expected_position_set = {()}
        actual_position_set = set(x.positions())

        self.assertEqual(expected_position_set, actual_position_set)

    def test_variables(self):
        """An IndexedVariable supports iterating its variables."""
        x = IndexedVariable(name="x", index=1)
        expected_variables = {x}
        actual_variables = set(variables(x))

        self.assertEqual(expected_variables, actual_variables)


class TestTerm(TestCase):
    """Test case for the Term class."""

    def setUp(self):
        """Set up useful stuff for testing."""
        self.f = Function("f", 2)
        self.g = Function("g", 1)

        self.x = Variable("x")
        self.y = Variable("y")
        self.z = Variable("z")

        self.g_subterm = Term(root=self.g, children=(self.x,))

        self.f_subterm = Term(root=self.f, children=(self.y, self.z))

        self.term = Term(root=self.f, children=(self.g_subterm, self.f_subterm))

    def test_getitem_root(self):
        """A Term is its own root subterm."""
        self.assertIs(self.term[()], self.term)

    def test_getitem_subterm(self):
        """A Term supports getting its subterms by position."""
        self.assertEqual(self.term[(0,)], self.g_subterm)
        self.assertEqual(self.term[(0, 0)], self.x)
        self.assertEqual(self.term[(1,)], self.f_subterm)
        self.assertEqual(self.term[(1, 0)], self.y)
        self.assertEqual(self.term[(1, 1)], self.z)

    def test_getitem_invalid(self):
        """A Term does not support getting invalid positions."""
        with self.assertRaises(KeyError):
            self.term[(2,)]
        with self.assertRaises(KeyError):
            self.term[(0, 1)]
        with self.assertRaises(KeyError):
            self.term[(1, 2)]
        with self.assertRaises(KeyError):
            self.term[(0, 0, 1)]

    def test_subterms(self):
        """A Term supports iterating its subterms."""
        expected_subterm_set = {
            ((), self.term),
            ((0,), self.g_subterm),
            ((0, 0), self.x),
            ((1,), self.f_subterm),
            ((1, 0), self.y),
            ((1, 1), self.z),
        }

        actual_subterm_set = set(self.term.subterms())

        self.assertEqual(expected_subterm_set, actual_subterm_set)

    def test_positions(self):
        """A Term supports iterating its positions."""
        expected_position_set = {(), (0,), (0, 0), (1,), (1, 0), (1, 1)}

        actual_position_set = set(self.term.positions())

        self.assertEqual(expected_position_set, actual_position_set)

    def test_variables(self):
        """A Term supports iterating its variables."""
        expected_variables = {self.x, self.y, self.z}
        actual_variables = set(variables(self.term))

        self.assertEqual(expected_variables, actual_variables)


class TestSubstitution(TestCase):
    """Test case for the Substitution class."""

    def setUp(self) -> None:
        """Set up useful stuff for testing."""
        self.f = Function("f", 2)
        self.g = Function("g", 1)

        self.a = Constant("a")
        self.b = Constant("b")
        self.c = Constant("c")

        self.x = Variable("x")
        self.y = Variable("y")
        self.z = Variable("z")

    def test_empty_str(self):
        """An empty substitution formats as a string."""
        sub = Substitution()
        expected_str = "{}"
        actual_str = str(sub)

        self.assertEqual(expected_str, actual_str)

    def test_nonempty_str(self):
        """A nonempty substitution formats as a string."""
        sub = Substitution(
            mapping={self.x: self.f(self.x, self.y), self.y: self.g(self.z)}
        )
        expected_str = "{?x -> f(?x, ?y), ?y -> g(?z)}"
        actual_str = str(sub)

        self.assertEqual(expected_str, actual_str)

    def test_substitute(self):
        """A substitution applies to another substitution."""
        inner_sub = Substitution(
            mapping={self.x: self.f(self.x, self.y), self.y: self.g(self.z)}
        )
        outer_sub = Substitution(
            mapping={self.x: self.a, self.y: self.b, self.z: self.c}
        )

        expected_sub = Substitution(
            mapping={
                self.x: self.f(self.a, self.b),
                self.y: self.g(self.c),
                self.z: self.c,
            }
        )
        actual_sub = outer_sub(inner_sub)

        self.assertEqual(expected_sub, actual_sub)
