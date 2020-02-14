from nsre.ast import *

# noinspection PyProtectedMember
from nsre.ast import _Initial, _Terminal
from nsre.matchers import Eq
from nsre.regexp import ast_to_graph


def unscrew(x):
    if x == _Terminal():
        return "T"
    elif x == _Initial():
        return "I"
    else:
        assert isinstance(x, Final)
        assert isinstance(x.statement, Eq)
        return x.statement.ref


def graph_edges(g):
    return list(sorted((unscrew(a), unscrew(b)) for a, b in g.edges))


def test_final(fa):
    g = ast_to_graph(fa)
    assert [*g.successors(_Initial())] == [fa]
    assert [*g.successors(fa)] == [_Terminal()]


def test_concatenate(fa, fb):
    g = ast_to_graph(fa + fb)
    assert [*g.successors(_Initial())] == [fa]
    assert [*g.successors(fa)] == [fb]
    assert [*g.successors(fb)] == [_Terminal()]


def test_alternate(fa, fb):
    g = ast_to_graph(fa | fb)
    assert {*g.successors(_Initial())} == {fa, fb}
    assert {*g.successors(fa)} == {_Terminal()}
    assert {*g.successors(fb)} == {_Terminal()}


def test_maybe(fa):
    g = ast_to_graph(Maybe(fa))
    assert {*g.successors(_Initial())} == {fa, _Terminal()}
    assert {*g.successors(fa)} == {_Terminal()}


def test_any_number(fa):
    g = ast_to_graph(AnyNumber(fa))
    assert {*g.successors(_Initial())} == {fa, _Terminal()}
    assert {*g.successors(fa)} == {fa, _Terminal()}


def test_capture(fa):
    g = ast_to_graph(Capture(statement=fa, name="foo"))
    assert g.get_edge_data(_Initial(), fa) == {"start_captures": ["foo"]}
    assert g.get_edge_data(fa, _Terminal()) == {"stop_captures": ["foo"]}


# noinspection DuplicatedCode
def test_exp_1(fa, fb, fc):
    g = ast_to_graph(((fa + fb) | fc) * slice(0, None))

    assert {*g.successors(_Initial())} == {fa, fc, _Terminal()}
    assert {*g.successors(fa)} == {fb}
    assert {*g.successors(fb)} == {fa, fc, _Terminal()}
    assert {*g.successors(fc)} == {fa, fc, _Terminal()}


def test_exp_2(fa, fb):
    g = ast_to_graph(AnyNumber(AnyNumber(fa) | AnyNumber(fb)))

    assert {*g.successors(_Initial())} == {fa, fb, _Terminal()}
    assert {*g.successors(fa)} == {fa, fb, _Terminal()}
    assert {*g.successors(fb)} == {fa, fb, _Terminal()}


# noinspection DuplicatedCode
def test_concat_any_number():
    a1 = Final(Eq("a1"))
    a2 = Final(Eq("a2"))
    b1 = Final(Eq("b1"))
    b2 = Final(Eq("b2"))
    c = Final(Eq("c"))

    p1: Node = a1 + AnyNumber(b1)
    p2: Node = a2 + AnyNumber(b2)

    exp = p1 + c + p2

    g = ast_to_graph(exp.copy())
    edges = list(
        sorted(
            [
                ("I", "a1"),
                ("a1", "c"),
                ("a1", "b1"),
                ("b1", "b1"),
                ("b1", "c"),
                ("c", "a2"),
                ("a2", "T"),
                ("a2", "b2"),
                ("b2", "b2"),
                ("b2", "T"),
            ]
        )
    )
    assert graph_edges(g) == edges


# noinspection DuplicatedCode
def test_concat_any_number_same(fa, fb, fc):
    p: Node = fa + AnyNumber(fb)

    exp1 = p.copy()
    g = ast_to_graph(exp1)
    edges = list(sorted([("I", "a"), ("a", "b"), ("a", "T"), ("b", "b"), ("b", "T")]))
    assert graph_edges(g) == edges

    exp2 = (p + fc).copy()
    g = ast_to_graph(exp2)
    edges = list(
        sorted([("I", "a"), ("a", "b"), ("a", "c"), ("b", "b"), ("b", "c"), ("c", "T")])
    )
    assert graph_edges(g) == edges

    exp3 = (exp2 + p).copy()
    g = ast_to_graph(exp3.copy())
    edges = list(
        sorted(
            [
                ("I", "a"),
                ("a", "c"),
                ("a", "b"),
                ("b", "b"),
                ("b", "c"),
                ("c", "a"),
                ("a", "T"),
                ("a", "b"),
                ("b", "b"),
                ("b", "T"),
            ]
        )
    )
    assert graph_edges(g) == edges
