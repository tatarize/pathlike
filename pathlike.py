"""
Pathlike Parser parses command line arguments like svg paths.

The parsing of attributes is done in the same greedy form adjacent parsing as found in the
svg spec. However this is not intended to parse svg path objects but arbitrary command line
data. The general command is a single character followed by a series of numbers or flags these
are always allowed to repeat at the end of the series.

The commands can be any single letter ascii in upper or lower case that is not the letter 'e' (reserved for floats)

eg:
myscript.py j200 50 30-7qql200.3

This runs arbitrary command j with (200, 50, 30, and -7), command q, command q and command l with 200.3

in addition, some commands can accept strings these are expected to be placed into quotes:

eg.
myscript.py p"hello world"

Runs arbitrary command p with string "hello world".

myscript.py p"hello world""this is me" runs command p with "hello world" then command p with "this is me"

Repeated instances are make repeated calls to the same command.

Alternatively if we are not using quoted syntax the remainder of the current COMMAWSP delinated element is used.

myscript.py pHi

This is treated as p("Hi") rather than p, H, i

myscript.py p Hi.

Is likewise treated as p("Hi.") rather than p, H, i

---

To define a particular element we use decorators, due to the simplicity these commands accept their arguments
directly. There are no cases to permit optional flags or anything else.

@pathlike.command('j', arguments=(float, float, str))

We also only support principle types since everything needs to be known. Unknown types are treated
like string commands and we attempt to type cast them.

@pathlike.command('f', arguments=(Color)) expects 1 argument that consists of a color:

myscript.py f"Blue"


"""

import re


PATTERN_COMMAWSP = r'[ ,\t\n\x09\x0A\x0C\x0D]+'
PATTERN_FLOAT = '[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'

cmd_parse = [
    ('COMMAND', r'[a-df-zA-DF-Z]'),
    ('SKIP', PATTERN_COMMAWSP)
]
cmd_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in cmd_parse))

num_parse = [
    ('FLOAT', PATTERN_FLOAT),
    ('SKIP', PATTERN_COMMAWSP)
]
num_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in num_parse))

flag_parse = [
    ('FLAG', r'[01]'),
    ('SKIP', PATTERN_COMMAWSP)
]
flag_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in flag_parse))

str_parse = [
    ('QSTR', r'"[^"]*"'),
    ('SKIP', PATTERN_COMMAWSP),
    ('DSTR', r'[^ ,\t\n\x09\x0A\x0C\x0D]*')
]
str_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in str_parse))


def command(parser, letters, *arguments):
    def command_dec(func):
        parser.add_command(letters, func, arguments)
        return func
    return command_dec


class Command:
    def __init__(self, letter, cmd, arguments):
        self.letter = letter
        self.command = cmd
        self.arguments = arguments


class PathlikeParser:
    def __init__(self):
        self.commands = dict()
        self.pathd = None
        self.pos = 0
        self.limit = 0

    def add_command(self, letters, cmd, arguments):
        for letter in letters:
            self.commands[letter] = Command(letter, cmd, arguments)

    def _command(self):
        while self.pos < self.limit:
            match = cmd_re.match(self.pathd, self.pos)
            if match is None:
                return None  # Did not match at command sequence.
            self.pos = match.end()
            kind = match.lastgroup
            if kind == 'SKIP':
                continue
            return match.group()
        return None

    def _more(self):
        while self.pos < self.limit:
            match = num_re.match(self.pathd, self.pos)
            if match is None:
                return False
            kind = match.lastgroup
            if kind == 'SKIP':
                # move skipped elements forward.
                self.pos = match.end()
                continue
            return True
        return None

    def _number(self):
        while self.pos < self.limit:
            match = num_re.match(self.pathd, self.pos)
            if match is None:
                break  # No more matches.
            kind = match.lastgroup
            if kind == 'SKIP':
                continue
            self.pos = match.end()
            return float(match.group())
        return None

    def _flag(self):
        while self.pos < self.limit:
            match = flag_re.match(self.pathd, self.pos)
            if match is None:
                break  # No more matches.
            kind = match.lastgroup
            if kind == 'SKIP':
                continue
            self.pos = match.end()
            return bool(int(match.group()))
        return None

    def _string(self):
        while self.pos < self.limit:
            match = str_re.match(self.pathd, self.pos)
            if match is None:
                break  # No more matches.
            kind = match.lastgroup
            if kind == 'SKIP':
                continue
            self.pos = match.end()
            return str(match.group())
        return None

    def parse(self, pathd):
        if isinstance(pathd, (tuple, list)):
            pathd = " ".join(pathd)
        self.pathd = pathd
        self.pos = 0
        self.limit = len(pathd)
        while True:
            cmd = self._command()
            if cmd is None:
                return
            try:
                command = self.commands[cmd]
            except KeyError:
                return
            arguments = command.arguments
            while True:
                args = list()
                if arguments is None:
                    command.command()
                    if self._more():
                        raise ValueError
                    break
                if not isinstance(arguments, (tuple,list)):
                    arguments = tuple(arguments)
                for arg in arguments:
                    if arg is None:
                        break
                    if arg is float:
                        args.append(self._number())
                    elif arg is int:
                        args.append(int(self._number()))
                    elif arg is bool:
                        args.append(self._flag())
                    elif arg is str:
                        args.append(self._string())
                    else:
                        args.append(arg(self._string()))
                command.command(*args)
                if not self._more():
                    break
