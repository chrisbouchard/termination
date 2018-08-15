from unittest import TestCase

from termination.pools import fresh_variable
from termination.signatures import Signature, arity, constant, variable
from termination.terms import Constant, Function, Term, Variable


class TestSignature(TestCase):
    class SimpleSignature(Signature):
        f = arity(2)
        g = arity(1)
        a = constant()
        b = constant()
        x = variable()
        y = variable()

    def test_signature(self):
        self.SimpleSignature()

    def test_signature_descriptors(self):
        s = self.SimpleSignature()

        with self.subTest(name='f'):
            self.assertIsInstance(s.f, Function)
            self.assertEqual(s.f.name, 'f')
            self.assertEqual(s.f.arity, 2)

        with self.subTest(name='g'):
            self.assertIsInstance(s.g, Function)
            self.assertEqual(s.g.name, 'g')
            self.assertEqual(s.g.arity, 1)

        with self.subTest(name='a'):
            self.assertIsInstance(s.a, Constant)
            self.assertEqual(s.a.name, 'a')

        with self.subTest(name='b'):
            self.assertIsInstance(s.b, Constant)
            self.assertEqual(s.b.name, 'b')

        with self.subTest(name='x'):
            self.assertIsInstance(s.x, Variable)
            self.assertEqual(s.x.name, 'x')

        with self.subTest(name='y'):
            self.assertIsInstance(s.y, Variable)
            self.assertEqual(s.y.name, 'y')
