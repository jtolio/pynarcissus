# PyNarcissus

PyNarcissus is a Javascript parser, and not a very Pythonic one
at that. Furthermore, documentation is poor.

Currently this is just a Javascript parser. Javascript evaluation might be a little more tricky since the Narcissus interpreter implements a bunch of stuff metacircularly.

Also, check out the original Narcissus: http://mxr.mozilla.org/mozilla/source/js/narcissus/

This project is interesting not only for the fact that a Javascript parser has been written in Python, but because the port was as direct a transliteration as possible, the Javascript Narcissus parser and this Python one make an interesting case study in the differences between Javascript and Python.

Perhaps I'll post a few interesting line by line comparisons, but in the interim time, jsparser.py is equivalent in function (and indeed incredibly similar at the source level) to Narcissus' jsdefs.js and jsparse.js. You'll have to blame Brendan Eich if you're unhappy with the overall structure and design.

There is also [a conversion routine](https://github.com/jtolds/pynarcissus/blob/master/sexp.py) that turns a Javascript parse tree into rudimentary S-expressions.

*New*: Check out [pyjon](http://code.google.com/p/pyjon)!

As of 2009-02-19, PyNarcissus has been engineered such that
```
str(parse("javascript code"))
```
in Python is identical to
```
parse("javascript code").toString()
```
in Javascript. It was this feature that allowed for robust testing of the
parser in the absence of a Javascript evaluator, as the output of the Python
version was compared to the output of the Javascript version over all of the
Spidermonkey Javascript tests.

There are a few differences in output, as Python handles both floating point
precision and non-ascii characters slightly differently.

It is expected that future versions of PyNarcissus will be more Pythonic in many
ways, and will break this string-conversion compatibility with the Javascript
Narcissus.

