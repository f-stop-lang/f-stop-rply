from rply import LexerGenerator

lexerGen = LexerGenerator()

lexerGen.add('STRING', r'''("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')''')
lexerGen.add('NUMBER', r'\d+')

lexerGen.add('LEFT_PAREN', r'\(')
lexerGen.add('RIGHT_PAREN', r'\)')

lexerGen.add('OPEN', r'OPEN')
lexerGen.add('AS', r'AS')
lexerGen.add('SAVE', r'SAVE')

lexerGen.add('NEWLINE', r'\n+')

lexerGen.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')

lexerGen.ignore(r'[^\n\S]+')
lexerGen.ignore(r'//.*')