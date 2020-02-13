from pytest import fixture, raises

from nsre.ast import *
from nsre.matchers import Eq


def test_final_eq(a, b):
    assert a != b
    assert a != Final(Eq("a"))
    assert a == a


def test_final_hash(fa, fb):
    h = {fa: "a", fb: "b"}
    assert h[fa] == "a"
    assert h[fb] == "b"


def test_concatenation(fa, fb):
    c = fa + fb
    assert isinstance(c, Concatenation)
    assert c.left == fa
    assert c.right == fb


def test_alternation(fa, fb):
    c = fa | fb
    assert isinstance(c, Alternation)
    assert c.left == fa
    assert c.right == fb


def test_maybe(fa, a):
    c: Maybe = fa * slice(0, 1)
    assert isinstance(c, Maybe)
    assert c.statement != fa
    assert isinstance(c.statement, Final)
    assert c.statement.statement is a


def test_any_number(fa, a):
    c: AnyNumber = fa * slice(0, None)
    assert isinstance(c, AnyNumber)
    assert c.statement != fa
    assert isinstance(c.statement, Final)
    assert c.statement.statement is a


def test_at_least_one(fa, a):
    c: Concatenation = fa * slice(1, None)
    assert isinstance(c, Concatenation)
    assert isinstance(c.left, Final)
    assert c.left.statement is a
    assert isinstance(c.right, AnyNumber)
    assert isinstance(c.right.statement, Final)
    assert c.right.statement.statement is a


def test_from_one_to_two(fa, a):
    c: Concatenation = fa * slice(1, 2)
    assert isinstance(c, Concatenation)
    assert isinstance(c.left, Final)
    assert c.left.statement is a
    assert isinstance(c.right, Maybe)
    assert isinstance(c.right.statement, Final)
    assert c.right.statement.statement is a


def test_from_one_to_three(fa, a):
    c: Concatenation = fa * slice(1, 3)
    assert isinstance(c, Concatenation)
    assert isinstance(c.left, Concatenation)
    assert isinstance(c.left.left, Final)
    assert c.left.left.statement is a
    assert isinstance(c.left.right, Maybe)
    assert isinstance(c.left.right.statement, Final)
    assert c.left.right.statement.statement is a
    assert isinstance(c.right, Maybe)
    assert isinstance(c.right.statement, Final)
    assert c.right.statement.statement is a


def test_capture(fa):
    c: Capture = fa["foo"]
    assert isinstance(c, Capture)
    assert c.statement == fa
    assert c.name == "foo"


def test_initial_terminal():
    i1 = Initial()
    i2 = Initial()
    t1 = Terminal()
    t2 = Terminal()

    assert i1 == i1
    assert i1 == i2
    assert t1 == t1
    assert t1 == t2
    assert i1 != t1
    assert t1 != i1


def test_getitem_no_string(fa):
    with raises(KeyError):
        assert fa[42]


def test_mul_neg(fa):
    with raises(ValueError):
        assert fa * 0


def test_mul_invalid_start(fa):
    with raises(ValueError):
        assert fa * slice("foo", None)


def test_mul_invalid_stop(fa):
    with raises(ValueError):
        assert fa * slice(None, "foo")


def test_mul_invalid(fa):
    with raises(ValueError):
        assert fa * "foo"


def test_dumb_hash(fa, fb):
    a = Concatenation(fa, fb)
    b = Concatenation(fa, fb)

    assert a == a
    assert a != b
    assert b == b

    assert hash(a) != hash(b)
