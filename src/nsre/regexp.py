from dataclasses import dataclass
from itertools import product
from typing import Dict, Generic, Iterator, List, Sequence, Text

import networkx as nx

from .ast import (
    Alternation,
    AnyNumber,
    Capture,
    Concatenation,
    Final,
    Initial,
    Maybe,
    Node,
    Out,
    Terminal,
    Tok,
)


def ast_to_graph(root: Node) -> nx.DiGraph:
    g = nx.DiGraph()
    initial = Initial()
    terminal = Terminal()

    g.add_nodes_from([initial, root, terminal])
    g.add_edge(initial, root)
    g.add_edge(root, terminal)

    explore = {root}

    while explore:
        for node in [*explore]:
            explore.remove(node)

            if isinstance(node, Final):
                pass
            elif isinstance(node, Concatenation):
                _explore_concatenation(explore, g, node)
            elif isinstance(node, Alternation):
                _explore_alternation(explore, g, node)
            elif isinstance(node, Maybe):
                _explore_maybe(explore, g, node)
            elif isinstance(node, AnyNumber):
                _explore_any_number(explore, g, node)
            elif isinstance(node, Capture):
                _explore_capture(explore, g, node)

    return g


def _explore_capture(explore, g, node):
    explore.add(node.statement)
    g.add_node(node.statement)

    for p in g.predecessors(node):
        data = g.get_edge_data(p, node, default={"start_captures": []})
        data["start_captures"] = [*data.get("start_captures", []), node.name]
        g.add_edge(p, node.statement, **data)

    for s in g.successors(node):
        data = g.get_edge_data(node, s, default={"stop_captures": []})
        data["stop_captures"] = [*data.get("stop_captures", []), node.name]
        g.add_edge(node.statement, s, **data)

    g.remove_node(node)


# noinspection DuplicatedCode
def _explore_any_number(explore, g, node):
    explore.add(node.statement)
    g.add_node(node.statement)

    g.add_edge(node.statement, node.statement)

    _cross_connect(g, node)

    for p in g.predecessors(node):
        data = g.get_edge_data(p, node, default={})
        g.add_edge(p, node.statement, **data)

    for s in g.successors(node):
        data = g.get_edge_data(node, s, default={})
        g.add_edge(node.statement, s, **data)

    g.remove_node(node)


# noinspection DuplicatedCode
def _explore_maybe(explore, g, node):
    explore.add(node.statement)
    g.add_node(node.statement)

    _cross_connect(g, node)

    for p in g.predecessors(node):
        data = g.get_edge_data(p, node, default={})
        g.add_edge(p, node.statement, **data)

    for s in g.successors(node):
        data = g.get_edge_data(node, s, default={})
        g.add_edge(node.statement, s, **data)

    g.remove_node(node)


def _cross_connect(g, node):
    for p, s in product(g.predecessors(node), g.successors(node)):
        data1 = g.get_edge_data(p, node, default={})
        data2 = g.get_edge_data(node, s, default={})
        merged = dict(**data1, **data2)

        if "start_captures" in data1 and "start_captures" in data2:
            merged["start_captures"] = data1["start_captures"] + data2["start_captures"]

        if "stop_captures" in data1 and "stop_captures" in data2:
            merged["stop_captures"] = data1["stop_captures"] + data2["stop_captures"]

        g.add_edge(p, s, **merged)


def _explore_alternation(explore, g, node):
    explore.add(node.left)
    explore.add(node.right)

    g.add_node(node.left)
    g.add_node(node.right)

    for p in g.predecessors(node):
        data = g.get_edge_data(p, node, default={})
        g.add_edge(p, node.left, **data)
        g.add_edge(p, node.right, **data)

    for s in g.successors(node):
        data = g.get_edge_data(node, s, default={})
        g.add_edge(node.left, s, **data)
        g.add_edge(node.right, s, **data)

    g.remove_node(node)


# noinspection DuplicatedCode
def _explore_concatenation(explore, g, node):
    explore.add(node.left)
    explore.add(node.right)

    g.add_node(node.left)
    g.add_node(node.right)

    for p in g.predecessors(node):
        data = g.get_edge_data(p, node, default={})
        g.add_edge(p, node.left, **data)

    g.add_edge(node.left, node.right)

    for s in g.successors(node):
        data = g.get_edge_data(node, s, default={})
        g.add_edge(node.right, s, **data)

    g.remove_node(node)


@dataclass
class TrailItem(Generic[Out]):
    item: Out
    data: Dict[Text, Sequence[Text]]


@dataclass(frozen=True)
class Explorer(Generic[Tok, Out]):
    re: "RegExp[Tok, Out]"
    node: Node[Tok, Out]
    trail: List[TrailItem[Out]]

    def advance(self, token: Tok) -> Iterator["Explorer[Tok, Out]"]:
        for s in self.re.graph.successors(self.node):
            if not isinstance(s, Final):
                continue

            for m in s.statement.match(token):
                data = self.re.graph.get_edge_data(self.node, s, default={})

                yield Explorer(
                    re=self.re,
                    node=s,
                    trail=[*self.trail, TrailItem(item=m, data=data)],
                )

    def can_terminate(self):
        return self.re.graph.has_successor(self.node, Terminal())


class _Match(Generic[Out]):
    def __init__(self, start_pos: int):
        self.start_pos = start_pos
        self.children: Dict[Text, List[_Match]] = {}
        self.trail: List[Out] = []
        self._stack: List[Text] = []

    def _deep_get(self, keys: Sequence[Text]) -> "_Match":
        ptr = self

        for key in keys:
            ptr = ptr.children[key][-1]

        return ptr

    def start(self, name: Text, pos: int) -> None:
        stick = self._deep_get(self._stack)

        if name not in stick.children:
            stick.children[name] = [_Match(pos)]
        else:
            stick.children[name].append(_Match(pos))

        self._stack.append(name)

    def stop(self, name: Text) -> None:
        if name != self._stack[-1]:
            raise ValueError("Trying to stop a match which is not started")

        self._stack = self._stack[0:-1]

    def append(self, item: Out) -> None:
        self.trail.append(item)
        ptr = self

        for key in self._stack:
            ptr = ptr.children[key][-1]
            ptr.trail.append(item)

    def as_match(self, join_trails: bool = False) -> "Match":
        return Match(
            start_pos=self.start_pos,
            trail="".join(self.trail) if join_trails else tuple(self.trail),
            children={
                k: MatchList(i.as_match(join_trails) for i in v)
                for k, v in self.children.items()
            },
        )


@dataclass(frozen=True)
class Match(Generic[Out]):
    start_pos: int
    children: Dict[Text, List["Match"]]
    trail: Sequence[Out]

    def __getitem__(self, item):
        return self.children[item][0]


class MatchList(tuple, Generic[Out]):
    def __getitem__(self, item) -> Match[Out]:
        if isinstance(item, str):
            return self[0][item]
        else:
            return super().__getitem__(item)


class RegExp(Generic[Tok, Out]):
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    @classmethod
    def from_ast(cls, root: Node[Tok, Out]) -> "RegExp[Tok, Out]":
        return cls(graph=ast_to_graph(root.copy()))

    def _make_match(self, explorer: Explorer[Tok, Out]) -> _Match[Out]:
        match = _Match(0)

        for i, token in enumerate(explorer.trail):
            for stop in token.data.get("stop_captures", []):
                match.stop(stop)

            for start in token.data.get("start_captures", []):
                match.start(start, i)

            match.append(token.item)

        return match

    def match(
        self, seq: Sequence[Tok], join_trails: bool = False
    ) -> MatchList[Match[Out]]:
        stack: List[Explorer[Tok, Out]] = [Explorer(self, Initial(), [])]

        for token in seq:
            stack = [ne for oe in stack for ne in oe.advance(token)]

            if not stack:
                break

        return MatchList(
            self._make_match(s).as_match(join_trails=join_trails)
            for s in stack
            if s.can_terminate()
        )


__all__ = ["RegExp", "ast_to_graph"]
