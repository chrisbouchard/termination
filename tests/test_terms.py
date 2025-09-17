"""Unit tests for the termination.terms module."""
# TODO: Test substitutions on different objects
# TODO: Test len() on different objects
# TODO: Test in on different objects
# TODO: Test Constant

import pytest

from termination.terms import (
    Constant,
    Function,
    IndexedVariable,
    Substitution,
    Term,
    Variable,
    variables,
)


class TestFunction:
    """Test cases for the Function class."""

    def test_call(self):
        """A Function symbol can be called to create a Term."""
        f = Function(name="f", arity=2)
        x = Variable(name="x")
        y = Variable(name="y")

        assert isinstance(f(x, y), Term)

    def test_call_root(self):
        """Calling a function symbol creates a term with the symbol as the root."""
        f = Function(name="f", arity=2)
        x = Variable(name="x")
        y = Variable(name="y")

        assert f(x, y).root == f

    def test_call_children(self):
        """Calling a function symbol creates a term with the given children."""
        f = Function(name="f", arity=2)
        x = Variable(name="x")
        y = Variable(name="y")

        assert f(x, y).children == (x, y)


class TestVariable:
    """Test cases for the Variable class."""

    def test_str(self):
        """A Variable formats as a string."""
        x = Variable(name="x")
        assert str(x) == "?x"

    def test_getitem_root(self):
        """A Variable is its own root subterm."""
        x = Variable(name="x")
        assert x[()] is x

    def test_getitem_invalid(self):
        """A Variable has no non-root position."""
        x = Variable(name="x")
        with pytest.raises(KeyError):
            x[(0,)]

    def test_subterms(self):
        """A Variable supports iterating its subterms."""
        x = Variable(name="x")
        assert set(x.subterms()) == {((), x)}

    def test_positions(self):
        """A Variable supports iterating its positions."""
        x = Variable(name="x")
        assert set(x.positions()) == {()}

    def test_variables(self):
        """A Variable supports iterating its variables."""
        x = Variable(name="x")
        assert set(variables(x)) == {x}


class TestIndexedVariable:
    """Test cases for the IndexedVariable class."""

    def test_str(self):
        """An IndexedVariable formats as a string."""
        x = IndexedVariable(name="x", index=1)
        assert str(x) == "?x#1"

    def test_getitem_root(self):
        """An IndexedVariable is its own root subterm."""
        x = IndexedVariable(name="x", index=1)
        assert x[()] is x

    def test_getitem_invalid(self):
        """An IndexedVariable has no non-root position."""
        x = IndexedVariable(name="x", index=1)
        with pytest.raises(KeyError):
            x[(0,)]

    def test_subterms(self):
        """An IndexedVariable supports iterating its subterms."""
        x = IndexedVariable(name="x", index=1)
        assert set(x.subterms()) == {((), x)}

    def test_positions(self):
        """An IndexedVariable supports iterating its positions."""
        x = IndexedVariable(name="x", index=1)
        assert set(x.positions()) == {()}

    def test_variables(self):
        """An IndexedVariable supports iterating its variables."""
        x = IndexedVariable(name="x", index=1)
        assert set(variables(x)) == {x}


class TestTerm:
    """Test cases for the Term class."""

    f = Function("f", 2)
    g = Function("g", 1)

    x = Variable("x")
    y = Variable("y")
    z = Variable("z")

    @pytest.mark.parametrize(
        ("term", "expected_str"),
        [
            pytest.param(g(x), "g(?x)"),
            pytest.param(f(y, z), "f(?y, ?z)"),
            pytest.param(f(g(x), f(y, z)), "f(g(?x), f(?y, ?z))"),
        ],
    )
    def test_str(self, term, expected_str):
        """A Term is its own root subterm."""
        assert str(term) == expected_str

    @pytest.mark.parametrize(
        ("term",),
        [
            pytest.param(g(x)),
            pytest.param(f(y, z)),
            pytest.param(f(g(x), f(y, z))),
        ],
    )
    def test_getitem_root(self, term):
        """A Term is its own root subterm."""
        assert term[()] is term

    @pytest.mark.parametrize(
        ("term", "position", "expected_subterm"),
        [
            pytest.param(g(x), (0,), x),
            pytest.param(f(y, z), (0,), y),
            pytest.param(f(y, z), (1,), z),
            pytest.param(f(g(x), f(y, z)), (0,), g(x)),
            pytest.param(f(g(x), f(y, z)), (0, 0), x),
            pytest.param(f(g(x), f(y, z)), (1,), f(y, z)),
            pytest.param(f(g(x), f(y, z)), (1, 0), y),
            pytest.param(f(g(x), f(y, z)), (1, 1), z),
        ],
    )
    def test_getitem_subterm(self, term, position, expected_subterm):
        """A Term supports getting its subterms by position."""
        assert term[position] == expected_subterm

    @pytest.mark.parametrize(
        ("term", "position"),
        [
            pytest.param(f(g(x), f(y, z)), (2,)),
            pytest.param(f(g(x), f(y, z)), (0, 1)),
            pytest.param(f(g(x), f(y, z)), (1, 2)),
            pytest.param(f(g(x), f(y, z)), (0, 0, 1)),
        ],
    )
    def test_getitem_invalid(self, term, position):
        """A Term does not support getting invalid positions."""
        with pytest.raises(KeyError):
            term[position]

    @pytest.mark.parametrize(
        ("term", "expected_subterms"),
        [
            pytest.param(
                f(g(x), f(y, z)),
                {
                    ((), f(g(x), f(y, z))),
                    ((0,), g(x)),
                    ((0, 0), x),
                    ((1,), f(y, z)),
                    ((1, 0), y),
                    ((1, 1), z),
                },
            )
        ],
    )
    def test_subterms(self, term, expected_subterms):
        """A Term supports iterating its subterms."""
        assert set(term.subterms()) == expected_subterms

    @pytest.mark.parametrize(
        ("term", "expected_positions"),
        [
            pytest.param(
                f(g(x), f(y, z)),
                {(), (0,), (0, 0), (1,), (1, 0), (1, 1)},
            )
        ],
    )
    def test_positions(self, term, expected_positions):
        """A Term supports iterating its positions."""
        assert set(term.positions()) == expected_positions

    @pytest.mark.parametrize(
        ("term", "expected_variables"),
        [
            pytest.param(f(g(x), f(y, z)), {x, y, z}),
        ],
    )
    def test_variables(self, term, expected_variables):
        """A Term supports iterating its variables."""
        assert set(variables(term)) == expected_variables


class TestSubstitution:
    """Test case for the Substitution class."""

    f = Function("f", 2)
    g = Function("g", 1)

    a = Constant("a")
    b = Constant("b")
    c = Constant("c")

    x = Variable("x")
    y = Variable("y")
    z = Variable("z")

    @pytest.mark.parametrize(
        ("sub", "expected_str"),
        [
            pytest.param(Substitution(), "{}"),
            pytest.param(
                Substitution({x: f(x, y), y: g(z)}),
                "{?x -> f(?x, ?y), ?y -> g(?z)}",
            ),
        ],
    )
    def test_str(self, sub, expected_str):
        """A Substitution formats as a string."""
        assert str(sub) == expected_str

    @pytest.mark.parametrize(
        ("sub", "target", "expected"),
        [
            pytest.param(
                Substitution({x: a, y: b, z: c}),
                f(g(x), f(y, z)),
                f(g(a), f(b, c)),
            ),
            pytest.param(
                Substitution({x: a, y: b, z: c}),
                Substitution({x: f(x, y), y: g(z)}),
                Substitution({x: f(a, b), y: g(c), z: c}),
            ),
        ],
    )
    def test_substitute(self, sub, target, expected):
        """Calling a substitution applies it to the given value."""
        assert sub(target) == expected
