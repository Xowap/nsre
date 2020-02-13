from pytest import fixture

from nsre.ast import *
from nsre.matchers import Eq


@fixture(name="a")
def make_a():
    return Eq("a")


@fixture(name="b")
def make_b():
    return Eq("b")


@fixture(name="c")
def make_c():
    return Eq("c")


@fixture(name="fa")
def make_fa(a):
    return Final(a)


@fixture(name="fb")
def make_fb(b):
    return Final(b)


@fixture(name="fc")
def make_fc(c):
    return Final(c)
