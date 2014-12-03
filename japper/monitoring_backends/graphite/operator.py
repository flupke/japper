from __future__ import absolute_import
import operator

from enumfields import Enum


class Operator(Enum):

    lt = 0
    le = 1
    eq = 2
    ne = 3
    ge = 4
    gt = 5

    class Labels:
        lt = '<'
        le = '<='
        eq = '=='
        ne = '!='
        ge = '>='
        gt = '>'

    def __call__(self, a, b):
        return operator_funcs[self.value](a, b)


# Operator values => operator.func map, take care of preserving indices here
operator_funcs = [
    operator.lt,
    operator.le,
    operator.eq,
    operator.ne,
    operator.ge,
    operator.gt,
]
