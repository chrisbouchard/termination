"""Unit tests for the termination.signatures module."""

import pytest

from termination.signatures import Signature, arity, constant, variable
from termination.terms import Constant, Function, Variable


class TestSignature:
    """Test case for the Signature class."""

    @pytest.fixture
    def signature_type(self, request):
        match request.param:
            case "SimpleSignature":

                class SimpleSignature(Signature):
                    f = arity(2)
                    g = arity(1)
                    a = constant()
                    b = constant()
                    x = variable()
                    y = variable()

                return SimpleSignature

        raise ValueError(f"Unrecognized signature name: {request.param}")

    @pytest.mark.parametrize(
        ("signature_type", "attr_name", "expected"),
        [
            pytest.param("SimpleSignature", "f", Function("f", arity=2)),
            pytest.param("SimpleSignature", "g", Function("g", arity=1)),
            pytest.param("SimpleSignature", "a", Constant("a")),
            pytest.param("SimpleSignature", "b", Constant("b")),
            pytest.param(
                "SimpleSignature",
                "x",
                Variable("x"),
                marks=pytest.mark.xfail(
                    reason="Variable and PoolVariable do not currently compare equal."
                ),
            ),
            pytest.param(
                "SimpleSignature",
                "y",
                Variable("y"),
                marks=pytest.mark.xfail(
                    reason="Variable and PoolVariable do not currently compare equal."
                ),
            ),
        ],
        indirect=("signature_type",),
    )
    def test_signature_descriptors(self, signature_type, attr_name, expected):
        """A Signature's symbols are created correctly."""
        signature = signature_type()
        assert getattr(signature, attr_name) == expected
