from typing import Optional

from PIL import ImageSequence, Image
from rply import ParserGenerator, Token

from .objects import ImageRepr

parser = ParserGenerator(
    [
        'INTEGER', 'FLOAT', 'STRING',
        'LEFT_PAREN', 'RIGHT_PAREN', 'LEFT_BR', 'RIGHT_BR',
        'OPEN', 'AS', 'SAVE', 'CLOSE', 'SHOW', 'BLEND', 'RESIZE', 'ROTATE', 'MASK', 'CONVERT', 'CLONE', 'PUTPIXEL',
        'NEW', 'WIDTH', 'HEIGHT', 'COLOR', 'ALPHA', 'PASTE', 'SIZE', 'MODE',
        'VARIABLE', 'COMMA', 'ON', 'ECHO', 'TO', 'SEQUENCE', 'APPEND', 'SEQ',
        'INVERT', 'SOLARIZE', 'MIRROR', 'FLIP',
    ],
    
    precedence = [],
)
parser.env = {}

def get_var(name: str, type_: str = 'var') -> Optional[ImageRepr]:
    obj = ImageRepr if type_ == 'var' else list
    if not isinstance(var := parser.env.get(name), obj):
        raise NameError("Undefined variable '%s'" % name)
    return var

# productions
# program statements

@parser.production("main : statements")
def program(p: list):
    return p[0]

@parser.production("statements : statements expr")
def statements(p: list):
    return p[0] + [p[1]]

@parser.production("statements : expr")
def expr(p: list):
    return [p[0]]

# object type productions

@parser.production('string : STRING')
@parser.production('string : MODE variable')
def string(p: list) -> str:
    if len(p) == 1:
        return p[0].getstr().strip("'").strip('"')
    else:
        img = get_var(p[1])
        return img.image.mode

@parser.production('number : INTEGER')
@parser.production('number : WIDTH variable')
@parser.production('number : HEIGHT variable')
def integer(p: list) -> int:
    if len(p) == 1:
        return int(p[0].getstr())
    else:
        img = get_var(p[1])
        return (
            img.image.width if p[0].gettokentype() == "WIDTH" else img.image.height
        )

@parser.production('float : FLOAT')
def float_num(p: list) -> float:
    return float(p[0].getstr())
    
@parser.production('variable : VARIABLE')
def variable(p: list) -> str:
    return p[0].getstr()

@parser.production('ntuple_start : LEFT_PAREN number COMMA')
def ntuple_start(p: list) -> tuple:
    return (p[1],)

@parser.production('ntuple_start : ntuple_start number COMMA')
def ntuple_body(p: list) -> tuple:
    return p[0] + (p[1],)

@parser.production('ntuple : ntuple_start RIGHT_PAREN')
@parser.production('ntuple : ntuple_start number RIGHT_PAREN')
@parser.production('ntuple : SIZE variable')
def ntuple(p: list) -> tuple:
    if isinstance(p[0], Token):
        img = get_var(p[1])
        return img.image.size
    else:
        return p[0] + (p[1],) if len(p) == 3 else p[0]

@parser.production('sequence_start : LEFT_BR variable COMMA')
def seq_start(p: list) -> list:
    return [p[0]]

@parser.production('sequence_start : sequence_start variable COMMA')
def seq_body(p: list) -> list:
    return p[0] + [p[1]]

@parser.production('sequence : sequence_start RIGHT_BR')
@parser.production('sequence : sequence_start number RIGHT_BR')
@parser.production('sequence : SEQUENCE variable')
def sequence(p: list) -> list:
    if isinstance(p[0], Token):
        img = get_var(p[1], 'seq')
        return list(ImageSequence.Iterator(img))
    else:
        return p[0] + [p[1]] if len(p) == 3 else p[0]

# operation productions

@parser.production('expr : APPEND variable TO variable')
def append_seq(p: list) -> None:
    img = get_var(p[1])
    seq = get_var(p[-1], 'seq')
    return seq.append(img)

@parser.production('expr : BLEND variable COMMA variable ALPHA float AS variable')
def blend(p: list) -> Image:
    backg, overlay, alpha, name = p[1], p[3], p[-3], p[-1]
    img1, img2 = get_var(backg), get_var(overlay)
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
        parser.env[p[-1]] = p[1]
    else:
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
def clone_statement(p: list) -> None:
    img = get_var(p[1])
    name = p[-1]
    image = img.image.copy()
    image = ImageRepr(image)
    parser.env[name] = image 
    return image

@parser.production('expr : CONVERT variable string')
def convert_statement(p: list) -> None:
    img = get_var(p[1])
    img.image = img.image.convert(p[-1])
    return None

@parser.production('expr : SAVE variable string')
def save_statement(p: list) -> str:
    img = get_var(p[1])
    img.image.save(p[-1])
    return p[-1]

@parser.production('expr : CLOSE variable')
def close_statement(p: list) -> None:
    img = get_var(p[1])
    img.image.close()
    return None

@parser.production('expr : RESIZE variable ntuple')
def resize_statement(p: list) -> None:
    img = get_var(p[1])
    img.image = img.image.resize(p[-1])
    return None

@parser.production('expr : ROTATE variable number')
def rotate_statement(p: list) -> None:
    img = get_var(p[1])
    img.image = img.image.rotate(p[-1])
    return None

@parser.production('expr : PASTE variable ON variable')
@parser.production('expr : PASTE variable ON variable ntuple')
@parser.production('expr : PASTE variable ON variable MASK variable ntuple')
def paste_statement(p: list) -> None:
    image, snippet = p[1], p[3]
    img1, img2 = get_var(image), get_var(snippet)
    xy = (0, 0) if len(p) == 4 else p[-1]
    mask = p[-2] if len(p) == 7 else None
    img2.image.paste(img1.image, xy, mask=mask)
    return None

@parser.production('expr : PUTPIXEL variable ntuple COLOR ntuple')
@parser.production('expr : PUTPIXEL variable ntuple COLOR number')
def putpixel(p: list) -> None:
    coords, color = p[-3], p[-1]
    img = get_var(p[1])
    img.image.putpixel(coords, color)
    return None
 
@parser.production('expr : SHOW variable')
@parser.production('expr : SHOW variable string')
def show_statement(p: list) -> None:
    img = get_var(p[1])
    title = p[-1] if len(p) == 3 else None
    img.image.show(title=title)
    return None

@parser.production('expr : ECHO expr')
def echo(p: list) -> None:
    return print(p[-1])