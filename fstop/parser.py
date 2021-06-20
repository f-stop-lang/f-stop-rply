from typing import Optional, Union, Any
from io import BytesIO

import requests
from PIL import ImageSequence, Image
from rply import ParserGenerator, Token

from .lexer import generator
from .objects import ImageRepr

parser = ParserGenerator(
    [
        l.name for l in generator.rules
    ],
    
    precedence = [
        ('left', ['ADD', 'SUB']),
        ('left', ['MUL', 'DIV', 'FLOOR_DIV']),
        ('left', ['EXP']),
    ],
)
parser.env = {}
parser._stream_env = []
parser._saved_streams = []

def get_var(name: str, type_: type = ImageRepr) -> Optional[ImageRepr]:
    if not isinstance(var := parser.env.get(name), type_):
        raise NameError("Undefined variable '%s'" % name)
    return var

# productions
# program statements

@parser.production("main : statements")
def program(p: list) -> list:
    return p[0]

@parser.production("statements : statements expr")
def statements(p: list) -> list:
    return p[0] + [p[1]]

@parser.production("statements : expr")
def expr(p: list) -> list:
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
@parser.production('number : FLOAT')
@parser.production('number : WIDTH variable')
@parser.production('number : HEIGHT variable')
@parser.production('number : LENGTH variable')
@parser.production('number : LENGTH sequence')
@parser.production('number : TELL variable')
def number(p: list) -> float:
    token = p[0].gettokentype()
    if len(p) == 1:
        string = p[0].getstr()
        return (
            float(string) if token == "FLOAT" else int(string)
        )
    elif len(p) == 2 and token == "LENGTH":
        if isinstance(p[1], list):
            return len(p[1])
        else:
            img = get_var(p[1], (ImageRepr, list))
            return (
                len(img) if isinstance(img, list) else getattr(img, 'n_frames', 1)
            )
    else:
        img = get_var(p[1])
        return (
            img.image.width if token == "WIDTH" else 
            img.image.height if token == "HEIGHT" else 
            img.image.tell() if token == "TELL" else 0
        )

@parser.production('number : number ADD number')
@parser.production('number : number SUB number')
@parser.production('number : number MUL number')
@parser.production('number : number DIV number')
@parser.production('number : number EXP number')
@parser.production('number : number FLOOR_DIV number')
def numerical_operations(p: list) -> float:
    x, y = p[0], p[2]
    token = p[1].gettokentype()

    if token == "ADD":
        return x + y
    elif token == "SUB":
        return x - y
    elif token == "MUL":
        return x * y
    elif token == "DIV":
        return x / y
    elif token == "EXP":
        return x ** y
    else:
        return x // y
    
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

@parser.production('sequence_start : LEFT_BR')
def seq_start(_: list) -> list:
    return []

@parser.production('sequence_start : sequence_start variable COMMA')
def seq_body(p: list) -> list:
    return p[0] + [p[1]]

@parser.production('sequence : sequence_start RIGHT_BR')
@parser.production('sequence : sequence_start variable RIGHT_BR')
@parser.production('sequence : SEQUENCE variable')
def sequence(p: list) -> list:
    if isinstance(p[0], Token):
        img = get_var(p[1])
        return list(ImageSequence.Iterator(img))
    else:
        seq = p[0] + [p[1]] if len(p) == 3 else p[0]
        return [getattr(get_var(i), 'image', None) for i in seq]

@parser.production('color : COLOR ntuple')
@parser.production('color : COLOR number')
def color_st(p: list) -> Union[tuple, int]:
    return p[-1]

@parser.production('ntuple : ntuple ADD ntuple')
def tuple_concat(p: list) -> tuple:
    return p[0] + p[-1]

@parser.production('sequence : sequence ADD sequence')
def seq_concat(p: list) -> list:
    return p[0] + p[-1]

# operation productions

@parser.production('expr : APPEND variable TO variable')
def append_seq(p: list) -> None:
    img = get_var(p[1])
    seq = get_var(p[-1], list)
    return seq.append(img.image)

@parser.production('expr : BLEND variable COMMA variable ALPHA number AS variable')
def blend(p: list) -> Image:
    backg, overlay, alpha, name = p[1], p[3], p[-3], p[-1]
    img1, img2 = get_var(backg), get_var(overlay)
    image = Image.blend(img1.image, img2.image, alpha=alpha)
    image = ImageRepr(image)
    parser.env[name] = image
    return image

@parser.production('expr : NEW sequence AS variable')
@parser.production('expr : NEW string ntuple AS variable')
@parser.production('expr : NEW string ntuple color AS variable')
def new_statement(p: list) -> Optional[ImageRepr]:

    if len(p) == 4:
        parser.env[p[-1]] = p[1]
    else:
        mode, size, name = p[1], p[2], p[-1]
        color = p[3] if len(p) == 6 else 0
        image = Image.new(mode, size, color)
        image = ImageRepr(image)
        parser.env[name] = image
        return image

@parser.production('expr : MERGE string sequence AS variable')
def merge_statement(p: list) -> Optional[ImageRepr]:
    mode, bands, name = p[1], p[2], p[4]
    image = Image.merge(mode, tuple(bands))
    image = ImageRepr(image)
    parser.env[name] = image
    return image

@parser.production('expr : OPEN string AS variable')
@parser.production('expr : OPEN STREAM number AS variable')
@parser.production('expr : OPEN URL string AS variable')
def open_statement(p: list) -> Optional[ImageRepr]:

    if len(p) == 4:
        filename, name = p[1], p[-1]
    elif p[1].gettokentype() == "STREAM":
        index, name = p[2], p[-1]
        filename = parser._stream_env[index]
    elif p[1].gettokentype() == "URL":
        url, name = p[2], p[-1]
        with requests.get(url) as resp:
            filename = BytesIO(resp.content)
            
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
@parser.production('expr : SAVE variable STREAM string')
@parser.production('expr : SAVE variable string LOOP number')
@parser.production('expr : SAVE variable string DURATION number')
@parser.production('expr : SAVE variable string DURATION number LOOP number')
@parser.production('expr : SAVE variable STREAM string LOOP number')
@parser.production('expr : SAVE variable STREAM string DURATION number')
@parser.production('expr : SAVE variable STREAM string DURATION number LOOP number')
def save_statement(p: list) -> Union[str, BytesIO]:
    img = get_var(p[1], (ImageRepr, list))
    if isinstance(img, list):
        options = {}
        try:
            i = p.index(Token('DURATION', r'DURATION')) + 1
            j = p.index(Token('LOOP', r'LOOP')) + 1
            options['duration'], options['loop'] = p[i], p[j]
        except (ValueError, TypeError, IndexError):
            pass
    if Token('STREAM', r'STREAM') not in p:
        if isinstance(img, ImageRepr):
            img.image.save(p[2])
        else:
            img[0].save(p[2], 
                save_all=True,
                append_images=img[1:], 
                optimize=True, **options,
            )
        return p[2]
    else:
        buffer = BytesIO()
        if isinstance(img, ImageRepr):
            img.image.save(buffer, p[3])
        else:
            img[0].save(buffer, 
                p[3],
                save_all=True, 
                append_images=img[1:],
                optimize=True, **options,
            )
        buffer.seek(0)
        parser._saved_streams.append(buffer)
        return buffer

@parser.production('expr : CLOSE variable')
def close_statement(p: list) -> None:
    img = get_var(p[1])
    img.image.close()
    return None

@parser.production('expr : RESIZE variable ntuple')
def resize_statement(p: list) -> tuple:
    img = get_var(p[1])
    img.image = img.image.resize(p[-1])
    return p[-1]

@parser.production('expr : ROTATE variable number')
def rotate_statement(p: list) -> float:
    img = get_var(p[1])
    img.image = img.image.rotate(p[-1])
    return p[-1]

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

@parser.production('expr : PUTPIXEL variable ntuple color')
def putpixel(p: list) -> tuple:
    coords, color = p[2], p[-1]
    img = get_var(p[1])
    img.image.putpixel(coords, color)
    return coords
 
@parser.production('expr : SHOW variable')
@parser.production('expr : SHOW variable string')
def show_statement(p: list) -> Optional[str]:
    img = get_var(p[1])
    title = p[-1] if len(p) == 3 else None
    img.image.show(title=title)
    return title

@parser.production('expr : CROP variable')
@parser.production('expr : CROP variable ntuple')
def crop_statement(p: list) -> None:
    img = get_var(p[1])
    box = p[-1] if len(p) == 3 else None
    img.image = img.image.crop(box=box)
    return None

@parser.production('expr : SPREAD variable number')
def spread_st(p: list) -> None:
    img = get_var(p[1])
    img.image = img.image.effect_spread(p[-1])
    return None

@parser.production('expr : PUTALPHA variable ON variable')
def putalpha_st(p: list) -> None:
    img2, img = get_var(p[1]), get_var(p[3])
    img.image = img.image.putalpha(img2.image)
    return None

@parser.production('expr : REDUCE variable number')
@parser.production('expr : REDUCE variable number ntuple')
def reduce_st(p: list) -> None:
    img = get_var(p[1])
    box = p[-1] if len(p) == 4 else None
    img.image = img.image.reduce(p[2], box=box)

@parser.production('expr : SEEK variable number')
def seek_st(p: list) -> int:
    img = get_var(p[1])
    img.image.seek(p[2])
    return p[2]

@parser.production('expr : ECHO expr')
@parser.production('expr : ECHO string')
@parser.production('expr : ECHO number')
@parser.production('expr : ECHO ntuple')
def echo(p: list) -> Any:
    print(p[-1])
    return p[-1]

@parser.production('expr : ECHO variable')
def echo_var(p: list) -> Union[ImageRepr, list]:
    var = get_var(p[1])
    print(var)
    return var