from abc import ABC, abstractmethod
from enum import Enum
from itertools import chain, product
from math import inf, isinf
from typing import Generic, Sequence, Tuple, TypeVar

from .utils import n_uple

T = TypeVar("T")


class Comparator(Generic[T], ABC):
    @abstractmethod
    def __eq__(self, other: T) -> bool:
        raise NotImplementedError


class StateType(Enum):
    MATCH = 0
    INITIAL = 1
    TERMINAL = 2
    NODE = 3

    def state(self) -> "State":
        return State(self)


class State:
    # The name is shadowed only for the constructor which then stores it as a
    # property of the object which makes more sense than `type_`.
    # noinspection PyShadowingBuiltins
    def __init__(self, type: StateType):
        self.type: StateType = type
        self.inbound: Tuple[State, ...] = tuple()
        self.outbound: Tuple[State, ...] = tuple()

    def __repr__(self):
        return f"State({self.type.name})"

    def __eq__(self, other):
        if not isinstance(other, State):
            return False

        if self.type in [StateType.INITIAL, StateType.TERMINAL]:
            return self.type == other.type

        return self is other

    @property
    def can_terminate(self):
        for state in self.outbound:
            if state.type == StateType.TERMINAL:
                return True
            elif state.type == StateType.NODE and state.can_terminate:
                return True

        return False

    def unlink_to(self, other: "State"):
        self.outbound = tuple(o for o in self.outbound if o != other)
        other.inbound = tuple(o for o in other.inbound if o != self)

    def link_to(self, other: "State"):
        if other not in self.outbound:
            self.outbound = tuple(chain(self.outbound, (other,)))

        if self not in other.inbound:
            other.inbound = tuple(chain(other.inbound, (self,)))


class MatchState(State, Generic[T]):
    def __init__(self, comparator: Comparator[T]):
        super().__init__(StateType.MATCH)
        self.comparator: Comparator[T] = comparator

    def __repr__(self):
        return f"State({self.type.name}, {self.comparator!r})"

    def accept(self, value: T) -> bool:
        return self.comparator == value


class Fsm(Generic[T]):
    def __init__(self):
        self.initial: State = StateType.INITIAL.state()
        self.terminal: State = StateType.TERMINAL.state()

        self.initial.link_to(self.terminal)

    def match(self, seq: Sequence[T]) -> bool:
        stack = [self.initial]

        def add_state(s: State):
            if id(s) in id_set:
                return

            if isinstance(s, MatchState) and s.accept(symbol):
                id_set.add(id(s))
                new_stack.append(s)
            elif s.type == StateType.NODE:
                for x in s.outbound:
                    add_state(x)

        for symbol in seq:
            id_set = set()
            new_stack = []

            for state in stack:
                for out in state.outbound:
                    add_state(out)

            stack = new_stack

        return any(s.can_terminate for s in stack)

    def __add__(self, other: "Fsm[T]") -> "Fsm[T]":
        left = self.terminal.inbound
        right = other.initial.outbound
        finish = other.terminal.inbound

        for state in left:
            state.unlink_to(self.terminal)

        for state in right:
            other.initial.unlink_to(state)

        for state in finish:
            state.unlink_to(other.terminal)
            state.link_to(self.terminal)

        for left_state, right_state in product(left, right):
            left_state.link_to(right_state)

        return self

    def __or__(self, other: "Fsm[T]") -> "Fsm[T]":
        begin = other.initial.outbound
        finish = other.terminal.inbound

        for state in begin:
            other.initial.unlink_to(state)
            self.initial.link_to(state)

        for state in finish:
            state.unlink_to(other.terminal)
            state.link_to(self.terminal)

        return self


class Symbol(Fsm[T]):
    def __init__(self, symbol: T):
        super().__init__()

        state = MatchState(symbol)

        self.initial.unlink_to(self.terminal)
        self.initial.link_to(state)
        state.link_to(self.terminal)


class Chain(Fsm[T]):
    def __init__(self, seq: Sequence[T]):
        super().__init__()

        self.initial.unlink_to(self.terminal)

        for left, right in n_uple(
            chain((self.initial,), (MatchState(x) for x in seq), (self.terminal,)), n=2
        ):
            left.link_to(right)


class Maybe(Fsm[T]):
    def __init__(self, symbol: T):
        super().__init__()

        state = MatchState(symbol)
        node = StateType.NODE.state()

        self.initial.unlink_to(self.terminal)

        self.initial.link_to(state)
        state.link_to(node)
        node.link_to(self.terminal)

        self.initial.link_to(node)


class AnyNumber(Fsm[T]):
    def __init__(self, symbol: T):
        super().__init__()

        state = MatchState(symbol)
        node = StateType.NODE.state()

        self.initial.unlink_to(self.terminal)

        self.initial.link_to(node)
        node.link_to(state)
        state.link_to(node)

        node.link_to(self.terminal)


class Range(Fsm[T]):
    # Shadowing `min` and `max` for API niceness
    # noinspection PyShadowingBuiltins
    def __init__(self, symbol: T, min=0, max=inf):
        super().__init__()

        for _ in range(0, min):
            self.__add__(Symbol(symbol))

        if not isinf(max):
            for _ in range(0, int(max) - min):
                self.__add__(Maybe(symbol))
        else:
            self.__add__(AnyNumber(symbol))
