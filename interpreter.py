import traceback
from collections import ChainMap, deque
from functools import reduce

from lex import lex
from utils import struct


Record = struct('statement', 'result')


class Stark:

    def __init__(self, hist_length=1000):
        self.state = ChainMap()
        self.stack = self.state.maps
        self.hist = deque(maxlen=hist_length)

        self.stack.append({
            name[6:]: getattr(self, name)
            for name in dir(self)
            if name.startswith('stark_')
        })

    def stark_eval(self, statement):
        name, *args = statement
        try:
            res = self.state[name](*args)
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
        self.stack.append({})

    def stark_pop(self):
        self.stack.pop()

    def stark_res(self, *args):
        index, = args
        return self.hist[-int(index)].result

    def stark_hist(self, *args):
        index, = args
        return self.hist[-int(index)].statement

    def stark_set(self, *args):
        name, *args = args
        self.state[name] = self.stark_eval(args)
        return None

    def stark_int(self, *args):
        i, = args
        return int(i)

    def stark_get(self, *args):
        name, = args
        return self.state[name]

    def stark_getall(self, *args):
        return tuple(self.state[a] for a in args)

    def stark_del(self, *args):
        name, = args
        return self.state.pop(name)

    def stark_delall(self, *args):
        # TODO: validate names first
        return tuple(self.state.pop(a) for a in args)

    def stark_say(self, *args):
        print(*args)
        return None

    def stark_show(self, *args):
        print(*[self.state[a] for a in args])
        return None

    def stark_while(self, *args):
        cond, code = args
        while self.stark_exec(cond):
            self.stark_exec(code)

    def stark_reduce(self, *args):
        func, *args = args
        values = [self.state[a] for a in args]
        return reduce(self.state[func], values)

    def stark_eq(self, *args):
        a, b = args
        return self.state[a] == self.state[b]

    def stark_ne(self, *args):
        a, b = args
        return self.state[a] != self.state[b]

    def stark_lt(self, *args):
        a, b = args
        # TODO: chain across arbitrarily many!! :D
        return self.state[a] < self.state[b]

    def stark_sum(self, *args):
        return sum(self.state[a] for a in args)

    def stark_any(self, *args):
        return any(self.state[a] for a in args)

    def stark_all(self, *args):
        return all(self.state[a] for a in args)

    def stark_python(self, *args):
        code, = args
        exec(code, globals())
        return None


if __name__ == '__main__':
    stark = Stark()
    code = """
        set x int 1
        set step int 1
        set end int 10
        while {ne x end} {
            show x
            set x sum x step
        }
        """
    stark.stark_exec(code)

    def ev(*args):
        stark.stark_eval(args)

    def ex(code):
        stark.stark_exec(code)
