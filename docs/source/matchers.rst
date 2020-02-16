Matchers
========

.. py:currentmodule:: nsre.matchers

The goal of matchers is to transform tokens into output. That's where NSRE is
pretty different from any other regular expression engine: tokens are not
necessarily validated as-is. Instead, the matcher can decide how it likes them
and the :code:`Match` objects that your receive after the completion of the
matching not contain the original tokens but rather the matched text.

Now you're like, what the fuck?

Let's have a look.

.. code-block:: python

    from nsre import *

    f = Final(OutOf("f"))
    o = Final(OutOf("o"))
    b = Final(OutOf("b"))
    a = Final(OutOf("a"))
    r = Final(OutOf("r"))

    data = [
        ('f', 'b'),
        ('o', 'a'),
        ('o', 'r'),
    ]

    re = RegExp.from_ast(((f + o + o) | (b + a + r))["capture"])

    m = re.match(data, join_trails=True)
    assert {mm["capture"].trail for mm in m} == {"foo", "bar"}

As you can see, we use the :py:class:`OutOf` matcher, which helps selecting
the right token out of a series of presented tokens.

The :code:`data` passed into the regular expression is not, as you usually
would expect, a string but rather a sequence of tuples that each contain
several letters.

The engine will match either :code:`"foo"` either :code:`"bar"` if it can be
found in the data, or both at the same time if both are found.

Reference
---------

There is a lot more matchers than this which all do some specific things.

.. automodule:: nsre.matchers
    :members:
