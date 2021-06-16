
from typing import Callable

from PIL import ImageOps, ImageDraw, ImageFont, ImageFilter
from PIL.Image import Image

from .parser import parser, get_var
from .objects import ImageRepr

def operation(p: list, operation: Callable, *args, **kwargs):
    image = get_var(p[1])
    mode = 'RGB' if operation.__module__ == 'PIL.ImageOps' else 'RGBA'
    image.image = operation(
        image.image.convert(mode),
        *args, **kwargs
    )
    return None

@parser.production('expr : INVERT variable')
def invert_op(p: list) -> None:
    operation(p, ImageOps.invert)

@parser.production('expr : GRAYSCALE variable')
def grayscale_op(p: list) -> None:
    operation(p, ImageOps.grayscale)

@parser.production('expr : MIRROR variable')
def mirror_op(p: list) -> None:
    operation(p, ImageOps.mirror)

@parser.production('expr : FLIP variable')
def flip_op(p: list) -> None:
    operation(p, ImageOps.flip)

@parser.production('expr : SOLARIZE variable')
@parser.production('expr : SOLARIZE variable number')
def solar_op(p: list) -> None:
    value = p[-1] if len(p) == 3 else 128
    operation(p, ImageOps.solarize, value)

@parser.production('expr : POSTERIZE variable')
@parser.production('expr : POSTERIZE variable number')
def poster_op(p: list) -> None:
    value = p[-1] if len(p) == 3 else 4
    if value < 1 or value > 8:
        raise Exception("Number must be an integer between 1 and 8")
    operation(p, ImageOps.solarize, value)

# filters

@parser.production('expr : EMBOSS variable')
def emboss(p: list) -> None:
    return operation(p, Image.filter, ImageFilter.EMBOSS)

@parser.production('expr : SMOOTH variable')
def smooth(p: list) -> None:
    return operation(p, Image.filter, ImageFilter.SMOOTH_MORE)

@parser.production('expr : SHARPEN variable')
def sharpen(p: list) -> None:
    return operation(p, Image.filter, ImageFilter.SHARPEN)

@parser.production('expr : DETAIL variable')
def detail(p: list) -> None:
    return operation(p, Image.filter, ImageFilter.DETAIL)

@parser.production('expr : CONTOUR variable')
def contour(p: list) -> None:
    return operation(p, Image.filter, ImageFilter.CONTOUR)

@parser.production('expr : EDGE_ENHANCE variable')
def edge_enhance(p: list) -> None:
    return operation(p, Image.filter, ImageFilter.EDGE_ENHANCE_MORE)

@parser.production('expr : BLUR variable')
@parser.production('expr : BLUR variable number')
def blur(p: list) -> None:
    radius = p[-1] if len(p) == 3 else 2
    return operation(p, Image.filter, ImageFilter.GaussianBlur, radius)

@parser.production('expr : MAX_FILTER variable')
@parser.production('expr : MAX_FILTER variable number')
def max_filter(p: list) -> None:
    deg = p[-1] if len(p) == 3 else 3
    return operation(p, Image.filter, ImageFilter.MaxFilter, deg)

@parser.production('expr : MIN_FILTER variable')
@parser.production('expr : MIN_FILTER variable number')
def min_filter(p: list) -> None:
    deg = p[-1] if len(p) == 3 else 3
    return operation(p, Image.filter, ImageFilter.MinFilter, deg)

@parser.production('expr : MODE_FILTER variable')
@parser.production('expr : MODE_FILTER variable number')
def mode_filter(p: list) -> None:
    deg = p[-1] if len(p) == 3 else 3
    return operation(p, Image.filter, ImageFilter.ModeFilter, deg)

@parser.production('expr : MEDIAN_FILTER variable')
@parser.production('expr : MEDIAN_FILTER variable number')
def median_filter(p: list) -> None:
    deg = p[-1] if len(p) == 3 else 3
    return operation(p, Image.filter, ImageFilter.MedianFilter, deg)

# ImageDraw operations

def draw(img: ImageRepr, operation: str, *args, **kwargs) -> ImageDraw.Draw:
    img = get_var(img)
    cursor = ImageDraw.Draw(img.image)
    operation = getattr(cursor, operation)
    operation(*args, **kwargs)
    return cursor

@parser.production('font : FONT string')
@parser.production('font : FONT LEFT_PAREN string COMMA number RIGHT_PAREN')
def get_font(p: list) -> ImageFont.FreeTypeFont:
    if len(p) == 2:
        return ImageFont.truetype(p[1])
    else:
        return ImageFont.truetype(p[2], p[4])

@parser.production('expr : TEXT variable string ntuple')
@parser.production('expr : TEXT variable string ntuple font')
@parser.production('expr : TEXT variable string ntuple color')
@parser.production('expr : TEXT variable string ntuple font color')
def write_text(p: list) -> ImageDraw.Draw:
    coords, text = p[3], p[2]
    fill = p[-1] if len(p) > 4 and not isinstance(p, ImageFont.FreeTypeFont) else None
    font = p[4] if len(p) > 4 and isinstance(p[4], ImageFont.FreeTypeFont) else None
    return draw(p[1], 'text', xy=coords, text=text, fill=fill, font=font)


@parser.production('expr : LINE variable ntuple')
@parser.production('expr : LINE variable ntuple color')
def draw_line(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 4 else None
    return draw(p[1], 'line', xy=p[2], fill=fill)

@parser.production('expr : LINE variable ntuple number')
@parser.production('expr : LINE variable ntuple number color')
def draw_line_w(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 5 else None
    return draw(p[1], 'line', xy=p[2], fill=fill, width=p[3])


@parser.production('expr : ELLIPSE variable ntuple')
@parser.production('expr : ELLIPSE variable ntuple color')
def draw_ellipse(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 4 else None
    return draw(p[1], 'ellipse', xy=p[2], fill=fill)

@parser.production('expr : ELLIPSE variable ntuple number')
@parser.production('expr : ELLIPSE variable ntuple number color')
def draw_ellipse_w(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 5 else None
    return draw(p[1], 'ellipse', xy=p[2], fill=fill, width=p[3])


@parser.production('expr : DOT variable ntuple')
@parser.production('expr : DOT variable ntuple color')
def draw_dot(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 4 else None
    return draw(p[1], 'point', xy=p[2], fill=fill)

@parser.production('expr : ARC variable ntuple number COMMA number')
@parser.production('expr : ARC variable ntuple number COMMA number color')
def draw_arc(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 7 else None
    return draw(p[1], 'arc', xy=p[2], start=p[3], end=p[5], fill=fill)

@parser.production('expr : CHORD variable ntuple number COMMA number')
@parser.production('expr : CHORD variable ntuple number COMMA number color')
def draw_chord(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 7 else None
    return draw(p[1], 'chord', xy=p[2], start=p[3], end=p[5], fill=fill)

@parser.production('expr : POLYGON variable ntuple')
@parser.production('expr : POLYGON variable ntuple color')
def draw_polygon(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 4 else None
    return draw(p[1], 'polygon', xy=p[2], fill=fill)

@parser.production('expr : RECTANGLE variable ntuple')
@parser.production('expr : RECTANGLE variable ntuple color')
def draw_rec(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 4 else None
    return draw(p[1], 'rectangle', xy=p[2], fill=fill)

@parser.production('expr : RECTANGLE variable ntuple number')
@parser.production('expr : RECTANGLE variable ntuple number color')
def draw_rec_w(p: list) -> ImageDraw.Draw:
    fill = p[-1] if len(p) == 5 else None
    return draw(p[1], 'rectangle', xy=p[2], fill=fill, width=p[3])
