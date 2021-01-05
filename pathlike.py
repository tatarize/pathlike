"""
Pathlike Parser parses command line arguments like svg paths.
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
    ('QSTR', r'`([^`]*)`'),
    ('DSTR', r'[^ ,\t\n\x09\x0A\x0C\x0D]+'),
    ('SKIP', PATTERN_COMMAWSP),
]
str_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in str_parse))

more_parse = [
    ('FLOAT', PATTERN_FLOAT),
    ('BTICK', r'`'),
    ('SKIP', PATTERN_COMMAWSP)
]
more_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in more_parse))


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
                self.pos = match.end()
                continue
            return match.group()
        return None

    def _more(self):
        while self.pos < self.limit:
            match = more_re.match(self.pathd, self.pos)
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
                self.pos = match.end()
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
                self.pos = match.end()
                continue
            self.pos = match.end()
            if kind == 'QSTR':
                return str(match.group())[1:-1]
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
