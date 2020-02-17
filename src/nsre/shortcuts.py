from functools import reduce
from operator import add
from typing import Sequence

from .ast import AnyNumber, Final, Node
from .matchers import Anything, Eq


def seq(s: Sequence) -> Node:
    """
    Converts a sequence of items into concatenated Eq matchers. Useful to
    match a string exactly.

    >>> from nsre import *
    >>> re = RegExp.from_ast(seq('foo'))
    >>> assert re.match('foo')
    >>> assert not re.match('bar')

    Parameters
    ----------
    s
        Sequence to convert into AST
    """

    nodes = [Final(Eq(x)) for x in s]
    return reduce(add, nodes)


def anything() -> Node:
    """
    Matches anything. Conceptual equivalent of ".*" in regular regular
    expressions.
    """

    return AnyNumber(Final(Anything()))


__all__ = ["seq", "anything"]
