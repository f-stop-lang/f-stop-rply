from PIL import ImageOps, ImageFilter

from .parser import parser

def operation(p, operation, *args, **kwargs):
    if not (image := parser.env.get(p[1])):
        raise NameError("Undefined image '%s'" % p[1])
    else:
        image.image = operation(
            image.image.convert("RGB"),
            *args, **kwargs
        )
    return None

@parser.production('expr : INVERT variable')
def invert_op(p: list) -> None:
    operation(p, ImageOps.invert)

@parser.production('expr : SOLARIZE variable')
@parser.production('expr : SOLARIZE variable number')
def solar_op(p: list) -> None:
    value = p[-1] if len(p) == 3 else 128
    operation(p, ImageOps.solarize, value)

@parser.production('expr : MIRROR variable')
def mirror_op(p: list) -> None:
    operation(p, ImageOps.mirror)

@parser.production('expr : FLIP variable')
def flip_op(p: list) -> None:
    operation(p, ImageOps.flip)