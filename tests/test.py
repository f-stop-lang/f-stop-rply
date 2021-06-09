from importlib import reload
import fstop

reload(fstop)

string = (
    '''OPEN "./assets/test.png" AS img
    SAVE img "s.png"
    '''
)

if __name__ == '__main__':
    lexer  = fstop.lexerGen.build()
    fstop.parser.env = {}
    parser = fstop.parser.build()

    tokens = lexer.lex(string)
    print(
        parser.parse(tokens)
    )