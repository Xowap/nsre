from .ast import *
from .matchers import *
from .shortcuts import *

__all__ = [
    "alnum",
    "alnums",
    "alpha",
    "alphas",
    "ascii_alnum",
    "ascii_alnums",
    "ascii_alpha",
    "ascii_alphas",
    "ascii_decimal",
    "ascii_decimals",
    "ascii_digit",
    "ascii_digits",
    "ascii_lower_alnum",
    "ascii_lower_alnums",
    "ascii_lower_alpha",
    "ascii_lower_alphas",
    "ascii_numeric",
    "ascii_numerics",
    "ascii_printable",
    "ascii_printables",
    "ascii_space",
    "ascii_spaces",
    "ascii_upper_alnum",
    "ascii_upper_alnums",
    "ascii_upper_alpha",
    "ascii_upper_alphas",
    "decimal",
    "decimals",
    "digit",
    "digits",
    "lower_alnum",
    "lower_alnums",
    "lower_alpha",
    "lower_alphas",
    "numeric",
    "numerics",
    "printable",
    "printables",
    "space",
    "spaces",
    "spaces_maybe",
    "upper_alnum",
    "upper_alnums",
    "upper_alpha",
    "upper_alphas",
    "hex_digit",
    "hex_digits",
    "domain_name",
    "url",
    "email",
    "html_tag",
]


if hasattr(str, "isascii"):

    def _isascii(s: str) -> bool:
        """
        Use regular isascii test in Python 3.7+
        """

        return s.isascii()


else:

    def _isascii(s: str) -> bool:
        """
        Support for isascii test in Python 3.6
        """

        if not s:
            return False

        for c in s:
            if ord(c) > ord("\u007f"):
                return False

        return True


# Basic Python string tests
alnum = Final(Test(lambda t: t.isalnum()))
alnums = alnum * slice(1, None)
alpha = Final(Test(lambda t: t.isalpha()))
alphas = alpha * slice(1, None)
ascii_alnum = Final(Test(lambda t: t.isalnum() and _isascii(t)))
ascii_alnums = ascii_alnum * slice(1, None)
ascii_alpha = Final(Test(lambda t: t.isalpha() and _isascii(t)))
ascii_alphas = ascii_alpha * slice(1, None)
ascii_decimal = Final(Test(lambda t: t.isdecimal() and _isascii(t)))
ascii_decimals = ascii_decimal * slice(1, None)
ascii_digit = Final(Test(lambda t: t.isdigit() and _isascii(t)))
ascii_digits = ascii_digit * slice(1, None)
ascii_lower_alnum = Final(Test(lambda t: t.isalnum() and t.islower() and _isascii(t)))
ascii_lower_alnums = ascii_lower_alnum * slice(1, None)
ascii_lower_alpha = Final(Test(lambda t: t.isalpha() and t.islower() and _isascii(t)))
ascii_lower_alphas = ascii_lower_alpha * slice(1, None)
ascii_numeric = Final(Test(lambda t: t.isnumeric() and _isascii(t)))
ascii_numerics = ascii_numeric * slice(1, None)
ascii_printable = Final(Test(lambda t: t.isprintable() and _isascii(t)))
ascii_printables = ascii_printable * slice(1, None)
ascii_space = Final(Test(lambda t: t.isspace() and _isascii(t)))
ascii_spaces = ascii_space * slice(1, None)
ascii_upper_alnum = Final(Test(lambda t: t.isalnum() and t.isupper() and _isascii(t)))
ascii_upper_alnums = ascii_upper_alnum * slice(1, None)
ascii_upper_alpha = Final(Test(lambda t: t.isalpha() and t.isupper() and _isascii(t)))
ascii_upper_alphas = ascii_upper_alpha * slice(1, None)
decimal = Final(Test(lambda t: t.isdecimal()))
decimals = decimal * slice(1, None)
digit = Final(Test(lambda t: t.isdigit()))
digits = digit * slice(1, None)
lower_alnum = Final(Test(lambda t: t.isalnum() and t.islower()))
lower_alnums = lower_alnum * slice(1, None)
lower_alpha = Final(Test(lambda t: t.isalpha() and t.islower()))
lower_alphas = lower_alpha * slice(1, None)
numeric = Final(Test(lambda t: t.isnumeric()))
numerics = numeric * slice(1, None)
printable = Final(Test(lambda t: t.isprintable()))
printables = printable * slice(1, None)
space = Final(Test(lambda t: t.isspace()))
spaces = space * slice(1, None)
spaces_maybe = space * slice(0, None)
upper_alnum = Final(Test(lambda t: t.isalnum() and t.isupper()))
upper_alnums = upper_alnum * slice(1, None)
upper_alpha = Final(Test(lambda t: t.isalpha() and t.isupper()))
upper_alphas = upper_alpha * slice(1, None)


# Hex
hex_digit = Final(ChrRanges(("a", "f"), ("A", "F"), ("0", "9")))
hex_digits = hex_digit * slice(1, None)


# Domain name
_dn_letter = ascii_alnum
_dn_sub_part = _dn_letter * slice(1, None)
_dn_part = Maybe(seq("xn--")) + _dn_sub_part + AnyNumber(seq("-") + _dn_sub_part)
domain_name = (
    _dn_part + AnyNumber(seq(".") + _dn_part) + seq(".") + _dn_letter * slice(2, None)
)


# Email address
_em_part = ascii_alnums
_em_sep = Final(In(["+", "."]))
_em_user = _em_part + AnyNumber(_em_sep + _em_part)
email = _em_user["user"] + seq("@") + domain_name["domain"]


# URL
_url_proto = (seq("http") + Maybe(seq("s")))["proto"] + seq("://")
_url_enc = (ascii_alnum | (seq("%") + hex_digit + hex_digit) | seq("+")) * slice(
    1, None
)
_url_auth = _url_enc["user"] + seq(":") + _url_enc["password"]
_url_path = Maybe(_url_enc + AnyNumber(seq("/") + _url_enc))
_url_query_var = _url_enc + Maybe(seq("=") + _url_enc)
_url_query = _url_query_var + AnyNumber(seq("&") + _url_query_var)
_url_hash = _url_enc
url = (
    _url_proto
    + Maybe(_url_auth["auth"] + seq("@"))
    + domain_name["domain"]
    + Maybe(seq("/") + _url_path["path"])
    + Maybe(seq("?") + _url_query["query"])
    + Maybe(seq("#") + _url_hash["hash"])
)


# HTML tag
_tag_attr_name = ascii_alnums + AnyNumber(seq("-") + ascii_alnums)
_tag_attr_val_quote_1 = seq("'") + AnyNumber(Final(Not(In("'>"))))["value"] + seq("'")
_tag_attr_val_quote_2 = seq('"') + AnyNumber(Final(Not(In('">'))))["value"] + seq('"')
_tag_attr_val_savage = AnyNumber(Final(Test(lambda t: not t.isspace() and t != "/")))
_tag_attr_quote = (
    _tag_attr_name["name"]
    + Maybe(
        spaces_maybe
        + seq("=")
        + spaces_maybe
        + (_tag_attr_val_quote_1 | _tag_attr_val_quote_2)
    )
)["attr"]
_tag_attr_savage = (
    _tag_attr_name["name"]
    + Maybe(spaces_maybe + seq("=") + spaces_maybe + _tag_attr_val_savage)
)["attr"]
# _tag_inside = AnyNumber(
#     (_tag_attr_savage + spaces) | (_tag_attr_quote + spaces_maybe)
# ) + Maybe(_tag_attr_savage | _tag_attr_quote)
_tag_inside = AnyNumber((_tag_attr_quote | _tag_attr_savage) + spaces) + Maybe(
    _tag_attr_savage | _tag_attr_quote
)
html_tag = (
    seq("<")
    + spaces_maybe
    + _tag_attr_name["name"]
    + spaces
    + _tag_inside["attr"]
    + spaces_maybe
    + (seq("/>") | seq(">"))
)
