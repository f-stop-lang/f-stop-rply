from rply import LexerGenerator

generator = LexerGenerator()

generator.add('STRING', r'''(['"]).*?(?<!\\)\1''')
generator.add('INTEGER', r'[+-]?[1-9][0-9]*')
generator.add('FLOAT', r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)')

generator.add('LEFT_PAREN', r'\(')
generator.add('RIGHT_PAREN', r'\)')

generator.add('OPEN', r'OPEN')
generator.add('AS', r'AS')
generator.add('SAVE', r'SAVE')

generator.add('INVERT', r'INVERT')
generator.add('SOLAR', r'SOLAR')
generator.add('MIRROR', r'MIRROR')
generator.add('FLIP', r'FLIP')

generator.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')

generator.ignore(r'[ \t]+')
generator.ignore(r'//.*')
