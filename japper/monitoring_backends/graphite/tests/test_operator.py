from ..operator import Operator


def test_operator():
    assert Operator.lt(0, 1)
    assert Operator.le(0, 1)
    assert not Operator.eq(0, 1)
    assert Operator.ne(0, 1)
    assert not Operator.ge(0, 1)
    assert not Operator.gt(0, 1)
