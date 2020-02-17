Expressions library
===================

.. py:currentmodule:: nsre.lib

This module contains AST nodes which already handle the most common tasks.

Example
+++++++

That's how to use the library

.. code-block:: python

    from nsre import *
    from nsre.lib import email

    re = RegExp.from_ast(email)
    assert re.match('user@domain.com')

List
++++

Here are all the available nodes

Python string tests
-------------------

There is a series of nodes available which correspond to Python's builtin
string tests.

By example, :code:`ascii_alpha` matches characters that Python would categorize
as :code:`s.isascii()` and :code:`s.isalpha()`. Also, the plural version
indicates a repetition of "one or more" of those characters. Literally,

.. code-block:: python

    ascii_alnum = Final(Test(lambda t: t.isalnum() and t.isascii()))
    ascii_alnums = ascii_alnum * slice(1, None)

You have here the full list of those constants:

    - :code:`alnum`
    - :code:`alnums`
    - :code:`alpha`
    - :code:`alphas`
    - :code:`ascii_alnum`
    - :code:`ascii_alnums`
    - :code:`ascii_alpha`
    - :code:`ascii_alphas`
    - :code:`ascii_decimal`
    - :code:`ascii_decimals`
    - :code:`ascii_digit`
    - :code:`ascii_digits`
    - :code:`ascii_lower_alnum`
    - :code:`ascii_lower_alnums`
    - :code:`ascii_lower_alpha`
    - :code:`ascii_lower_alphas`
    - :code:`ascii_numeric`
    - :code:`ascii_numerics`
    - :code:`ascii_printable`
    - :code:`ascii_printables`
    - :code:`ascii_space`
    - :code:`ascii_spaces`
    - :code:`ascii_upper_alnum`
    - :code:`ascii_upper_alnums`
    - :code:`ascii_upper_alpha`
    - :code:`ascii_upper_alphas`
    - :code:`decimal`
    - :code:`decimals`
    - :code:`digit`
    - :code:`digits`
    - :code:`lower_alnum`
    - :code:`lower_alnums`
    - :code:`lower_alpha`
    - :code:`lower_alphas`
    - :code:`numeric`
    - :code:`numerics`
    - :code:`printable`
    - :code:`printables`
    - :code:`space`
    - :code:`spaces`
    - :code:`spaces_maybe`
    - :code:`upper_alnum`
    - :code:`upper_alnums`
    - :code:`upper_alpha`
    - :code:`upper_alphas`
    - :code:`hex_digit`
    - :code:`hex_digits`

Common patterns
---------------

Other patterns are available:

    - :code:`domain_name`: A domain name
    - :code:`email`: An email address
    - :code:`url`: An URL (HTTP or HTTPS)
    - :code:`html_tag`: A HTML opening or self-closing tag
