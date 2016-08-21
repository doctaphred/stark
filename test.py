from interpreter import Stark


stark = Stark()


def x(code, trace=True, echo=True):
    return stark.cmd_exec(code, trace, echo)


def exf(path, trace=True, echo=True):
    with open(path) as f:
        return stark.cmd_exec(f.read(), trace, echo)


if __name__ == '__main__':
    import sys
    exf(sys.argv[1])
