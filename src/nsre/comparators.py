from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Generic, Iterable, List, Set, Text, Tuple, Type, TypeVar, Union

T = TypeVar("T")


class Comparator(Generic[T], ABC):
    """
    Implementing this interface allows to make a comparator that will be used
    to test if a symbol is legit
    """

    @abstractmethod
    def __eq__(self, value: T) -> bool:
        raise NotImplementedError


class InSet(Comparator[T]):
    """
    Checks if the compared value is found within a set (faster than finding it
    in a list but it means that the base type T has to be hashable).
    """

    def __init__(self, values: Iterable[T]):
        self.values: Set[T] = set(values)

    def __eq__(self, value: T) -> bool:
        return value in self.values

    def __repr__(self):
        return f"InSet({repr(self.values)})"


class InList(Comparator[T]):
    """
    Checks if the compared value is found within a list. It means that the base
    type T has to be comparable with __eq__().
    """

    def __init__(self, values: Iterable[T]):
        self.values: List[T] = list(values)

    def __eq__(self, value: T) -> bool:
        return value in self.values

    def __repr__(self):
        return f"InList({repr(self.values)})"


class IsInstance(Comparator[T]):
    """
    Tests if the provided value is an instance of any of the classes passed to
    the constructor.
    """

    def __init__(self, *types: Type[T]):
        self.types = types

    def __eq__(self, value: T) -> bool:
        # Mishap in type specification syntax
        # noinspection PyTypeHints
        return isinstance(value, self.types)

    def __repr__(self):
        r = ", ".join(repr(x) for x in self.types)

        return f"IsInstance({r})"


class AttributeHasValue(Comparator[T]):
    """
    Tests the compared value to see if their `attribute` has the right `value`.
    """

    def __init__(self, attribute: Text, value: Any):
        self.attribute = attribute
        self.value = value

    def __eq__(self, value: T) -> bool:
        return (
            hasattr(value, self.attribute)
            and getattr(value, self.attribute) == self.value
        )

    def __repr__(self):
        return f"AttributeHasValue({self.attribute}={repr(self.value)})"


class KeyHasValue(Comparator[T]):
    """
    Tests the compared value (which has to be a Dict) to see if their `key` has
    the right `value`.
    """

    def __init__(self, key: Text, value: Any):
        self.key = key
        self.value = value

    def __eq__(self, value: T) -> bool:
        return (
            isinstance(value, Mapping)
            and self.key in value
            and value[self.key] == self.value
        )

    def __repr__(self):
        return f"KeyHasValue({repr(self.key)}={repr(self.value)})"


class Neg(Comparator[T]):
    """
    Negates the output of any comparator, including if you give a raw value.
    """

    def __init__(self, comparator: Union[T, Comparator[T]]):
        self.comparator = comparator

    def __eq__(self, value: T) -> bool:
        return self.comparator != value

    def __repr__(self):
        return f"Neg({self.comparator!r})"


class All(Comparator[T]):
    """
    Matches all and any inputs.
    """

    # The argument here is just for type safety
    # noinspection PyUnusedLocal,PyShadowingBuiltins
    def __init__(self, type: Type[T] = Type[Any]):
        pass

    def __eq__(self, other: T) -> bool:
        return True

    def __repr__(self):
        return "All()"


class ChrRanges(Comparator[str]):
    """
    Comparator for strings only, matches any number of character ranges.

    >>> ChrRanges(('a', 'z'), ('A', 'Z'))
    """

    def __init__(self, *ranges: Tuple[str, str]):
        self.ranges = ranges

    def __eq__(self, other: str) -> bool:
        for start, stop in self.ranges:
            if ord(start) <= ord(other) <= ord(stop):
                return True

        return False
