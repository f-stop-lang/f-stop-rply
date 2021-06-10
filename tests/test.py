from importlib import reload
import fstop

reload(fstop)

string = '''
NEW 'RGBA' (100, 100 COLOR 255) AS img
FLIP img
SOLAR img 128
SHOW img
CLOSE img
'''

if __name__ == '__main__':
    lexer  = fstop.generator.build()
    fstop.parser.env = {}
    parser = fstop.parser.build()
    tokens = lexer.lex(string)

    print(
        parser.parse(tokens)
    )