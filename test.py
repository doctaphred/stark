from interpreter import Stark


stark = Stark()


def ev(*args):
    return stark.cmd_eval(args)


def ex(code):
    return stark.cmd_exec(code)


def exf(path):
    with open(path) as f:
        return stark.cmd_exec(f.read())


exf('test.stark')
