from dataclasses import dataclass, replace
from functools import reduce
from typing import Generic, Text, Union

from .matchers import Matcher, Out, Tok


@dataclass(frozen=True)
class Node(Generic[Tok, Out]):
    def __add__(self, other: "Node"):
        return Concatenation(self, other)

    def __or__(self, other: "Node"):
        return Alternation(self, other)

    def __getitem__(self, item: Text):
        if not isinstance(item, Text):
            raise KeyError("Cannot capture with a key other than a string")

        return Capture(name=item, statement=self)

    def __mul__(self, other: Union[int, slice]):
        if isinstance(other, int):
            if other < 1:
                raise ValueError("Cannot repeat item a negative number of times")

            return reduce(lambda a, b: a + b, [replace(self) for _ in range(0, other)])
        elif isinstance(other, slice):
            parts = []

            if isinstance(other.start, int) and other.start > 0:
                parts.append(self * other.start)
            elif other.start is None or other.start == 0:
                pass
            else:
                raise ValueError("Start of slice does not look valid")

            if isinstance(other.stop, int):
                for _ in range(other.start or 0, other.stop):
                    parts.append(Maybe(replace(self)))
            elif other.stop is None:
                parts.append(AnyNumber(replace(self)))
            else:
                raise ValueError("End of slice does not look valid")

            return reduce(lambda a, b: a + b, parts)
        else:
            raise ValueError("Multiply either with an int or a slice")

    def copy(self):
        return replace(self)


# noinspection PyUnresolvedReferences
class CopyLeftRightMixin:
    def copy(self):
        return self.__class__(self.left.copy(), self.right.copy())


# noinspection PyUnresolvedReferences
class CopyStatementMixin:
    def copy(self):
        return self.__class__(self.statement)


class DumbHash:
    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self is other


@dataclass(frozen=True, eq=False)
class Final(DumbHash, Node):
    statement: Matcher[Tok, Out]


@dataclass(frozen=True, eq=False)
class Concatenation(DumbHash, CopyLeftRightMixin, Node):
    left: Node
    right: Node


@dataclass(frozen=True, eq=False)
class Alternation(DumbHash, CopyLeftRightMixin, Node):
    left: Node
    right: Node


@dataclass(frozen=True, eq=False)
class Maybe(DumbHash, CopyStatementMixin, Node):
    statement: Node


@dataclass(frozen=True, eq=False)
class AnyNumber(DumbHash, CopyStatementMixin, Node):
    statement: Node


@dataclass(frozen=True, eq=False)
class Capture(DumbHash, Node):
    name: Text
    statement: Node

    def copy(self):
        return Capture(name=self.name, statement=self.statement.copy())


@dataclass(frozen=True)
class Initial(Node):
    pass


@dataclass(frozen=True)
class Terminal(Node):
    pass


__all__ = [
    "Node",
    "Final",
    "Concatenation",
    "Alternation",
    "Maybe",
    "AnyNumber",
    "Capture",
    "Initial",
    "Terminal",
    "Out",
    "Tok",
]
