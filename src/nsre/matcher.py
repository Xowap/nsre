from abc import ABC, abstractmethod
from collections import Mapping
from collections import Sequence as SequenceCollection
from typing import Any, Iterable, List, Sequence, Set, Text, Type, TypeVar, Union

T = TypeVar("T")

C = Union[Type[T], Sequence[Type[T]]]


class BaseMatcher(ABC):
    @abstractmethod
    def match(self, value: T) -> bool:
        raise NotImplementedError


class SetMatcher(BaseMatcher):
    def __init__(self, values: Iterable[T]):
        self.values: Set[T] = set(values)

    def match(self, value: T) -> bool:
        return value in self.values

    def __repr__(self):
        return f"SetMatcher({repr(self.values)})"


class ListMatcher(BaseMatcher):
    def __init__(self, values: Iterable[T]):
        self.values: List[T] = list(values)

    def match(self, value: T) -> bool:
        return value in self.values

    def __repr__(self):
        return f"ListMatcher({repr(self.values)})"


class EqualMatcher(BaseMatcher):
    def __init__(self, value: T):
        self.value: T = value

    def match(self, value: T) -> bool:
        return self.value == value

    def __repr__(self):
        return f"EqualMatcher({repr(self.value)})"


class InstanceMatcher(BaseMatcher):
    def __init__(self, value: C):
        self.value: C = value

    def match(self, value: T) -> bool:
        return isinstance(value, self.value)

    def __repr__(self):
        if isinstance(self.value, SequenceCollection):
            values = [self.value]
        else:
            values = self.value

        r = ", ".join(repr(x) for x in values)

        return f"InstanceMatcher({r})"


class AttributeMatcher(BaseMatcher):
    def __init__(self, attribute: Text, value: Any):
        self.attribute = attribute
        self.value = value

    def match(self, value: T) -> bool:
        return (
            hasattr(value, self.attribute)
            and getattr(value, self.attribute) == self.value
        )

    def __repr__(self):
        return f"AttributeMatcher({self.attribute}={repr(self.value)})"


class KeyMatcher(BaseMatcher):
    def __init__(self, key: Text, value: Any):
        self.key = key
        self.value = value

    def match(self, value: T) -> bool:
        return (
            isinstance(value, Mapping)
            and self.key in value
            and value[self.key] == self.value
        )

    def __repr__(self):
        return f"KeyMatcher({repr(self.key)}={repr(self.value)})"
