from nsre.matcher import (
    AttributeMatcher,
    EqualMatcher,
    InstanceMatcher,
    KeyMatcher,
    ListMatcher,
    SetMatcher,
)


def test_set_matcher():
    m = SetMatcher("abc")
    assert m.match("a")
    assert m.match("b")
    assert m.match("c")
    assert not m.match("d")


def test_list_matcher():
    m = ListMatcher("abc")
    assert m.match("a")
    assert m.match("b")
    assert m.match("c")
    assert not m.match("d")


def test_equal_matcher():
    m = EqualMatcher("a")
    assert m.match("a")
    assert not m.match("b")


def test_instance_matcher_single():
    class A:
        pass

    class B:
        pass

    m = InstanceMatcher(A)

    assert m.match(A())
    assert not m.match(B())


def test_instance_matcher_sequence():
    class A:
        pass

    class B:
        pass

    m = InstanceMatcher((A, B))

    assert m.match(A())
    assert m.match(B())


def test_attribute_matcher():
    class A:
        def __init__(self, foo):
            self.foo = foo

    m = AttributeMatcher("foo", "bar")

    assert m.match(A("bar"))
    assert not m.match(A("baz"))
    assert not m.match(None)


def test_key_matcher():
    m = KeyMatcher("foo", "bar")

    assert m.match({"foo": "bar"})
    assert not m.match({"foo": "baz"})
    assert not m.match({})
