from typing import Iterator, Tuple, TypeVar

T = TypeVar("T")


def n_uple(it: Iterator[T], n: int) -> Tuple[T, ...]:
    """
    Generates n-uples from the iterator.
    """

    stack = []

    for i in it:
        stack.append(i)

        if len(stack) > n:
            stack.pop(0)

        if len(stack) == n:
            yield tuple(stack)
