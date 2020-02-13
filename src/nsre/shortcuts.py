from functools import reduce
from operator import add
from typing import Sequence

from .ast import AnyNumber, Final, Node
from .matchers import Anything, Eq


def seq(s: Sequence) -> Node:
    nodes = [Final(Eq(x)) for x in s]
    return reduce(add, nodes)


def anything() -> Node:
    return AnyNumber(Final(Anything()))
