from PIL import ImageOps, ImageDraw, ImageFilter
from PIL.Image import Image

from .parser import parser, get_var

def operation(p, operation, *, mode: str = 'RGBA', *args, **kwargs):
    image = get_var(p[1])
    image.image = operation(
        image.image.convert(mode),
        *args, **kwargs
    )
    return None

def image_draw(img, operation: str, *args, **kwargs) -> None:
    cursor = ImageDraw.Draw(img.image)
    getattr(cursor, operation)(*args, **kwargs)
    return None

@parser.production('expr : INVERT variable')
def invert_op(p: list) -> None:
    operation(p, ImageOps.invert, mode='RGB')

@parser.production('expr : GRAYSCALE variable')
def grayscale_op(p: list) -> None:
    operation(p, ImageOps.grayscale, mode='RGB')

@parser.production('expr : MIRROR variable')
def mirror_op(p: list) -> None:
    operation(p, ImageOps.mirror, mode='RGB')

@parser.production('expr : FLIP variable')
def flip_op(p: list) -> None:
    operation(p, ImageOps.flip, mode='RGB')

@parser.production('expr : SOLARIZE variable')
@parser.production('expr : SOLARIZE variable number')
def solar_op(p: list) -> None:
    value = p[-1] if len(p) == 3 else 128
    operation(p, ImageOps.solarize, value, mode='RGB')

@parser.production('expr : POSTERIZE variable')
@parser.production('expr : POSTERIZE variable number')
def poster_op(p: list) -> None:
    value = p[-1] if len(p) == 3 else 4
    operation(p, ImageOps.solarize, value, mode='RGB')

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