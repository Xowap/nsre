from nsre.fsm import AnyNumber, Chain, Maybe, Range, Symbol


def test_single_symbol():
    re = Symbol("a")

    assert re.match("a")
    assert not re.match("b")
    assert not re.match("aa")


def test_multiple_symbols():
    re = Symbol("a") + Symbol("b") + Symbol("c")

    assert not re.match("a")
    assert not re.match("ab")
    assert re.match("abc")
    assert not re.match("abcd")
    assert not re.match("aaa")


def test_chain():
    re = Chain("abc")

    assert not re.match("a")
    assert not re.match("ab")
    assert re.match("abc")
    assert not re.match("abcd")
    assert not re.match("aaa")


def test_branch():
    re = (
        Symbol("a")
        + (Symbol("b") | Symbol("c"))
        + (Symbol("d") | Symbol("e"))
        + Symbol("f")
    )

    assert not re.match("a")
    assert not re.match("ab")
    assert not re.match("abd")
    assert re.match("abdf")
    assert re.match("acdf")
    assert re.match("abef")
    assert re.match("acef")
    assert not re.match("aaaf")
    assert not re.match("abccf")


def test_maybe_simple():
    re = Maybe("a")

    assert re.match("")
    assert re.match("a")
    assert not re.match("aa")


def test_maybe_double():
    re = Maybe("a") + Maybe("b")

    assert re.match("")
    assert re.match("a")
    assert re.match("ab")
    assert re.match("b")
    assert not re.match("aa")
    assert not re.match("abc")


def test_maybe():
    re = Maybe("a") + Maybe("a") + Maybe("a") + Chain("aaa")

    assert not re.match("a")
    assert not re.match("aa")
    assert re.match("aaa")
    assert re.match("aaaa")
    assert re.match("aaaaa")
    assert re.match("aaaaaa")
    assert not re.match("aaaaaaa")


def test_maybe_fsm():
    re = Chain("say") + Maybe(Chain(" hello"))

    assert not re.match("")
    assert re.match("say")
    assert re.match("say hello")
    assert not re.match("say hell")
    assert not re.match(" hello")


def test_any_number_simple():
    re = AnyNumber("a")

    assert re.match("")
    assert re.match("a")
    assert re.match("aaaa")
    assert re.match("aaaaaaaaaaaa")
    assert not re.match("b")
    assert not re.match("bbbbbbb")


def test_any_number():
    re = AnyNumber("a") + Chain("bc")

    assert re.match("bc")
    assert re.match("abc")
    assert re.match("aaaaaabc")
    assert not re.match("")
    assert not re.match("aaaaaa")
    assert not re.match("ab")


def test_any_number_fsm():
    re = AnyNumber(Chain("na ")) + Chain("Batman!")

    assert re.match("Batman!")
    assert re.match("na Batman!")
    assert re.match("na na Batman!")
    assert re.match("na na na Batman!")
    assert re.match("na na na na Batman!")
    assert not re.match("na na ")
    assert not re.match("na na Batman!!")


def test_range():
    re = Range("a")

    assert re.match("")
    assert re.match("a")
    assert re.match("aaaaa")

    re = Range("a", min=3)

    assert not re.match("")
    assert not re.match("a")
    assert not re.match("aa")
    assert re.match("aaa")
    assert re.match("aaaaaaaaaaaaa")

    re = Range("a", max=4)

    assert re.match("")
    assert re.match("a")
    assert re.match("aa")
    assert re.match("aaa")
    assert re.match("aaaa")
    assert not re.match("aaaaa")

    re = Range("a", min=2, max=3) + Symbol("b")

    assert not re.match("b")
    assert not re.match("ab")
    assert re.match("aab")
    assert re.match("aaab")
    assert not re.match("aaaab")
