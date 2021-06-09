from PIL import ImageOps, ImageFilter

from .parser import parser

def operation(p, operation, *args, **kwargs):
    if not (img := parser.env.get(p[-1])):
        raise NameError("Undefined image '%s'" % p[-1])
    else:
        img.image = operation(
            img.image.convert("RGB"),
            *args, **kwargs
        )
        parser.env[p[-1]] = img
    return None

@parser.production('string : INVERT variable')
def invert_op(p: list) -> None:
    operation(p, ImageOps.invert)

@parser.production('string : SOLAR variable number')
def invert_op(p: list) -> None:
    value = p[-1]
    operation(p, ImageOps.solarize, value)

@parser.production('string : MIRROR variable')
def invert_op(p: list) -> None:
    operation(p, ImageOps.mirror)

@parser.production('string : FLIP variable')
def invert_op(p: list) -> None:
    operation(p, ImageOps.flip)