from importlib import reload
import fstop

reload(fstop)

with open('./test.ft', 'r') as string:
    string = string.read()
print(string)
if __name__ == '__main__':
    lexer  = fstop.generator.build()
    fstop.parser.env = {}
    parser = fstop.parser.build()

    tokens = lexer.lex(string)
    for i in tokens:
        print(i)
    print(
        parser.parse(tokens)
    )
