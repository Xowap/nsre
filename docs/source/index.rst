Welcome to NSRE's documentation!
================================

NSRE (Non-String Regular Expressions) is a new spin at regular expressions.
It's really abstract, even compared to regular expressions as you know them,
but it's also pretty powerful for some uses.

Here's the twist: what if regular expressions could, instead of matching just
character strings, match any sequence of anything?

.. code-block:: python

    from nsre import *

    re = RegExp.from_ast(seq('hello, ') + (seq('foo') | seq('bar')))
    assert re.match('hello, foo')

The main goal here is matching NLU grammars when there is several possible
interpretations of a single word, however there is a lot of other things that
you could do. You just need to understand what NSRE is and apply it to
something.

.. note::
   This is inspired by
   `this article <https://swtch.com/~rsc/regexp/regexp1.html>`_ from Russ Cox,
   which explains how Thompson NFA work, except that I needed to add some
   features and then the implementation is much less elegant because I actually
   don't know what I'm doing. But it seems to be working.

Let's go
--------

.. toctree::
   :maxdepth: 2

   getting_started
   regexp
   ast
   matchers
   shortcuts
   lib


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
