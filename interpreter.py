import traceback
from collections import deque
from functools import reduce

from lex import lex
from stack import Stack
from utils import struct


# TODO: capture stdin, stdout, stderr
Record = struct('statement', 'result')


class Stark:

    def __init__(self, hist_length=1000):
        self.hist = deque(maxlen=hist_length)
        self.stack = Stack({
            name[4:]: getattr(self, name)
            for name in dir(self)
            if name.startswith('cmd_')
        })

    def cmd_eval(self, statement):
        name, *args = statement
        try:
            result = self.stack[name](*args)
        except Exception as ex:
            traceback.print_exc()
            result = ex
        self.hist.append(Record(statement, result))
        return result

    def cmd_exec(self, code):
        program = lex(code)
        # TODO: handle empty program better (return sentinel value?
        # don't update self.result?)
        assert program
        for statement in program:
            result = self.cmd_eval(statement)
        return result

    def cmd_push(self):
        self.stack.push()

    def cmd_pop(self):
        return self.stack.pop()

    def cmd_result(self, *args):
        index, = args
        return self.hist[-int(index)].result

    def cmd_hist(self, *args):
        index, = args
        return self.hist[-int(index)].statement

    def cmd_set(self, *args):
        name, *args = args
        self.stack[name] = self.cmd_eval(args)
        return None

    def cmd_int(self, *args):
        i, = args
        return int(i)

    def cmd_get(self, *args):
        name, = args
        return self.stack[name]

    def cmd_getall(self, *args):
        return tuple(self.stack[a] for a in args)

    def cmd_del(self, *args):
        name, = args
        return self.stack.pop(name)

    def cmd_delall(self, *args):
        # TODO: validate names first
        return tuple(self.stack.pop(a) for a in args)

    def cmd_say(self, *args):
        print(*args)
        return None

    def cmd_show(self, *args):
        print(*[self.stack[a] for a in args])
        return None

    def cmd_while(self, *args):
        cond, code = args
        while self.cmd_exec(cond):
            self.cmd_exec(code)

    def cmd_reduce(self, *args):
        func, *args = args
        values = [self.stack[a] for a in args]
        return reduce(self.stack[func], values)

    def cmd_eq(self, *args):
        a, b = args
        return self.stack[a] == self.stack[b]

    def cmd_ne(self, *args):
        a, b = args
        return self.stack[a] != self.stack[b]

    def cmd_lt(self, *args):
        a, b = args
        # TODO: chain across arbitrarily many!! :D
        return self.stack[a] < self.stack[b]

    def cmd_sum(self, *args):
        return sum(self.stack[a] for a in args)

    def cmd_any(self, *args):
        return any(self.stack[a] for a in args)

    def cmd_all(self, *args):
        return all(self.stack[a] for a in args)

    def cmd_python(self, *args):
        code, = args
        exec(code, globals())
        return None


if __name__ == '__main__':
    stark = Stark()

    def ev(*args):
        stark.cmd_eval(args)

    def ex(code):
        stark.cmd_exec(code)

    def exf(path):
        with open(path) as f:
            stark.cmd_exec(f.read())

    exf('test.stark')
