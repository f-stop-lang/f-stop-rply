from rply import LexerGenerator

generator = LexerGenerator()

generator.ignore(r'\s+')  # ignore all whitespace
generator.ignore(r'//.*') # single line comment
generator.ignore(r"/\*([\n\r]|.)*\*/") # multi-line comment

generator.add('STRING', r'''("[^"\\]*(\\.[^"\\]*)*"|'[^'\\]*(\\.[^'\\]*)*')''')
generator.add('FLOAT', r'[+-]?(((([1-9][0-9]*)|0))?\.[0-9]+)|((([1-9][0-9]*)|0)\.[0-9]*)')
generator.add('INTEGER', r'[+-]?([1-9][0-9]*|0)')

generator.add('TO', r'TO')
generator.add('ON', r'ON')

generator.add('ECHO', r'ECHO')
generator.add('APPEND', r'APPEND')

generator.add('OPEN', r'OPEN')
generator.add('AS', r'AS')
generator.add('SAVE', r'SAVE')
generator.add('CLOSE', r'CLOSE')
generator.add('SHOW', r'SHOW')

generator.add('RESIZE', r'RESIZE')
generator.add('ROTATE', r'ROTATE')
generator.add('BLEND', r'BLEND')
generator.add('PASTE', r'PASTE')
generator.add('MASK', r'MASK')

generator.add('CLONE', r'CLONE')
generator.add('CONVERT', r'CONVERT')
generator.add('PUTPIXEL', r'PUTPIXEL')
generator.add('SEQUENCE', r'SEQUENCE')

generator.add('NEW', r'NEW')
generator.add('WIDTH', r'WIDTH')
generator.add('HEIGHT', r'HEIGHT')
generator.add('COLOR', r'COLOR')
generator.add('ALPHA', r'ALPHA')
generator.add('SIZE', r'SIZE')
generator.add('MODE', r'MODE')
generator.add('CROP', r'CROP')

generator.add('INVERT', r'INVERT')
generator.add('SOLARIZE', r'SOLARIZE')
generator.add('MIRROR', r'MIRROR')
generator.add('FLIP', r'FLIP')
generator.add('GRAYSCALE', r'GRAYSCALE')
generator.add('POSTERIZE', r'POSTERIZE')
generator.add('MIRROR', r'MIRROR')

generator.add('EMBOSS', r'EMBOSS')
generator.add('SMOOTH', r'SMOOTH')
generator.add('SHARPEN', r'SHARPEN')
generator.add('DETAIL', r'DETAIL')
generator.add('CONTOUR', r'CONTOUR')
generator.add('EDGE_ENHANCE', r'EDGE_ENHANCE')
generator.add('BLUR', r'BLUR')
generator.add('MAX_FILTER', r'MAX_FILTER')
generator.add('MIN_FILTER', r'MIN_FILTER')
generator.add('MODE_FILTER', r'MODE_FILTER')
generator.add('MEDIAN_FILTER', r'MEDIAN_FILTER')

generator.add('TEXT', r'TEXT')
generator.add('FONT', r'FONT')
generator.add('LINE', r'LINE')
generator.add('ELLIPSE', r'ELLIPSE')
generator.add('DOT', r'DOT')

generator.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')

generator.add('COMMA', r',')
generator.add('LEFT_PAREN', r'\(')
generator.add('RIGHT_PAREN', r'\)')
generator.add('LEFT_BR', r'\[')
generator.add('RIGHT_BR', r'\]')

generator.add('ADD', r'\+')
generator.add('SUB', r'-')
generator.add('MUL', r'\*')
generator.add('DIV', r'/')
generator.add('EXP', r'\^')
generator.add('FLOOR_DIV', r'~/')