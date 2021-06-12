from typing import Optional

from PIL import ImageSequence, Image
from rply import ParserGenerator, Token

from .objects import ImageRepr

parser = ParserGenerator(
    [
        'INTEGER', 'FLOAT', 'STRING', 'NUMBER_TUPLE',
        'LEFT_PAREN', 'RIGHT_PAREN', 
        'OPEN', 'AS', 'SAVE', 'CLOSE', 'SHOW', 'BLEND', 'RESIZE', 'ROTATE', 'MASK', 'CONVERT', 'CLONE', 'PUTPIXEL',
        'NEW', 'WIDTH', 'HEIGHT', 'COLOR', 'ALPHA', 'PASTE', 'SIZE', 'MODE',
        'VARIABLE', 'COMMA', 'ON', 'ECHO', 'TO', 'SEQUENCE', 'APPEND', 'SEQ',
        'INVERT', 'SOLARIZE', 'MIRROR', 'FLIP',
    ],
    
    precedence = [
        ('left', ['OPEN', 'SAVE', 'AS']),
        ('left', ['INVERT'])
    ],
)
parser.sq_env = {}
parser.env = {}

@parser.production("main : statements")
def program(p: list):
    return p[0]

@parser.production("statements : statements expr")
def statements(p: list):
    return p[0] + [p[1]]

@parser.production("statements : expr")
def expr(p: list):
    return [p[0]]

@parser.production('string : STRING')
@parser.production('string : MODE variable')
def string(p: list) -> str:
    if len(p) == 1:
        return p[0].getstr().strip("'").strip('"')
    else:
        if not (img := parser.env.get(p[-1])):
            raise NameError("Undefined image '%s'" % p[-1])
        else:
            return img.image.mode

@parser.production('number : INTEGER')
@parser.production('number : WIDTH variable')
@parser.production('number : HEIGHT variable')
def integer(p: list) -> int:
    if len(p) == 1:
        return int(p[0].getstr())
    else:
        if not (img := parser.env.get(p[-1])):
            raise NameError("Undefined image '%s'" % p[-1])
        else:
            return (
                img.image.width if p[0].gettokentype() == "WIDTH" else img.image.height
            )

@parser.production('float : FLOAT')
def float_(p: list) -> float:
    return float(p[0].getstr())
    
@parser.production('variable : VARIABLE')
def variable_name(p: list) -> str:
    return p[0].getstr()

@parser.production('ntuple : LEFT_PAREN number COMMA number RIGHT_PAREN')
@parser.production('ntuple : LEFT_PAREN number COMMA number COMMA number RIGHT_PAREN')
@parser.production('ntuple : LEFT_PAREN number COMMA number COMMA number COMMA number RIGHT_PAREN')
@parser.production('ntuple : SIZE variable')
def num_tuple(p: list) -> tuple:
    if len(p) == 2:
        if not (img := parser.env.get(p[-1])):
            raise NameError("Undefined image '%s'" % p[-1])
        else:
            return img.image.size
    else:
        return tuple(x for x in p if not isinstance(x, Token))

@parser.production('sequence : SEQ')
@parser.production('sequence : SEQUENCE variable')
def sequence(p: list) -> list:
    if len(p) == 1:
        try:
            seq =  [
                parser.env[f] for f in p[0].getstr()[1:-1].split(',') if f
            ]
        except KeyError as k:
            raise NameError("Undefined image '%s'" % k)
        return seq
    else:
        if not (img := parser.env.get(p[-1])):
            raise NameError("Undefined image '%s'" % p[-1])
        else:
            return list(ImageSequence.Iterator(img))

@parser.production('expr : APPEND variable TO variable')
def append_seq(p: list) -> None:

    if not (seq := parser.sq_env.get(p[-1])):
        raise NameError("Undefined sequence '%s'" % p[-1])
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])

    seq.append(img)
    return None

@parser.production('expr : BLEND variable COMMA variable ALPHA float AS variable')
def blend(p: list) -> Image:
    backg, overlay, alpha, name = p[1], p[3], p[-3], p[-1]

    if not (img1 := parser.env.get(backg)):
        raise NameError("Undefined image '%s'" % backg)
    if not (img2 := parser.env.get(overlay)):
        raise NameError("Undefined image '%s'" % overlay)

    image = Image.blend(img1.image, img2.image, alpha=alpha)
    image = ImageRepr(image)
    parser.env[name] = image
    return image

@parser.production('expr : NEW sequence AS variable')
@parser.production('expr : NEW string ntuple AS variable')
@parser.production('expr : NEW string ntuple COLOR ntuple AS variable')
@parser.production('expr : NEW string ntuple COLOR number AS variable')
def new_statement(p: list) -> Optional[Image.Image]:
    if len(p) == 4:
        parser.sq_env[p[-1]] = p[1]

    mode, size, name = p[1], p[2], p[-1]
    color = p[4] if len(p) == 7 else 0
    image = Image.new(mode, size, color)
    image = ImageRepr(image)
    parser.env[name] = image
    return image

@parser.production('expr : OPEN string AS variable')
def open_statement(p: list) -> Image:
    filename, name = p[1], p[-1]
    image = Image.open(filename)
    image = ImageRepr(image)
    parser.env[name] = image
    return image

@parser.production('expr : CLONE variable AS variable')
def clone_statement(p: list) -> Image:
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        name = p[-1]
        image = img.image.copy()
        image = ImageRepr(image)
        parser.env[name] = image 
        return image

@parser.production('expr : CONVERT variable string')
def convert_statement(p: list) -> Image:
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        img.image = img.image.convert(p[-1])
    return None

@parser.production('expr : SAVE variable string')
def save_statement(p: list) -> str:
    if not (img := parser.env.get(p[-2])):
        raise NameError("Undefined image '%s'" % p[-2])
    else:
        img.image.save(p[-1])
    return p[-1]

@parser.production('expr : CLOSE variable')
def close_statement(p: list) -> None:
    if not (img := parser.env.get(p[-1])):
        raise NameError("Undefined image '%s'" % p[-1])
    else:
        img.image.close()
    return None

@parser.production('expr : RESIZE variable ntuple')
def resize_statement(p: list) -> None:
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        img.image = img.image.resize(p[-1])
    return None

@parser.production('expr : ROTATE variable number')
def rotate_statement(p: list) -> None:
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        img.image = img.image.rotate(p[-1])
    return None

@parser.production('expr : PASTE variable ON variable')
@parser.production('expr : PASTE variable ON variable ntuple')
@parser.production('expr : PASTE variable ON variable MASK variable ntuple')
def paste_statement(p: list) -> None:
    image, snippet = p[1], p[3]

    if not (img1 := parser.env.get(image)):
        raise NameError("Undefined image '%s'" % image)
    if not (img2 := parser.env.get(snippet)):
        raise NameError("Undefined image '%s'" % snippet)

    xy = (0, 0) if len(p) == 4 else p[-1]
    mask = p[-2] if len(p) == 7 else None
    img2.image.paste(img1.image, xy, mask=mask)
    return None

@parser.production('expr : PUTPIXEL variable ntuple COLOR ntuple')
@parser.production('expr : PUTPIXEL variable ntuple COLOR number')
def putpixel(p: list) -> None:
    coords, color = p[-3], p[-1]
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        img.image.putpixel(coords, color)
    return None

@parser.production('expr : SHOW variable')
@parser.production('expr : SHOW variable string')
def show_statement(p: list) -> None:
    if not (img := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        title = p[-1] if len(p) == 3 else None
        img.image.show(title=title)
    return None

@parser.production('expr : ECHO string')
@parser.production('expr : ECHO number')
@parser.production('expr : ECHO float')
@parser.production('expr : ECHO variable')
@parser.production('expr : ECHO ntuple')
def echo(p: list) -> None:
    print(p[-1])
    return None