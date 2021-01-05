# pathlike
SVG-Path like parsing for command line and other parsing.

Pathlike does parsing of strings into executable calls like svg-pathd parsing.

See:
https://www.w3.org/TR/SVG/paths.html

The goal of this project is to bring the easy compact path-like parsing to CLI (or other parsing). You may want the same very compact short syntax found in SVG Path Data, for other arbitrary routines.

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

We are making parsing *like* that SVG-Path parsing, but with arbitrarily defined commands. This could be used to parse SVG Paths, but it's intended to be more broadly functional than that.

* The commands can be any single letter in ascii in upper or lower case that is not the letter 'e' (reserved for floats)

# Types:

* `float` float type is expects a float number.
* `int` int type expects an string integer.
* `bool` bool type expects either a 1 or 0. This is not keyword like True or False it is a flagged 0 or 1. Also, note because of the greedy nature flags can be compounded together without issue if we are expecting `bool, float, str` we can give the pathlike string: `11.2Yellow` and this is bool: `1`, float: `1.2` and str: `Yellow`.
* `str` string types can contain letters, so these cannot take non-backtick quoted strings as multiple commands. The first string can be accepted without COMMA_WS characters, however if the first element of a new cycle is a string it must be backticked so that the we can determine whether this is more data of the original command or a new command.
* other: other types are taken as strings and these are passed into the type given in arguments. The only permitted initialization used on an undefined type is a `str`. We treat the parsing exactly like a string. For example if we have `complex` we can call that with `100+2j` and it will feed that as a string into the `complex('100+2j')`. Undefined types also have the same multi-call limiting factor of strings.

#Examples:

eg: (assume `j` takes a four floats).
Assuming: `@command(parser, "j", float, float)`

`myscript.py j200 50 30-7qql200.3`

This runs arbitrary command j with (200, 50), j with (30, -7), command q, command q, command l with (200.3)


eg.
```python
@command(parser, "sS", str)
def print_this_string(string):
    print(string)
```

Using that:

```
> myscript.py s`Hello World!`
> Hello World!
```

Using that command with multiple operators: 

```
> myscript.py s`Hello World!` `Here I am!`
> Hello World!
> Here I am!
```

The first string does not require backticks. Only strings with spaces and additional commands with strings.

```
> myscript.py sHi `Hello World!` `Here I am!`
> Hi!
> Hello World!
> Here I am!
```


If we apply additional data:

```
> myscript.py she sells seashells by the seashore
> he
> ells
> eashells
```

Note that it stops as soon as it reaches the word `by` and because `b` is not a recognized command. Parsing stops. This is consistent with the methods for svg path parsing.


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

`myscript.py fBlue`

We can also do multiple values here.
```
myscript.py f`Blue` `Red`
```

We don't however need to treat strings with backticks if the the first argument is a number-type:

For example if we have:
```
@command(parser, "aA", bool, str)
def rev(b, q):
    if b:
        print(q)
    else:
        print(q[::-1])
```


> myscript.py a 1yellow 0blue 1red 0backwards 1forwards
> yellow
> eulb
> red
> sdrawkcab
> forwards

Because the boolean comes before the string, we can determine that more commands are needed for the `a` command. We only need backticks to capture COMMA_WS characters or if the the more parsing is ambiguous. `yellow blue` would return None for the bool, which becomes `False` but the next iteration the first character is `b` which is a new command and is expected to be either `0` or `1`

