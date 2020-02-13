from typing import Text

from nsre.ast import *
from nsre.matchers import ChrRanges, Eq, In, OutOf
from nsre.regexp import RegExp
from nsre.shortcuts import anything, seq


def test_match_basic_1(fa, fb):
    r: RegExp[Text, Text] = RegExp.from_ast(fa + Maybe(fa) + AnyNumber(fb))
    assert r.match("a")
    assert r.match("aa")
    assert r.match("aab")
    assert r.match("aabbbbb")
    assert r.match("aabbbbbbbbbb")
    assert not r.match("b")
    assert not r.match("ba")
    assert not r.match("aaa")
    assert not r.match("foo")

    m = r.match("a")
    assert len(m) == 1
    assert len(m[0].trail) == 1
    assert m[0].trail[0] == "a"


def test_match_basic_2(fa, fb, fc):
    r: RegExp[Text, Text] = RegExp.from_ast(((fa + fb) | fc) * slice(0, None))
    assert r.match("")
    assert r.match("ab")
    assert r.match("c")
    assert r.match("abc")
    assert r.match("abccccc")
    assert r.match("abababc")
    assert r.match("cabcab")
    assert not r.match("cba")
    assert not r.match("cbaaaa")
    assert not r.match("abaaaa")


# noinspection DuplicatedCode
def test_match_group_1(fa):
    r = RegExp.from_ast(fa["foo"])
    m = r.match("a")
    assert len(m) == 1
    assert m[0].trail == ("a",)
    assert len(m[0].children["foo"]) == 1
    assert m[0].children["foo"][0].trail == ("a",)


# noinspection DuplicatedCode
def test_match_group_2(fa):
    r = RegExp.from_ast(fa["bar"]["foo"])
    m = r.match("a")
    assert len(m) == 1
    assert m[0].trail == ("a",)
    assert len(m[0].children["foo"]) == 1
    assert m[0].children["foo"][0].trail == ("a",)
    assert len(m[0].children["foo"][0].children["bar"]) == 1
    assert m[0].children["foo"][0].children["bar"][0].trail == ("a",)


# noinspection DuplicatedCode
def test_match_group_3(fa):
    r = RegExp.from_ast(Maybe(fa)["foo"])

    m = r.match("a")
    assert len(m) == 1
    assert m[0].trail == ("a",)
    assert len(m[0].children["foo"]) == 1
    assert m[0].children["foo"][0].trail == ("a",)

    m = r.match("")
    assert len(m) == 1
    assert m[0].trail == tuple()


# noinspection DuplicatedCode
def test_match_group_4(fa):
    r = RegExp.from_ast(Maybe(fa["foo"]))

    m = r.match("a")
    assert len(m) == 1
    assert m[0].trail == ("a",)
    assert len(m[0].children["foo"]) == 1
    assert m[0].children["foo"][0].trail == ("a",)

    m = r.match("")
    assert len(m) == 1
    assert m[0].trail == tuple()


def test_match_group_5():
    fm = OutOf("f")
    om = OutOf("o")
    bm = OutOf("b")
    am = OutOf("a")
    rm = OutOf("r")

    f = Final(fm)
    o = Final(om)
    b = Final(bm)
    a = Final(am)
    z = Final(rm)

    data = list(zip("foo", "bar"))

    r = RegExp.from_ast((f + o + o)["foo"])
    m = r.match(data, join_trails=True)
    assert m["foo"].trail == "foo"

    r = RegExp.from_ast(((f + o + o) | (b + a + z))["foo"])
    m = r.match(data, join_trails=True)
    assert {mm["foo"].trail for mm in m} == {"foo", "bar"}


def test_match_group_6():
    r = RegExp.from_ast(
        anything()
        + seq("like")
        + anything()
        + (seq("sausages") | seq("bananas"))["what"]
        + anything()
    )
    m = r.match(
        "I really like to eat a lot of sausages! Who doesn't?", join_trails=True
    )
    assert m["what"].trail == "sausages"


def test_match_group_7():
    w = seq("a")
    ww = seq("b")
    c = seq("+")
    p = w + AnyNumber(ww)

    re = RegExp.from_ast(p + c + p)
    assert not re.match("a")
    assert not re.match("abb")
    assert not re.match("abb+")
    assert re.match("abb+abb")
    assert re.match("abb+abb+ab")


def test_match_email():
    w = Final(ChrRanges(("a", "z"), ("A", "Z")))
    ww = Final(ChrRanges(("a", "z"), ("A", "Z"), ("0", "9")))
    user_connector = Final(In({"+", "-", "."}))
    domain_connector = Final(In({".", "-"}))

    part = w + AnyNumber(ww)
    user_name = part + AnyNumber(user_connector + part)
    domain_name = part + domain_connector + part
    at = seq("@")

    re = RegExp.from_ast(w)
    assert re.match("X")
    assert not re.match("9")

    re = RegExp.from_ast(ww)
    assert re.match("X")
    assert re.match("9")
    assert not re.match("+")

    re = RegExp.from_ast(user_connector)
    assert re.match("+")
    assert not re.match("X")

    re = RegExp.from_ast(domain_connector)
    assert re.match(".")
    assert not re.match("X")

    re = RegExp.from_ast(part)
    assert re.match("f")
    assert re.match("foo")
    assert re.match("foo42")
    assert re.match("foo42bar")
    assert not re.match("42")
    assert not re.match("42foo")

    re = RegExp.from_ast(user_name)
    assert re.match("remy")
    assert re.match("remy.sanchez")
    assert re.match("remy.sanchez+foo")
    assert not re.match("remy..sanchez")
    assert not re.match("remy.+sanchez")

    re = RegExp.from_ast(domain_name)
    assert not re.match("foo")
    assert re.match("foo.bar")
    assert re.match("foo.bar-boo.baz")
    assert not re.match("foo.42bar")
    assert re.match("foo.bar42")

    re = RegExp.from_ast(at)
    assert re.match("@")
    assert not re.match("X")

    re = RegExp.from_ast(user_name["user"] + at + domain_name["domain"])

    m = re.match("remy.sanchez@with-madrid.com", join_trails=True)
    assert m["user"].trail == "remy.sanchez"
    assert m["domain"].trail == "with-madrid.com"

    m = re.match("foo@bar")
    assert not m
