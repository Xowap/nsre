from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Iterator, Mapping, Sequence, Text, Tuple, TypeVar

# Tokens type
Tok = TypeVar("Tok")

# Output type
Out = TypeVar("Out")


class Matcher(Generic[Tok, Out], metaclass=ABCMeta):
    @abstractmethod
    def match(self, token: Tok) -> Iterator[Out]:
        raise NotImplementedError


class Eq(Matcher):
    def __init__(self, ref: Tok):
        self.ref = ref

    def match(self, token: Tok) -> Iterator[Out]:
        if self.ref == token:
            yield token

    def __repr__(self):
        return f"Eq({self.ref!r})"


class In(Matcher):
    def __init__(self, ref: Sequence[Tok]):
        self.ref = ref

    def match(self, token: Tok) -> Iterator[Out]:
        if token in self.ref:
            yield token

    def __repr__(self):
        return f"In({self.ref!r})"


class OutOf(Matcher):
    def __init__(self, ref: Tok):
        self.ref = ref

    def __repr__(self):
        return f"OutOf({self.ref!r})"

    def match(self, token: Tok) -> Iterator[Out]:
        if self.ref in token:
            yield self.ref


class AttributeHasValue(Matcher):
    def __init__(self, attribute: Text, value: Any):
        self.attribute = attribute
        self.value = value

    def match(self, token: Tok) -> Iterator[Out]:
        if (
            hasattr(token, self.attribute)
            and getattr(token, self.attribute) == self.value
        ):
            yield token

    def __repr__(self):
        return f"AttributeHasValue({self.attribute}={self.value!r}"


class KeyHasValue(Matcher):
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value

    def match(self, token: Tok) -> Iterator[Out]:
        if (
            isinstance(token, Mapping)
            and self.key in token
            and token[self.key] == self.value
        ):
            yield token

    def __repr__(self):
        return f"KeyHasValue({self.key!r}={self.value!r})"


class Anything(Matcher):
    def __repr__(self):
        return f"Anything()"

    def match(self, token: Tok) -> Iterator[Out]:
        yield token


class ChrRanges(Matcher[str, str]):
    def __init__(self, *ranges: Tuple[str, str]):
        self.ranges = ranges

    def __repr__(self):
        return f"ChrRanges{self.ranges!r}"

    def match(self, token: Tok) -> Iterator[Out]:
        for start, stop in self.ranges:
            if ord(start) <= ord(token) <= ord(stop):
                yield token


__all__ = [
    "Tok",
    "Out",
    "Matcher",
    "Eq",
    "In",
    "OutOf",
    "AttributeHasValue",
    "KeyHasValue",
    "Anything",
    "ChrRanges",
]
