"""Unit tests for the termination.signatures module."""

from unittest import TestCase

from termination.signatures import Signature, arity, constant, variable
from termination.terms import Constant, Function, Variable


class TestSignature(TestCase):
    """Test case for the Signature class."""

    class SimpleSignature(Signature):
        """Simple signature for testing."""

        f = arity(2)
        g = arity(1)
        a = constant()
        b = constant()
        x = variable()
        y = variable()

    def test_signature(self):
        """A Signature can be instantiated."""
        self.SimpleSignature()

    def test_signature_descriptors(self):
        """A Signature's symbols are created correctly."""
        s = self.SimpleSignature()

        with self.subTest(name="f"):
            self.assertIsInstance(s.f, Function)
            self.assertEqual(s.f.name, "f")
            self.assertEqual(s.f.arity, 2)

        with self.subTest(name="g"):
            self.assertIsInstance(s.g, Function)
            self.assertEqual(s.g.name, "g")
            self.assertEqual(s.g.arity, 1)

        with self.subTest(name="a"):
            self.assertIsInstance(s.a, Constant)
            self.assertEqual(s.a.name, "a")

        with self.subTest(name="b"):
            self.assertIsInstance(s.b, Constant)
            self.assertEqual(s.b.name, "b")

        with self.subTest(name="x"):
            self.assertIsInstance(s.x, Variable)
            self.assertEqual(s.x.name, "x")

        with self.subTest(name="y"):
            self.assertIsInstance(s.y, Variable)
            self.assertEqual(s.y.name, "y")
