from nsre import *


def test_string():
    # "([^"\\]|\\.)*"

    re = (
        Symbol('"')
        + AnyNumber(Symbol(Neg(InSet('"\\'))) | Chain(["\\", All(str)]))
        + Symbol('"')
    )

    assert re.match('"foo"')
    assert re.match('"foo \\" bar"')
    assert not re.match('"foo')


def test_email():
    # [a-z]+([\.-][a-z]+)*@[a-z]+([\.\-][a-z]+)*\.[a-z]+

    letter = ChrRanges(("a", "z"))
    join = ChrRanges((".", "."), ("-", "-"))

    re = (
        Range(letter, min=1)
        + AnyNumber(Symbol(join) + Range(letter, min=1))
        + Symbol("@")
        + Range(letter, min=1)
        + AnyNumber(Symbol(join) + Range(letter, min=1))
        + Symbol(".")
        + Range(letter, min=1)
    )

    assert re.match("foo.bar@acme-corp.com")
    assert not re.match("foo..bar@acme-corp.com")


def test_dict():
    # (image caption?)* text+

    re = AnyNumber(
        Symbol(KeyHasValue("type", "image")) + Maybe(KeyHasValue("type", "caption"))
    ) + Range(KeyHasValue("type", "text"), min=1)

    assert re.match(
        [
            {"type": "image", "url": "https://img1.jpg"},
            {"type": "image", "url": "https://img2.jpg"},
            {"type": "image", "url": "https://img3.jpg"},
            {"type": "caption", "text": "Image 3"},
            {"type": "image", "url": "https://img4.jpg"},
            {"type": "caption", "text": "Image 4"},
            {"type": "image", "url": "https://img5.jpg"},
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "Foo"},
            {"type": "text", "text": "Bar"},
        ]
    )

    assert re.match(
        [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "Foo"},
            {"type": "text", "text": "Bar"},
        ]
    )

    assert re.match(
        [
            {"type": "image", "url": "https://img1.jpg"},
            {"type": "image", "url": "https://img2.jpg"},
            {"type": "image", "url": "https://img3.jpg"},
            {"type": "caption", "text": "Image 3"},
            {"type": "image", "url": "https://img4.jpg"},
            {"type": "caption", "text": "Image 4"},
            {"type": "image", "url": "https://img5.jpg"},
            {"type": "text", "text": "Hello"},
        ]
    )

    assert re.match(
        [
            {"type": "image", "url": "https://img1.jpg"},
            {"type": "image", "url": "https://img2.jpg"},
            {"type": "image", "url": "https://img3.jpg"},
            {"type": "image", "url": "https://img4.jpg"},
            {"type": "image", "url": "https://img5.jpg"},
            {"type": "text", "text": "Hello"},
        ]
    )

    assert not re.match(
        [
            {"type": "image", "url": "https://img1.jpg"},
            {"type": "image", "url": "https://img2.jpg"},
            {"type": "image", "url": "https://img3.jpg"},
            {"type": "image", "url": "https://img4.jpg"},
            {"type": "image", "url": "https://img5.jpg"},
        ]
    )
