# pathlike
SVG-Path like parsing for command line and other parsing.

Pathlike does parsing of strings into executable calls like svg-pathd parsing.

See:
https://www.w3.org/TR/SVG/paths.html

The goal here is to convey to CLI or other parsing you may need the same highly short syntax found in SVG Path d attributes.

* All instructions are expressed as one character.
* Superfluous white space and separators (such as commas) may be eliminated; for instance, the following contains unnecessary spaces:
    * M 100 100 L 200 200
    * It may be expressed more compactly as:
    * M100 100L200 200
* A command letter may be eliminated if an identical command letter would otherwise precede it; for instance, the following contains an unnecessary second "L" command:
    * M 100 200 L 200 100 L -100 -200
    * It may be expressed more compactly as:
    * M 100 200 L 200 100 -100 -200

The path data syntax is a prefix notation (i.e., commands followed by parameters). The only allowable decimal point is a Unicode U+0046 FULL STOP (".") character (also referred to in Unicode as PERIOD, dot and decimal point) and no other delimiter characters are allowed. (For example, the following is an invalid numeric value in a path data stream: "13,000.56". Instead, say: "13000.56".)

We are making parsing *like* that parsing, but with arbitrarily defined commands. 

* The commands can be any single letter in ascii in upper or lower case that is not the letter 'e' (reserved for floats)

# Types:

* `float` float type is expects a float number.
* `int` int type expects an string integer.
* `bool` bool type expects either a 1 or 0. This is not keyword like True or False it is a flagged 0 or 1. Also, note because of the greedy nature flags can be compounded together without issue if we are expecting `bool, float, str` we can give the pathlike string: `11.2Yellow` and this is bool: `1`, float: `1.2` and str: `Yellow`.
* `str` string types can contain letters and thus require some additional delimiting, there are two string delimiting. Either COMMA_WS characters `[ ,\t\n\x09\x0A\x0C\x0D]` or quoted syntax "A string with spaces etc inside of it.".
* other: other types are taken as strings and these are passed into the type def we are given. The only permitted initialization used on an undefined type is a string. We treat the parsing exactly like a string. For example if we have `complex` we can call that with `100+2j` and it will feed that as a string into the `complex('100+2j')`. Note that undefined types must be parsed with string delimiting methods. They must contain a COMMA_WS character or be quoted.

#Examples:

eg: (assume `j` takes a four floats).
Assuming: `@command(parser, "j", float, float)`

`myscript.py j200 50 30-7qql200.3`

This runs arbitrary command j with (200, 50), j with (30, -7), command q, command q, command l with (200.3)


eg.
```python
@command(parser, "sS", str)
def p(string):
    print(string)
```

Using that:

> myscript.py s"Hello World!"
> Hello World!

Using that command with multiple operators: 

> myscript.py s"Hello World!""Here I am!"
> Hello World!
> Here I am!

Repeated instances make repeated calls to the same command.

Alternatively if we are not using quoted syntax the remainder of the current COMMAWSP delinated element is used.

myscript.py sHi

This is treated as s("Hi") rather than s, H, i

myscript.py s Hi.

Is likewise treated as s("Hi.") rather than s, H, i

# Example Script

```python
from sys import argv
from pathlike import PathlikeParser, command

parser = PathlikeParser()

@command(parser, "sS", str)
def print_this_string(q):
    print(q)

parser.parse(argv[1:])
```

To mark a particular function as linked with some characters, we use decorators. Specifically we define the function with the `@command` annotation.

We denote additional values with additional types:

```python
@command('j', float, float, str)
def funct(a0_float, a1_float, a2_str)
    pass
```

We also only support principle types since everything needs to be known. Unknown types are treated
like string commands and we attempt to type cast them.

`@command('f', Color)` expects 1 argument that consists of a Color class. It is assumed that Color can accept the string "Blue"

myscript.py f"Blue"

We can also do multiple values here. f"Blue""Red"
