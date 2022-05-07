from typing import Optional, Union, Any
from io import BytesIO

from urllib import error as url_error
from urllib import request

from PIL import ImageSequence, Image
from rply import ParserGenerator, Token

from .lexer import generator
from .objects import *

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

def get_var(state: ParserState, name: str, _: type = ImageRepr) -> Optional[Union[ImageRepr, list, float]]:
    if (var := state.env.get(name)) is None:
        raise NameError("Undefined variable '%s'" % name)
    return var

# productions
# program statements

@parser.production("main : statements")
def program(state: ParserState, p: list) -> list:
    return p[0]

@parser.production("statements : statements expr")
def statements(state: ParserState, p: list) -> list:
    return p[0] + [p[1]]

@parser.production("statements : expr")
def expr(state: ParserState, p: list) -> list:
    return [p[0]]

@parser.production('expr : LEFT_PAREN expr RIGHT_PAREN')
@evaluate
def expr_paren(state: ParserState, p: list) -> Any:
    return p[1]()

# object type productions

@parser.production('string : STRING')
@parser.production('string : MODE variable')
@parser.production('string : FORMAT variable')
@evaluate
def string(state: ParserState, p: list) -> str:
    token = p[0].gettokentype()
    if token == 'STRING':
        return p[0].getstr().strip("'").strip('"')
    else:
        img = get_var(state, p[1])
        return (
            img.image.mode if token == 'MODE' else
            (img.image.format or (
                'PNG' if img.image.mode in ('RGBA', 'LA') else 'JPEG'
            ))
        )

@parser.production('number : INTEGER')
@parser.production('number : FLOAT')
@parser.production('number : WIDTH variable')
@parser.production('number : HEIGHT variable')
@parser.production('number : LENGTH variable')
@parser.production('number : LENGTH sequence')
@parser.production('number : TELL variable')
@parser.production('number : DURATION variable')
@parser.production('number : LOOP variable')
@evaluate
def number(state: ParserState, p: list) -> float:
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
            img = get_var(state, p[1], (ImageRepr, list))
            return (
                len(img) if isinstance(img, list) else getattr(img.image, 'n_frames', 1)
            )
    else:
        img = get_var(state, p[1])
        return (
            img.image.width if token == "WIDTH" else 
            img.image.height if token == "HEIGHT" else 
            img.image.tell() if token == "TELL" else 
            img.image.info.get('duration', 0) if token == "DURATION" else
            img.image.info.get('loop', 0) if token == "LOOP" else 0
        )

@parser.production('number : ADD number')
@parser.production('number : SUB number')
@evaluate
def pos_neg(state: ParserState, p: list) -> float:
    token = p[0].gettokentype()
    return -(p[1]()) if token == 'SUB' else p[1]()


@parser.production('number : number ADD number')
@parser.production('number : number SUB number')
@parser.production('number : number MUL number')
@parser.production('number : number DIV number')
@parser.production('number : number EXP number')
@parser.production('number : number FLOOR_DIV number')
@evaluate
def numerical_operations(state: ParserState, p: list) -> float:
    x, y = p[0](), p[2]()
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

@parser.production('number : variable')
@evaluate
def num_var(state: ParserState, p: list) -> Any:
    return get_var(state, p[0], (int, float))
    
@parser.production('variable : VARIABLE')
def variable(state: ParserState, p: list) -> str:
    return p[0].getstr()

@parser.production('ntuple_start : LEFT_PAREN number COMMA')
@evaluate
def ntuple_start(state: ParserState, p: list) -> tuple:
    return (p[1](),)

@parser.production('ntuple_start : ntuple_start number COMMA')
@evaluate
def ntuple_body(state: ParserState, p: list) -> tuple:
    return p[0]() + (p[1](),)

@parser.production('ntuple : ntuple_start RIGHT_PAREN')
@parser.production('ntuple : ntuple_start number RIGHT_PAREN')
@parser.production('ntuple : SIZE variable')
@evaluate
def ntuple(state: ParserState, p: list) -> tuple:
    if isinstance(p[0], Token):
        img = get_var(state, p[1])
        return img.image.size
    else:
        return p[0]() + (p[1](),) if len(p) == 3 else p[0]()

@parser.production('vartuple_start : LEFT_PAREN variable COMMA')
@evaluate
def vartuple_start(state: ParserState, p: list) -> tuple:
    return (p[1],)

@parser.production('vartuple_start : vartuple_start variable COMMA')
@evaluate
def vartuple_body(state: ParserState, p: list) -> tuple:
    return p[0]() + (p[1],)

@parser.production('vartuple : vartuple_start RIGHT_PAREN')
@parser.production('vartuple : vartuple_start variable RIGHT_PAREN')
@evaluate
def vartuple(state: ParserState, p: list) -> tuple:
    tup = p[0]() + (p[1],) if len(p) == 3 else p[0]()
    return tup

@parser.production('ntuple : TEXTSIZE font COMMA string')
@evaluate
def get_textsize(state: ParserState, p: list) -> tuple:
    return p[1]().getsize_multiline(p[-1]())

@parser.production('sequence_start : LEFT_BR')
def seq_start(state: ParserState, p: list) -> list:
    return []

@parser.production('sequence_start : sequence_start variable COMMA')
def seq_body(state: ParserState, p: list) -> list:
    return p[0] + [p[1]]

@parser.production('sequence : sequence_start RIGHT_BR')
@parser.production('sequence : sequence_start variable RIGHT_BR')
@parser.production('sequence : SEQUENCE variable')
@evaluate
def sequence(state: ParserState, p: list) -> list:
    if isinstance(p[0], Token):
        img = get_var(state, p[1])
        return list(ImageSequence.Iterator(img.image))
    else:
        seq = p[0] + [p[1]] if len(p) == 3 else p[0]
        return [getattr(get_var(state, i), 'image', None) for i in seq]

@parser.production('color : COLOR ntuple')
@parser.production('color : COLOR number')
@parser.production('color : COLOR string')
@evaluate
def color_st(state: ParserState, p: list) -> Union[tuple, int, str]:
    return p[-1]()

@parser.production('string : string ADD string')
@evaluate
def str_concat(state: ParserState, p: list) -> str:
    return p[0]() + p[-1]()

@parser.production('ntuple : ntuple ADD ntuple')
@evaluate
def tuple_concat(state: ParserState, p: list) -> tuple:
    return p[0]() + p[-1]()

@parser.production('vartuple : vartuple ADD vartuple')
@evaluate
def vartuple_concat(state: ParserState, p: list) -> tuple:
    return p[0]() + p[-1]()
    
@parser.production('sequence : sequence ADD sequence')
@evaluate
def seq_concat(state: ParserState, p: list) -> list:
    return p[0]() + p[-1]()

@parser.production('range : RANGE LEFT_PAREN number RIGHT_PAREN')
@parser.production('range : RANGE ntuple')
@evaluate
def range_(state: ParserState, p: list) -> range:
    if len(p) == 4:
        return range(p[2]())
    else:
        return range(*p[1]())

# operation productions


@parser.production('expr : DEL variable')
@evaluate
def del_st(state: ParserState, p: list) -> None:
    img = get_var(state, p[1], (list, ImageRepr))
    del img; del state.env[p[1]]

 
@parser.production('expr : APPEND variable TO variable')
@evaluate
def append_seq(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    seq = get_var(state, p[-1], list)
    return seq.append(img.image)

 
@parser.production('expr : BLEND variable COMMA variable ALPHA number AS variable')
@evaluate
def blend(state: ParserState, p: list) -> Image:
    backg, overlay, alpha, name = p[1], p[3], p[-3], p[-1]
    img1, img2 = get_var(state, backg), get_var(state, overlay)
    image = Image.blend(img1.image, img2.image, alpha=alpha())
    image = ImageRepr(image)
    state.env[name] = image
    return image

 
@parser.production('expr : NEW sequence AS variable')
@parser.production('expr : NEW string ntuple AS variable')
@parser.production('expr : NEW string ntuple color AS variable')
@evaluate
def new_statement(state: ParserState, p: list) -> Optional[ImageRepr]:

    if len(p) == 4:
        state.env[p[-1]] = p[1]()
    else:
        mode, size, name = p[1](), p[2](), p[-1]
        color = p[3]() if len(p) == 6 else 0
        image = Image.new(mode, size, color)
        image = ImageRepr(image)
        state.env[name] = image
        return image

@parser.production('expr : SPLIT variable AS vartuple')
@evaluate
def split_statement(state: ParserState, p: list) -> None:
    var, bands = p[1], p[3]()
    img = get_var(state, var)
    chan = img.image.split()

    if (a := len(bands)) != (b := len(chan)):
        raise ValueError('Got %s bands from the image, received %s variables to store as' % (b, a))
    else:
        for var, band in zip(bands, chan):
            img = ImageRepr(band)
            state.env[var] = img

 
@parser.production('expr : MERGE string vartuple AS variable')
@evaluate
def merge_statement(state: ParserState, p: list) -> Optional[ImageRepr]:
    mode, bands, name = p[1](), p[2](), p[4]

    bands = tuple(getattr(
        get_var(state, i), 'image', None) for i in bands
    )

    image = Image.merge(mode, bands)
    image = ImageRepr(image)
    state.env[name] = image
    return image

 
@parser.production('expr : OPEN string AS variable')
@parser.production('expr : OPEN STREAM number AS variable')
@parser.production('expr : OPEN URL string AS variable')
@evaluate
def open_statement(state: ParserState, p: list) -> Optional[ImageRepr]:

    if len(p) == 4:
        filename, name = p[1](), p[-1]
    elif p[1].gettokentype() == "STREAM":
        index, name = p[2](), p[-1]
        filename = state._stream_env[index]
    elif p[1].gettokentype() == "URL":
        url, name = p[2](), p[-1]
        try:
            payload = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with request.urlopen(payload) as resp:
                filename = BytesIO(resp.read())
        except url_error.HTTPError as exc:
            raise RuntimeError('Could not fetch the image properly; status-code: %s' % exc.getcode())

    image = Image.open(filename)
    
    image = ImageRepr(image)
    state.env[name] = image
    return image

 
@parser.production('expr : CLONE variable AS variable')
@evaluate
def clone_statement(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    name = p[-1]
    image = img.image.copy()
    image = ImageRepr(image)
    state.env[name] = image 
    return image

 
@parser.production('expr : CONVERT variable string')
@parser.production('expr : CONVERT variable string ntuple')
@evaluate
def convert_statement(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    matrix = p[-1]() if len(p) == 4 else None
    img.image = img.image.convert(p[2](), matrix=matrix)
    return None

 
@parser.production('expr : SAVE variable string')
@parser.production('expr : SAVE variable STREAM string')
@parser.production('expr : SAVE variable string LOOP number')
@parser.production('expr : SAVE variable string DURATION number')
@parser.production('expr : SAVE variable string DURATION number LOOP number')
@parser.production('expr : SAVE variable STREAM string LOOP number')
@parser.production('expr : SAVE variable STREAM string DURATION number')
@parser.production('expr : SAVE variable STREAM string DURATION number LOOP number')
@evaluate
def save_statement(state: ParserState, p: list) -> Union[str, BytesIO]:
    img = get_var(state, p[1], (ImageRepr, list))
    
    options = {}
    if (dur_tok := Token('DURATION', r'DURATION')) in p:
        i = p.index(dur_tok) + 1
        options['duration'] = p[i]()
        
    if (loop_tok := Token('LOOP', r'LOOP')) in p:
        j = p.index(loop_tok) + 1
        options['loop'] = p[j]()
        
    if Token('STREAM', r'STREAM') not in p:
        if isinstance(img, ImageRepr):
            img.image.save(p[2]())
        else:
            img[0].save(p[2](), 
                save_all=True,
                append_images=img[1:], 
                disposal=2, optimize=False, quality=100,
                **options
            )
        return p[2]()
    else:
        buffer = BytesIO()
        if isinstance(img, ImageRepr):
            img.image.save(buffer, p[3]())
        else:
            img[0].save(buffer, 
                p[3](),
                save_all=True, 
                append_images=img[1:],
                disposal=2, optimize=False, quality=100,
                **options
            )
        buffer.seek(0)
        state._saved_streams.append(buffer)
        return buffer

 
@parser.production('expr : CLOSE variable')
@evaluate
def close_statement(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    img.image.close()
    return None

 
@parser.production('expr : RESIZE variable ntuple')
@parser.production('expr : RESIZE variable ntuple string')
@parser.production('expr : RESIZE variable ntuple number')
@evaluate
def resize_statement(state: ParserState, p: list) -> tuple:
    img = get_var(state, p[1])
    resample = getattr(Image, str(p[-1]()), p[-1]()) if len(p) == 4 else 3
    img.image = img.image.resize(p[2](), resample=resample)
    return p[2]

 
@parser.production('expr : ROTATE variable number')
@parser.production('expr : ROTATE variable number string')
@parser.production('expr : ROTATE variable number number')
@evaluate
def rotate_statement(state: ParserState, p: list) -> float:
    img = get_var(state, p[1])
    resample = getattr(Image, str(p[-1]()), p[-1]()) if len(p) == 4 else 0
    img.image = img.image.rotate(p[2](), resample=resample)
    return p[2]

 
@parser.production('expr : PASTE variable ON variable')
@parser.production('expr : PASTE variable ON variable ntuple')
@parser.production('expr : PASTE variable ON variable MASK variable ntuple')
@evaluate
def paste_statement(state: ParserState, p: list) -> None:
    image, snippet = p[1], p[3]
    img1, img2 = get_var(state, image), get_var(state, snippet)
    xy = (0, 0) if len(p) == 4 else p[-1]()
    mask = get_var(state, p[-2]) if len(p) == 7 else None
    img2.image.paste(img1.image, xy, mask=mask.image)
    return None

 
@parser.production('expr : PUTPIXEL variable ntuple color')
@evaluate
def putpixel(state: ParserState, p: list) -> tuple:
    coords, color = p[2](), p[-1]()
    img = get_var(state, p[1])
    img.image.putpixel(coords, color)
    return coords

  
@parser.production('expr : SHOW variable')
@parser.production('expr : SHOW variable string')
@evaluate
def show_statement(state: ParserState, p: list) -> Optional[str]:
    img = get_var(state, p[1])
    title = p[-1]() if len(p) == 3 else None
    img.image.show(title=title)
    return title

 
@parser.production('expr : CROP variable')
@parser.production('expr : CROP variable ntuple')
@evaluate
def crop_statement(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    box = p[-1]() if len(p) == 3 else None
    img.image = img.image.crop(box=box)
    return None

 
@parser.production('expr : SPREAD variable number')
@evaluate
def spread_st(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    img.image = img.image.effect_spread(p[-1]())
    return None

 
@parser.production('expr : PUTALPHA variable ON variable')
@evaluate
def putalpha_st(state: ParserState, p: list) -> None:
    img2, img = get_var(state, p[1]), get_var(state, p[3])
    img.image.putalpha(img2.image)
    return None

 
@parser.production('expr : REDUCE variable number')
@parser.production('expr : REDUCE variable number ntuple')
@evaluate
def reduce_st(state: ParserState, p: list) -> None:
    img = get_var(state, p[1])
    box = p[-1]() if len(p) == 4 else None
    img.image = img.image.reduce(p[2](), box=box)

 
@parser.production('expr : SEEK variable number')
@evaluate
def seek_st(state: ParserState, p: list) -> int:
    img = get_var(state, p[1])
    img.image.seek(p[2]())
    return p[2]

 
@parser.production('expr : ECHO expr')
@parser.production('expr : ECHO string')
@parser.production('expr : ECHO ntuple')
@parser.production('expr : ECHO sequence')
@evaluate
def echo(state: ParserState, p: list) -> Any:
    print(p[-1]())
    return p[-1]()
 
@parser.production('expr : ECHO variable')
@evaluate
def echo_var(state: ParserState, p: list) -> Union[ImageRepr, list]:
    var = get_var(state, p[1], object)
    print(var)
    return var

@parser.production('expr : ECHO number')
@evaluate
def echo_num(state: ParserState, p: list) -> float:
    print(p[-1]())
    return p[-1]()

# iterators

@parser.production('expr : ITER LEFT_PAREN variable AS variable RIGHT_PAREN ARROW LEFT_PAREN statements RIGHT_PAREN')
@evaluate
def seq_iterator(state: ParserState, p: list) -> None:
    img = get_var(state, p[2])
    fr = p[4]
    
    old_frames = []
    new_frames = []

    if isinstance(img, ImageRepr):
        iterator = ImageSequence.Iterator(img.image)
    else:
        iterator = img

    for frame in iterator:
        old_frames.append(frame)
        state.env[fr] = ImageRepr(frame)

        for f in p[-2]:
            f()

        curr_frame = get_var(state, fr)
        new_frames.append(curr_frame.image)

    if old_frames != new_frames:
        state.env[p[2]] = new_frames

    try:
        del state.env[fr]
    except KeyError:
        pass

    return None

@parser.production('expr : ITER LEFT_PAREN ntuple AS variable RIGHT_PAREN ARROW LEFT_PAREN statements RIGHT_PAREN')
@parser.production('expr : ITER LEFT_PAREN range AS variable RIGHT_PAREN ARROW LEFT_PAREN statements RIGHT_PAREN')
@parser.production('expr : ITER LEFT_PAREN sequence AS variable RIGHT_PAREN ARROW LEFT_PAREN statements RIGHT_PAREN')
@evaluate
def for_loop_st(state: ParserState, p: list) -> None:
    var, iterable = p[4], p[2]()
    
    if isinstance(iterable, list):
        iterable = [ImageRepr(i) for i in iterable]
        
    for i in iterable:
        state.env[var] = i
        for f in p[-2]:
            f()
    try:
        del state.env[var]
    except KeyError:
        pass
    return None

# function impl

@parser.production('args : LEFT_PAREN RIGHT_PAREN')
@parser.production('args : LEFT_PAREN variable RIGHT_PAREN')
@parser.production('args : vartuple')
@evaluate
def fn_args(state: ParserState, p: list) -> tuple:
    if len(p) == 2:
        return ()
    elif len(p) == 3:
        return (p[1],)
    else:
        return p[0]()

@parser.production('arg : number')
@parser.production('arg : string')
@parser.production('arg : ntuple')
@parser.production('arg : sequence')
@parser.production('arg : color')
@parser.production('arg : range')
@evaluate
def arg_1(state: ParserState, p: list) -> Any:
    return p[0]()

@parser.production('arg : variable')
@evaluate
def arg_2(state: ParserState, p: list) -> Any:
    return get_var(p[0])

@parser.production('input_args_start : LEFT_PAREN')
@evaluate
def in_args_start(state: ParserState, p: list) -> tuple:
    return ()

@parser.production('input_args_start : input_args_start arg COMMA')
@evaluate
def in_args_body(state: ParserState, p: list) -> tuple:
    return p[0]() + (p[1](),)

@parser.production('input_args : input_args_start RIGHT_PAREN')
@parser.production('input_args : input_args_start arg RIGHT_PAREN')
@evaluate
def input_args(state: ParserState, p: list) -> tuple:
    return p[0]() + (p[1](),) if len(p) == 3 else p[0]()

@parser.production('expr : FN variable args ARROW LEFT_PAREN statements RIGHT_PAREN')
@evaluate
def function_def(state: ParserState, p: list) -> Function:
    name, args, statements = p[1], p[2](), p[5]
        
    fn = Function(state,
        name=name, 
        statements=statements,
        args=args
    )

    return fn

@parser.production('expr : CALL variable input_args')
@evaluate
def call_function(state: ParserState, p: list) -> None:
    name, args = p[1], p[2]()
    fn = get_var(state, name)
    return fn(*args)

# error handler

@parser.error
def error_handler(state: ParserState, token: Token):
    options = {
        'token': token.gettokentype(), 
        'pos': token.getsourcepos(),
        'val': token.getstr(),
    }
    raise SyntaxError(
        "Unexpected {token} at position {pos}\nvalue: '{val}'".format(**options)
    )