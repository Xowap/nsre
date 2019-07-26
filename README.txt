Non-String Regular Expressions
==============================

Regular expressions are used to match strings of characters, however the
concept can be applied to anything else. This engine allows you to match
any list of any type of objects using the same kind of constructs that
regular expressions allow.

The algorithm is (far away but) based on `this
article <https://swtch.com/~rsc/regexp/regexp1.html>`__ by Russ Cox, aka
uses the Thomson NFA algorithm (because it's apparently more efficient
but mostly because it's the first explanation of a RE engine that I
understood).

However the package doesn't support (yet?) the regular expression syntax
that everybody is used to (because it allows to do different things).

    **Note** — The current implementation is a pile of crap because I
    have no idea what I'm doing

Installation
------------

::

    pip install nsre

Then from your project you can

.. code:: python

    from nsre import *

Concept demo
------------

By example, suppose that you have a list of dictionaries with a ``type``
key which indicates the type of content. You want to check certain
patterns in that list. Suppose you want a series if ``image`` that might
have an attached ``caption`` then all of that is followed by a series of
``text``.

Conceptually, it would like like this

::

    (image caption?)* text+

Which once translated into NSRE looks like this

.. code:: python

    from nsre import *

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

Examples
--------

Because all of that is very abstract, let's have a look at more
examples:

String RE
~~~~~~~~~

Suppose that you want to `match a
string <https://dev.to/xowap/the-string-matching-regex-explained-step-by-step-4lkp>`__,
the traditional RE would be:

::

    "([^"\\]|\\.)*"

You can translate this into:

.. code:: python

    re = (
        Symbol('"')
        + AnyNumber(Symbol(Neg(InSet('"\\'))) | Chain(["\\", All()]))
        + Symbol('"')
    )

Email validation
~~~~~~~~~~~~~~~~

There is a notable debate around how to validate email addresses,
however let's consider for the exercise the following expression:

::

    [a-z]+([\.-][a-z]+)*@[a-z]+([\.\-][a-z]+)*\.[a-z]+

Now let's see how that translates in NSRE:

.. code:: python

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

    assert re.match("remy.sanchez@with-madrid.com")

Reference
---------

There is two kind of objects provided:

-  Comparators — It's mostly the equivalent of writing ``a`` or
   ``[abc]`` in a regular expression. It will do a test (equal, is
   instance of, etc) on the considered value to see if it's a match.
-  FSM — Builds the finite-state machine that will be used to test the
   regular expression. Those objects match the constructs like ``*`` or
   ``?``.

Comparators
~~~~~~~~~~~

``InSet``
^^^^^^^^^

Checks if the compared value is found within a set (faster than finding
it in a list but it means that the base type T has to be hashable).

.. code:: python

    assert Symbol(InSet([1, 2, 3])).match([1])

``InList``
^^^^^^^^^^

Checks if the compared value is found within a list. It means that the
base type T has to be comparable with ``__eq__()``.

.. code:: python

    assert Symbol(InList([1, 2, 3])).match([1])

``IsInstance``
^^^^^^^^^^^^^^

Tests if the provided value is an instance of any of the classes passed
to the constructor.

.. code:: python

    assert Symbol(IsInstance(A, B, C)).match([A()])

``AttributeHasValue``
^^^^^^^^^^^^^^^^^^^^^

Tests the compared value to see if their ``attribute`` has the right
``value``.

.. code:: python

    class Foo:
        foo = 'bar'

    assert Symbol(AttributeHasValue('foo', 'bar')).match([Foo()])

``KeyHasValue``
^^^^^^^^^^^^^^^

Tests the compared Dict to see if their ``key`` has the right ``value``.

.. code:: python

    assert Symbol(KeyHasValue('foo', 'bar')).match([{'foo': 'bar'}])

``Neg``
^^^^^^^

Negates the output of any comparator or raw value

.. code:: python

    assert Symbol(Neg('a')).match('b')
    assert not Symbol(Neg('a')).match('a')

``All``
^^^^^^^

Matches anything.

.. code:: python

    assert Symbol(All()).match('a')
    assert Symbol(All()).match([1])

``ChrRanges``
^^^^^^^^^^^^^

For a given character, checks that it is within a given set of ranges.

.. code:: python

    assert Symbol(ChrRanges(('a', 'z'), ('A', 'Z'))).match('X')

FSM
~~~

Symbol
^^^^^^

Matches exactly 1 symbol

.. code:: python

    re = Symbol("a")

    assert re.match("a")
    assert not re.match("b")
    assert not re.match("aa")

Chain
^^^^^

Matches exactly a chain of symbols

.. code:: python

    re = Chain('hello')

    assert re.match('hello')

``+``
^^^^^

Puts two rules next to each other

.. code:: python

    re = Symbol('h') + Symbol('e') + Symbol('l') + Symbol('l') + Symbol('o')

    assert re.match('hello')

``|``
^^^^^

Branches different options

.. code:: python

    re = Chain('My name is ') + (Chain('Foo') | Chain('Bar'))

    assert re.match('My name is Foo')

Maybe (equivalent to ``?``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Matches 0 or 1 occurrences

.. code:: python

    re = Chain('Call me') + Maybe(Chain(' maybe'))

    assert re.match('Call me')
    assert re.match('Call me maybe')

AnyNumber (equivalent to ``*``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Matches 0 or more occurrences

.. code:: python

    re = AnyNumber(Chain("na ")) + Chain("Batman!")

    assert re.match("na na na na Batman!")

Range (equivalent to ``{min,max}`` and ``+``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Matches from min to max number of occurrences. By default ``min`` is 0
and ``max`` is infinity.

.. code:: python

    re = Maybe(Chain('Cam')) + Range('a', min=3) + Chain('rgh')

    assert re.match('Camaaaaaaaargh')

Performance
-----------

It's terrible

Development
-----------

There is no dependencies per se for NSRE, however there is several
packages to help on the development in ``requirements.txt``.

Install the dev dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install -r requirements.txt

Update dependencies
~~~~~~~~~~~~~~~~~~~

Edit ``requirements.txt`` then run

::

    make venv

Run tests
~~~~~~~~~

Unit tests run with ``pytest``.

::

    make test
