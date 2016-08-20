"""Brace yourselves..."""

ESCAPE = '\\'
QUOTE = '{'
UNQUOTE = '}'
SPACE = ' '
NEWLINE = '\n'
SEMICOLON = ';'
NOPE = '\t'


def lex(code):

    program = []
    statement = []
    token = []
    escape = False
    quote_level = 0
    line = 1
    col = 0

    def end_token():
        if token:
            t = ''.join(token)
            statement.append(t)
            token.clear()

    def end_statement():
        end_token()
        if statement:
            s = tuple(statement)
            program.append(s)
            statement.clear()

    for char in code:

        if char == NEWLINE:
            line += 1
            col = 0
        else:
            col += 1

        if char in NOPE:
            raise SyntaxError(
                'line {}, col {}: {!r} <-- NOPE'
                .format(line, col, char))

        if escape:
            token.append(char)
            escape = False

        elif token == ESCAPE:
            escape = True

        elif quote_level:

            if quote_level and char == QUOTE:
                quote_level += 1
                token.append(char)

            elif quote_level and char == UNQUOTE:
                quote_level -= 1
                if quote_level:
                    # Only if we're still quoted
                    token.append(char)

            else:
                token.append(char)

        else:

            if char == QUOTE:
                quote_level += 1

            elif char == UNQUOTE:
                raise SyntaxError(
                    'line {}, column{}: unexpected {}'
                    .format(char))

            elif char == SPACE:
                end_token()

            elif char == SEMICOLON or char == NEWLINE:
                end_statement()

            else:
                token.append(char)

    end_statement()

    return program


if __name__ == '__main__':
    code = """
        set x 1
        while {lt x 10} {
            sysout x
            inc x 1
        }
        """

    print(code)
    print(lex(code))
