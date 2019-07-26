from enum import Enum
from itertools import chain, product
from math import inf, isinf
from typing import Generic, Sequence, Tuple, Union

from .comparators import Comparator, T
from .utils import n_uple

Comparable = Union[T, Comparator[T]]
Matchable = Union[Comparable, "Fsm[T]"]


class StateType(Enum):
    """
    Describes the types of states you can find in the FSM

    MATCH = this state must match something
    INITIAL = this state is an initial state
    TERMINAL = this state is terminal
    NODE = this state is just a connecting node between other states
    """

    MATCH = 0
    INITIAL = 1
    TERMINAL = 2
    NODE = 3

    def state(self) -> "State":
        return State(self)


class State:
    """
    Represents a state of the FSM. Connexions between states are oriented.
    You can find `outbound` and `inbound` links in the eponymous attributes.
    There is also a `type`.
    """

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
        """
        Compares two states, INITIAL and TERMINAL are always equal while
        otherwise it's the equivalent of using `is`.
        """

        if not isinstance(other, State):
            return False

        if self.type in [StateType.INITIAL, StateType.TERMINAL]:
            return self.type == other.type

        return self is other

    @property
    def can_terminate(self):
        """
        If the parsing of the string ends on this state then it can be
        considered as a match.
        """

        for state in self.outbound:
            if state.type == StateType.TERMINAL:
                return True
            elif state.type == StateType.NODE and state.can_terminate:
                return True

        return False

    def unlink_to(self, other: "State"):
        """
        Removes a link towards the other state.
        """

        self.outbound = tuple(o for o in self.outbound if o != other)
        other.inbound = tuple(o for o in other.inbound if o != self)

    def link_to(self, other: "State"):
        """
        Creates a link towards the other state.
        """

        if other not in self.outbound:
            self.outbound = tuple(chain(self.outbound, (other,)))

        if self not in other.inbound:
            other.inbound = tuple(chain(other.inbound, (self,)))


class MatchState(State, Generic[T]):
    """
    Special state that implements an `accept()` method. The machine cannot
    transition to a MatchState that does not accept the incoming symbol.

    See the comparators module to see valid comparators.
    """

    def __init__(self, comparator: Comparator[T]):
        super().__init__(StateType.MATCH)
        self.comparator: Comparator[T] = comparator

    def __repr__(self):
        return f"State({self.type.name}, {self.comparator!r})"

    def accept(self, value: T) -> bool:
        """
        Compares the value with the reference to know if we accept the
        transition.
        """

        return self.comparator == value


class Fsm(Generic[T]):
    """
    Core FSM object. It is made so you can connect it to other FSM.

    The `initial` and `terminal` states are a way to know the entry/exit points
    of the FSM and connecting two FSM together involves replacing all the
    `initial`/`terminal` nodes with something on the other FSM.
    """

    def __init__(self):
        self.initial: State = StateType.INITIAL.state()
        self.terminal: State = StateType.TERMINAL.state()

        self.initial.link_to(self.terminal)

    def match(self, seq: Sequence[T]) -> bool:
        """
        That's the core of the algorithm. For each symbol in the sequence,
        advance to all the possible states which accept the symbol.
        """

        stack = [self.initial]

        def add_state(s: State):
            """
            Adds a state to the stack. If the state is a node, follow through
            until a match state is found.
            """

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
        """
        Drops the terminal state of this FSM and the initial state of the other
        one and reconnect the finish layer of this FSM to the begin layer of
        the other FSM. Also replace the terminal state of the other FSM by
        this terminal state for technical reasons.
        """

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
        """
        Merges initial and terminal states of this FSM and the other in order
        to parallelize them.
        """

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
    """
    Matches one symbol exactly
    """

    def __init__(self, symbol: Comparable):
        super().__init__()

        state = MatchState(symbol)

        self.initial.unlink_to(self.terminal)
        self.initial.link_to(state)
        state.link_to(self.terminal)


class Chain(Fsm[T]):
    """
    Matches a chain of symbols exactly
    """

    def __init__(self, seq: Sequence[Comparable]):
        super().__init__()

        self.initial.unlink_to(self.terminal)

        for left, right in n_uple(
            chain((self.initial,), (MatchState(x) for x in seq), (self.terminal,)), n=2
        ):
            left.link_to(right)


class Maybe(Fsm[T]):
    """
    Matches maybe a symbol/sub-FSM, maybe jumps over it.
    """

    def __init__(self, symbol: Matchable):
        super().__init__()

        if isinstance(symbol, Fsm):
            fsm = symbol
        else:
            fsm = Symbol(symbol)

        node = StateType.NODE.state()

        self.initial.unlink_to(self.terminal)

        begin = fsm.initial.outbound
        finish = fsm.terminal.inbound

        for state in begin:
            fsm.initial.unlink_to(state)
            self.initial.link_to(state)

        for state in finish:
            state.unlink_to(fsm.terminal)
            state.link_to(node)

        node.link_to(self.terminal)
        self.initial.link_to(node)


class AnyNumber(Fsm[T]):
    """
    Matches 0 to infinity number of repetitions of the same symbol/sub-FSM.
    """

    def __init__(self, symbol: Matchable):
        super().__init__()

        if isinstance(symbol, Fsm):
            fsm = symbol
        else:
            fsm = Symbol(symbol)

        node = StateType.NODE.state()

        self.initial.unlink_to(self.terminal)
        self.initial.link_to(node)
        node.link_to(self.terminal)

        begin = fsm.initial.outbound
        finish = fsm.terminal.inbound

        for state in begin:
            fsm.initial.unlink_to(state)
            node.link_to(state)

        for state in finish:
            state.unlink_to(fsm.terminal)
            state.link_to(node)


class Range(Fsm[T]):
    """
    Matches from min to max repetitions of the same symbol/sub-FSM.
    """

    # Shadowing `min` and `max` for API niceness
    # noinspection PyShadowingBuiltins
    def __init__(self, symbol: Comparable, min=0, max=inf):
        super().__init__()

        for _ in range(0, min):
            if isinstance(symbol, Fsm):
                self.__add__(symbol)
            else:
                self.__add__(Symbol(symbol))

        if not isinf(max):
            for _ in range(0, int(max) - min):
                self.__add__(Maybe(symbol))
        else:
            self.__add__(AnyNumber(symbol))
