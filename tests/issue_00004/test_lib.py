from nsre import RegExp
from nsre.lib import *
from nsre.lib import (
    _tag_attr_name,
    _tag_attr_quote,
    _tag_attr_savage,
    _tag_attr_val_quote_1,
    _tag_attr_val_quote_2,
    _tag_attr_val_savage,
    _tag_inside,
)


def test_basic_python():
    assert RegExp.from_ast(numerics).match("42")
    assert not RegExp.from_ast(alphas).match("42")
    assert not RegExp.from_ast(ascii_alphas).match("éléphant")


def test_domain_name():
    re = RegExp.from_ast(domain_name)

    assert not re.match("com")
    assert re.match("foo.com")
    assert re.match("bar.foo.com")
    assert re.match("bar.foo-bar.com")
    assert re.match("bar.xn--hello.com")
    assert not re.match("bar.foo--bar.com")
    assert not re.match("a b")
    assert not re.match("foo.bar--baz.com")


def test_email():
    re = RegExp.from_ast(email)

    # assert not re.match("foo")
    # assert not re.match("foo@bar")
    assert re.match("foo@bar.com")
    assert re.match("foo.bar+baz@bar.com")


def test_url():
    re = RegExp.from_ast(url)

    assert not re.match("foo")
    assert not re.match("foo.com/bar")
    assert re.match("http://something.com")
    assert re.match("https://something.com/#pouet")
    assert re.match("https://something.com/?foo=bar%20baz")

    m = re.match(
        "https://user:pass@domain.com/path/to/thing?query=foo&bar=baz#thing",
        join_trails=True,
    )
    assert m["proto"].trail == "https"
    assert m["auth"]["user"].trail == "user"
    assert m["auth"]["password"].trail == "pass"
    assert m["domain"].trail == "domain.com"
    assert m["path"].trail == "path/to/thing"
    assert m["query"].trail == "query=foo&bar=baz"
    assert m["hash"].trail == "thing"


def test_html_tag_parts():
    return  # TODO make this work

    assert RegExp.from_ast(_tag_attr_name).match("foo")
    m = RegExp.from_ast(_tag_attr_name).match("foo-bar")
    assert len(m) == 1
    assert not RegExp.from_ast(_tag_attr_name).match("foo-bar/")
    assert not RegExp.from_ast(_tag_attr_name).match("foo-bar=")

    assert RegExp.from_ast(_tag_attr_val_quote_1).match("'foo'")
    assert RegExp.from_ast(_tag_attr_val_quote_1).match("'foo pouet'")
    m = RegExp.from_ast(_tag_attr_val_quote_1).match("'foo pouet /'")
    assert len(m) == 1
    assert not RegExp.from_ast(_tag_attr_val_quote_1).match("'foo pouet'/")
    assert not RegExp.from_ast(_tag_attr_val_quote_1).match("'foo >'")
    assert not RegExp.from_ast(_tag_attr_val_quote_1).match("'foo''bar'")

    assert RegExp.from_ast(_tag_attr_val_quote_2).match('"foo"')
    assert RegExp.from_ast(_tag_attr_val_quote_2).match('"foo pouet"')
    m = RegExp.from_ast(_tag_attr_val_quote_2).match('"foo pouet /"')
    assert len(m) == 1
    assert not RegExp.from_ast(_tag_attr_val_quote_2).match('"foo pouet"/')
    assert not RegExp.from_ast(_tag_attr_val_quote_2).match('"foo >"')

    assert RegExp.from_ast(_tag_attr_savage).match("foo")
    m = RegExp.from_ast(_tag_attr_savage).match("foo-bar")
    assert len(m) == 1
    assert not RegExp.from_ast(_tag_attr_savage).match("foo-bar/")
    assert not RegExp.from_ast(_tag_attr_savage).match("foo-bar baz")

    assert RegExp.from_ast(_tag_attr_quote).match('foo="bar"')
    assert RegExp.from_ast(_tag_attr_quote).match('foo =   "bar"')
    m = RegExp.from_ast(_tag_attr_quote).match("foo-bar =   'baz'", join_trails=True)
    assert len(m) == 1
    assert m["name"].trail == "foo-bar"
    assert m["value"].trail == "baz"
    assert not RegExp.from_ast(_tag_attr_quote).match("foo-bar =   'baz'/")
    assert not RegExp.from_ast(_tag_attr_quote).match("foo-bar = baz")
    assert not RegExp.from_ast(_tag_attr_quote).match("foo='bar' bar='baz'")

    m = RegExp.from_ast(_tag_inside).match(
        "foo=bar baz='bar'yo=\"sup\"", join_trails=True
    )
    assert len(m) == 1
    attrs = m[0]
    assert attrs[0]["name"] == "foo"
    assert attrs[0]["value"] == "bar"
    assert attrs[1]["name"] == "baz"
    assert attrs[1]["value"] == "bar"
    assert attrs[2]["name"] == "yo"
    assert attrs[2]["value"] == "sup"


def test_html_tag():
    return  # TODO make this work

    re = RegExp.from_ast(html_tag)

    m = re.match("<img width=42 height='312'src=\"foo.jpg\"/>", join_trails=True)
    assert len(m) == 1
    tag = m[0]
    assert tag["name"].trail == "img"
    attrs = tag.children["attr"]
    assert attrs[0]["name"] == "width"
    assert attrs[0]["value"] == "42"
    # assert attrs[1]["name"] == "height"
    # assert attrs[1]["value"] == "312"
    # assert attrs[2]["name"] == "src"
    # assert attrs[2]["value"] == "foo.jpg"
