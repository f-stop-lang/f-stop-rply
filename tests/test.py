from importlib import reload
import fstop

reload(fstop)

string = '''OPEN "../test.png" AS img//lol sus
'''

if __name__ == '__main__':
    lexer  = fstop.generator.build()
    fstop.parser.env = {}
    parser = fstop.parser.build()

    tokens = lexer.lex(string)
    print(
        parser.parse(tokens)
    )
