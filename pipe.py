def pipe(statement, on):
    """

    (forward, backward) for 'abc>def':
    a: a, <empty>
    b: ab, <empty>
    c: abc, <empty>
    >: <empty>, cba
    d: d, cba
    e: de, cba
    f: def, cba
    => defabc, <empty>

    >>> pipe(['list', 'a', 'b', 'c', '>', 'set', 'x'], on='>')
    ['set', 'x', 'list', 'a', 'b', 'c']

    >>> def ppipe(s):
    ...     print(''.join(pipe(s, '>')))

    >>> ppipe('abc')
    abc
    >>> ppipe('abc>def')
    defabc
    >>> ppipe('abc>def>ghi')
    ghidefabc

    >>> ppipe('abc>>def')
    defabc
    >>> ppipe('abc>>>>>>>>>>def')
    defabc

    >>> ppipe('abc>')
    abc
    >>> ppipe('>abc')
    abc
    >>> ppipe('>abc>def>ghi>')
    ghidefabc

    >>> ppipe('a>b>c>d>e>f')
    fedcba
    >>> ppipe('>a>b>c>d>e>f>')
    fedcba
    """
    forward = []
    backward = []

    def flip():
        while forward:
            backward.append(forward.pop())

    def unflip():
        while backward:
            forward.append(backward.pop())

    for token in statement:
        if token == on:
            flip()
        else:
            forward.append(token)

    unflip()
    return forward
