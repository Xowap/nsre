AST
===

.. py:currentmodule:: nsre.ast

The whole idea of the :py:mod:`nsre.ast` module is to help you building the
RegExp's graph using regular Python syntax.

If you are wondering what the fuck is this thing about graphs, don't worry too
much, let's just say that you need the AST to build a regular expression. You
can know more in the
`inspirational article <https://swtch.com/~rsc/regexp/regexp1.html>`_.

Usage
-----

The idea was to create something convenient and familiar to use. As you might
have read, there is on one side *matchers* which will validate tokens and on
the other side AST *nodes* that will help you build the regular expression
itself.

Let's consider this:

.. code-block:: python

    from nsre import *

    hi = Final(Eq("h")) + Final(Eq("e")) + Final(Eq("!"))
    assert re = RegExp.from_ast(hi).match("hi!")

What you see here is

  - :code:`Eq(...)` is a  matcher that matches a token equal to the reference
    passed to its constructor
  - :code:`Final(...)` is a final node, aka a node that will be used for
    matching
  - :code:`X + Y` by adding together two nodes, you expect a concatenation.

Example
+++++++

You can look into the :py:mod:`nsre.lib` module to see many examples of regular
expressions being built. Let's have a look at the email parsing expression.

One of the largest advantages of this is that you can re-use the same AST
several times to build your regular expressions. Let's say that you already
have an expression able to match a domain name, you can use it in an email
address expression.

.. code-block:: python

    email_part = ascii_alnums
    email_sep = Final(In(["+", "."]))
    email_user = email_part + AnyNumber(email_sep + email_part)
    email = email_user + seq("@") + domain_name

    re = RegExp.from_ast(email)
    assert re.match('remy@with-madrid.com')

Please note that here :py:func:`nsre.shortcuts.seq` is a shortcut that will
automatically create a concatenation of :code:`Final` nodes with a :code:`Eq`
matcher.

Operations
++++++++++

Let's review all the operations that you can do with nodes. In those examples,
let's suppose that :code:`node_a` would match the letter :code:`"a"`,
:code:`node_b` the letter :code:`"b"`, and so forth.

Concatenation
~~~~~~~~~~~~~

Expect two nodes to be consecutive using the :code:`+` operator.

.. code-block:: python

    exp = node_a + node_b + node_c
    # Would match "abc"

Alternation
~~~~~~~~~~~

Expect either one node either the other using the :code:`|` operator.

.. code-block:: python

    exp = node_a + (node_b | node_c)
    # Would match either "ab" or "ac"

Multiplication
~~~~~~~~~~~~~~

Multiply a node in order to indicate repetition. You can multiply by:

- An int, to get exactly this number of occurrences
- :code:`slice(X, None)` to get from X to +inf occurrences
- :code:`slice(None, X)` to get from 0 to X occurrences
- :code:`slice(X, Y)` to get from X to Y occurrences

.. code-block:: python

    exp = node_a * slice(1, 3)
    # Would match "a", "aa" or "aaa"

Capture
~~~~~~~

To report the content that was matched into a capture group, simply name the
capture group using brackets.

.. code-block:: python

    exp = node_a + (node_b | node_c)['foo']
    # For "ab" group "foo" would contain "b"

Reference
---------

On top of using the Python syntax as shortcuts, you can directly create
instances of nodes. It's sometimes more convenient to do so.

.. automodule:: nsre.ast
    :members:
