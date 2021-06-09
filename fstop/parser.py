
from rply import ParserGenerator

from .objects import Image

parser = ParserGenerator(
    [
        'INTEGER', 'STRING', 
        'LEFT_PAREN', 'RIGHT_PAREN', 
        'OPEN', 'AS', 'SAVE',
        'VARIABLE',
        'INVERT', 'SOLAR', 'MIRROR', 'FLIP',
    ],
    
    precedence = [
        ('left', ['OPEN', 'SAVE', 'AS']),
        ('left', ['INVERT'])
    ],
)

@parser.production("main : statements")
def expr(p: list):
    return p[0]

@parser.production("statements : statements expr")
def expr(p: list):
    return p[0] + [p[1]]

@parser.production("statements : expr")
def expr(p: list):
    return [p[0]]

@parser.production('string : STRING')
def string(p: list) -> str:
    return p[0].getstr()[1:-1]

@parser.production('number : INTEGER')
def number(p: list) -> str:
    return int(p[0].getstr())
    
@parser.production('variable : VARIABLE')
def variable_name(p: list) -> str:
    return p[0].getstr()

@parser.production('expr : OPEN string AS variable')
def open_statement(p: list) -> Image:
    left, right = p[1], p[-1]
    image = Image(left, right)
    parser.env[right] = image
    return image

@parser.production('expr : SAVE variable string')
def save_statement(p: list) -> None:
    if not (img := parser.env.get(p[-2])):
        raise NameError("Undefined image '%s'" % p[-2])
    else:
        img.image.save(p[-1])
    return None