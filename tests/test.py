from importlib import reload
import fstop

reload(fstop)

string = '''
OPEN "./assets/test.png" AS img
FLIP img
SOLAR img 128
SAVE img "x.png"
'''

if __name__ == '__main__':
    lexer  = fstop.generator.build()
    fstop.parser.env = {}
    parser = fstop.parser.build()
    tokens = lexer.lex(string)

    print(
        parser.parse(tokens)
    )