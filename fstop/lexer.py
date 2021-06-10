from rply import LexerGenerator

generator = LexerGenerator()

generator.add('STRING', r'''("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')''')
generator.add('INTEGER', r'[+-]?(\d+)')
generator.add('FLOAT', r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)')

generator.add('LEFT_PAREN', r'\(')
generator.add('RIGHT_PAREN', r'\)')

generator.add('OPEN', r'OPEN')
generator.add('AS', r'AS')
generator.add('SAVE', r'SAVE')
generator.add('CLOSE', r'CLOSE')
generator.add('SHOW', r'SHOW')

generator.add('NEW', r'NEW')
generator.add('WIDTH', r'WIDTH')
generator.add('HEIGHT', r'HEIGHT')
generator.add('COLOR', r'COLOR')
generator.add('ALPHA', r'ALPHA')

generator.add('INVERT', r'INVERT')
generator.add('SOLAR', r'SOLAR')
generator.add('MIRROR', r'MIRROR')
generator.add('FLIP', r'FLIP')

generator.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')
generator.add('NUMBER_TUPLE', r"\(\s*(([+-]?\s*\d+,\s*)+)?\s*[+-]?\s*\d+,?\s*\)")

generator.add('COMMA', r',')

generator.ignore(r'\s+')  # ignore all whitespace
generator.ignore(r'//.*') # single line comment
generator.ignore(r"/\*[.\n\r]*\*/") # multi-line comment