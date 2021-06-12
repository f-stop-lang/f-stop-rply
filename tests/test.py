from importlib import reload
import fstop

reload(fstop)

with open("test.ft") as ft:
    string = ft.read()

if __name__ == '__main__':
    lexer  = fstop.generator.build()
    fstop.parser.env = {}
    fstop.parser.sq_env = {}
    parser = fstop.parser.build()
    tokens = lexer.lex(string)

    print(
        parser.parse(tokens)
    )