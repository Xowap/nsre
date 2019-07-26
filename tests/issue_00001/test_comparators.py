from nsre.comparators import (
    AttributeHasValue,
    InList,
    InSet,
    IsInstance,
    KeyHasValue,
    Neg,
)


def test_set_comparator():
    m = InSet("abc")
    assert m == "a"
    assert m == "b"
    assert m == "c"
    assert m != "d"


def test_list_comparator():
    m = InList("abc")
    assert m == "a"
    assert m == "b"
    assert m == "c"
    assert m != "d"


def test_instance_comparator_single():
    class A:
        pass

    class B:
        pass

    m = IsInstance(A)

    assert m == A()
    assert m != B()


def test_instance_comparator_sequence():
    class A:
        pass

    class B:
        pass

    m = IsInstance(A, B)

    assert m == A()
    assert m == B()


def test_attribute_comparator():
    class A:
        def __init__(self, foo):
            self.foo = foo

    m = AttributeHasValue("foo", "bar")

    assert m == A("bar")
    assert m != A("baz")
    assert m is not None


def test_key_comparator():
    m = KeyHasValue("foo", "bar")

    assert m == {"foo": "bar"}
    assert m != {"foo": "baz"}
    assert m != {}


def test_neg_comparator():
    m = Neg("a")

    assert m != "a"
    assert m == "b"
    assert m == "c"

    m = Neg(KeyHasValue("foo", "bar"))

    assert m != {"foo": "bar"}
    assert m == {"foo": "baz"}
    assert m == {}
