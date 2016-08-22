"""Brace yourselves..."""
from pipe import pipe

ESCAPE = '\\'
QUOTE = '{'
UNQUOTE = '}'
SPACE = ' '
NEWLINE = '\n'
SEMICOLON = ';'
NOPE = '\t'

PIPE_CHAR = '|'
PIPE_TOKEN = object()

COMMENT_CHAR = '#'
COMMENT_TOKEN = object()


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
            statement.append(''.join(token))
            token.clear()

    def end_statement():
        end_token()

        # Remove comments
        try:
            comment_index = statement.index(COMMENT_TOKEN)
        except ValueError:
            pass
        else:
            del statement[comment_index:]

        if statement:
            # TODO: make `lex` into a class to avoid hacks like [:]
            statement[:] = pipe(statement, on=PIPE_TOKEN)
            program.append(tuple(statement))
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
                    'line {}, column{}: unexpected {!r}'
                    .format(line, col, char))

            elif char == SPACE:
                end_token()

            elif char == SEMICOLON or char == NEWLINE:
                end_statement()

            elif char == COMMENT_CHAR:
                end_token()
                statement.append(COMMENT_TOKEN)

            # TODO: don't limit to single char
            elif char == PIPE_CHAR:
                end_token()
                statement.append(PIPE_TOKEN)

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
