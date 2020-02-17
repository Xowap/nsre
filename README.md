Non-String Regular Expressions
==============================

[![Build Status](https://travis-ci.org/Xowap/nsre.svg?branch=develop)](https://travis-ci.org/Xowap/nsre)

NSRE (Non-String Regular Expressions) is a new spin at regular expressions.
It's really abstract, even compared to regular expressions as you know them,
but it's also pretty powerful for some uses.

Here's the twist: what if regular expressions could, instead of matching just
character strings, match any sequence of anything?

```python
from nsre import *

re = RegExp.from_ast(seq('hello, ') + (seq('foo') | seq('bar')))
assert re.match('hello, foo')
```

The main goal here is matching NLU grammars when there is several possible
interpretations of a single word, however there is a lot of other things that
you could do. You just need to understand what NSRE is and apply it to
something.

> **Note** &mdash; This is inspired by
> [this article](https://swtch.com/~rsc/regexp/regexp1.html) from Russ Cox,
> which explains how Thompson NFA work, except that I needed to add some
> features and then the implementation is much less elegant because I actually
> don't know what I'm doing. But it seems to be working.

## Documentation

[✨ **Documentation is there** ✨](http://nsre.rtfd.io/)

## Licence

This library is provided under the terms of the [WTFPL](./LICENSE).

If you find it useful, you can have a look at the
[contributors](https://github.com/Xowap/nsre/graphs/contributors) page to
know who helped.
