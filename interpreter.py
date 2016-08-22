import traceback
from collections import deque
from functools import reduce

import pp

from lex import lex
from stack import Stack
from utils import struct


# TODO: capture stdin, stdout, stderr
Record = struct('cmd', 'args', 'result')


class Stark:

    def __init__(self, hist_length=1000):
        self.hist = deque(maxlen=hist_length)
        self.stack = Stack({
            name[4:].replace('_', '-'): getattr(self, name)
            for name in dir(self)
            if name.startswith('cmd_')
        })

    def cmd_record(self, *args, **kwargs):
        self.hist.append(Record(*args, **kwargs))

    def cmd_lex(self, code):
        return lex(code)

    def cmd_parse(self, statement):
        try:
            values = []
            for token in statement:
                if token.startswith(':'):
                    values.append(self[token[1:]])
                else:
                    values.append(token)
            cmd, *args = values
            return cmd, args
        except Exception:
            print('Error parsing statement:')
            pp(statement)
            raise

    def cmd_eval(self, cmd, args):
        try:
            result = self.stack[cmd](*args)
        except Exception as ex:
            print('{}: {}'.format(ex.__class__.__name__, ex))
            print('  command:', repr(cmd))
            print('  args:', repr(args))
            raise
        self.cmd_record(cmd, args, result)
        return result

    def cmd_exec(self, code, trace=False, echo=False):
        program = self.cmd_lex(code)
        if not program:
            return None
        for statement in program:
            if trace:
                print('>', repr(statement))
            cmd, args = self.cmd_parse(statement)
            result = self.cmd_eval(cmd, args)
        self.cmd_record(cmd, args, result)
        if echo:
            print('=>', result)
        return result

    def cmd_push(self, frame=None):
        self.stack.push(frame)

    def cmd_pop(self):
        return self.stack.pop()

    def cmd_stark_get(self, name):
        return getattr(self, name)

    def cmd_stark_set(self, name, value):
        prev = getattr(self, name, None)
        setattr(self, name, value)
        return prev

    def cmd_stark_del(self, name):
        prev = getattr(self, name, None)
        delattr(self, name)
        return prev

    def cmd_hist(self, index=1):
        return self.hist[-int(index)]

    def cmd_result(self, index=1):
        return self.cmd_hist(index).result

    def cmd_cmd(self, index=1):
        return self.cmd_hist(index).cmd

    def cmd_args(self, index=1):
        return self.cmd_hist(index).args

    # def cmd_set(self, name, *statement):
    #     cmd, args = self.cmd_parse(statement)
    #     self.stack[name] = self.cmd_eval(cmd, args)
    #     return None

    # def cmd_set(self, name, cmd_name, *args):
    #     prev = self.stack.get(name, None)
    #     # TODO: this seems strange
    #     cmd = self[cmd_name]
    #     self.stack[name] = cmd(*args)
    #     return prev

    def cmd_alias(self, newname, name):
        self.stack[newname] = self.stack[name]

    def cmd_do(self, code):
        # TODO: allow args
        return lambda: self.cmd_exec(code)

    def cmd_def(self, name, code):
        self.stack[name] = self.cmd_do(code)

    def cmd_ignore(self, *args):
        pass

    def cmd_lit(self, arg):
        return arg

    def cmd_list(self, *args):
        return args

    def cmd_first(self, *args):
        first, *rest = args
        return first

    def cmd_last(self, *args):
        *rest, last = args
        return last

    def cmd_str(self, arg):
        return str(arg)

    def cmd_repr(self, arg):
        return repr(arg)

    def cmd_int(self, i):
        return int(i)

    def cmd_get(self, name):
        return self.stack[name]

    __getitem__ = cmd_get

    def cmd_getall(self, *args):
        return tuple(self[a] for a in args)

    def cmd_del(self, name):
        return self.stack.top.pop(name)

    def cmd_delall(self, *names):
        # TODO: validate names first
        return tuple(self.stack.pop(name) for name in names)

    def cmd_say(self, *strings):
        print(*strings)
        return None

    def cmd_show(self, *names):
        self.cmd_say(*self.cmd_getall(*names))
        return None

    def cmd_while(self, cond, code):
        result = None  # TODO: handle "code never exec'd" better
        while self.cmd_exec(cond):
            result = self.cmd_exec(code)
        return result

    def cmd_reduce(self, func, *args):
        return reduce(self[func], self.cmd_getall(*args))


    def cmd_is(self, *args):
        # TODO: decide whether commands like these should auto-lookup
        # names or accept values directly. Or add an "in-place eval"
        # syntax.
        a, b = args
        return self[a] is self[b]

    def cmd_eq(self, *args):
        a, b = args
        return self[a] == self[b]

    def cmd_ne(self, *args):
        a, b = args
        return self[a] != self[b]

    def cmd_lt(self, *args):
        a, b = args
        # TODO: chain across arbitrarily many!! :D
        return self[a] < self[b]

    def cmd_sum(self, *names):
        return sum(self.cmd_getall(*names))

    def cmd_any(self, *names):
        return any(self.cmd_getall(*names))

    def cmd_all(self, *names):
        return all(self.cmd_getall(*names))

    def cmd_pyexec(self, code):
        exec(code, globals())

    def cmd_pyeval(self, statement):
        return eval(statement)

    def cmd_pyset(self, name, value):
        globals()[name] = value

    def cmd_pyget(self, name):
        return globals()[name]

    def cmd_builtin(self, name):
        return getattr(__builtins__, name)

    def cmd_call(self, name, *args):
        return self.cmd_builtin(name)(*args)

    def cmd_expect(self, expected):
        actual = pp.fmt(self.cmd_result())
        # expected = repr(' '.join(parts))
        if actual != expected:
            raise RuntimeError('Expected {!r}, got {!r}'.format(
                expected, actual))

    def cmd_with(self, setup, code):
        self.cmd_push()
        self.cmd_exec(setup)
        result = self.cmd_exec(code)
        self.cmd_pop()
        return result

    def cmd_using(self, frame, code):
        self.cmd_push(frame)
        result = self.cmd_exec(code)
        self.cmd_pop()
        return result

    def cmd_frame(self, code):
        self.cmd_push()
        self.cmd_exec(code)
        return self.cmd_pop()
