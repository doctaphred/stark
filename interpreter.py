import traceback
from collections import deque
from functools import reduce

from lex import lex
from stack import Stack
from utils import struct


Record = struct('statement', 'result')


class Stark:

    def __init__(self, hist_length=1000):
        self.hist = deque(maxlen=hist_length)
        self.stack = Stack({
            name[6:]: getattr(self, name)
            for name in dir(self)
            if name.startswith('stark_')
        })

    def stark_eval(self, statement):
        name, *args = statement
        try:
            res = self.stack[name](*args)
        except Exception as ex:
            traceback.print_exc()
            res = ex
        self.hist.append(Record(statement, res))
        return res

    def stark_exec(self, code):
        program = lex(code)
        # TODO: handle empty program better (return sentinel value?
        # don't update self.res?)
        assert program
        for statement in program:
            res = self.stark_eval(statement)
        return res

    def stark_push(self):
        self.stack.push()

    def stark_pop(self):
        return self.stack.pop()

    def stark_res(self, *args):
        index, = args
        return self.hist[-int(index)].result

    def stark_hist(self, *args):
        index, = args
        return self.hist[-int(index)].statement

    def stark_set(self, *args):
        name, *args = args
        self.stack[name] = self.stark_eval(args)
        return None

    def stark_int(self, *args):
        i, = args
        return int(i)

    def stark_get(self, *args):
        name, = args
        return self.stack[name]

    def stark_getall(self, *args):
        return tuple(self.stack[a] for a in args)

    def stark_del(self, *args):
        name, = args
        return self.stack.pop(name)

    def stark_delall(self, *args):
        # TODO: validate names first
        return tuple(self.stack.pop(a) for a in args)

    def stark_say(self, *args):
        print(*args)
        return None

    def stark_show(self, *args):
        print(*[self.stack[a] for a in args])
        return None

    def stark_while(self, *args):
        cond, code = args
        while self.stark_exec(cond):
            self.stark_exec(code)

    def stark_reduce(self, *args):
        func, *args = args
        values = [self.stack[a] for a in args]
        return reduce(self.stack[func], values)

    def stark_eq(self, *args):
        a, b = args
        return self.stack[a] == self.stack[b]

    def stark_ne(self, *args):
        a, b = args
        return self.stack[a] != self.stack[b]

    def stark_lt(self, *args):
        a, b = args
        # TODO: chain across arbitrarily many!! :D
        return self.stack[a] < self.stack[b]

    def stark_sum(self, *args):
        return sum(self.stack[a] for a in args)

    def stark_any(self, *args):
        return any(self.stack[a] for a in args)

    def stark_all(self, *args):
        return all(self.stack[a] for a in args)

    def stark_python(self, *args):
        code, = args
        exec(code, globals())
        return None


if __name__ == '__main__':
    stark = Stark()

    def ev(*args):
        stark.stark_eval(args)

    def ex(code):
        stark.stark_exec(code)

    def exf(path):
        with open(path) as f:
            stark.stark_exec(f.read())

    exf('test.stark')
