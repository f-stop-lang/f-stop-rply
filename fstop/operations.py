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

@parser.production('expression : INVERT expression')
def invert_op(p: list) -> None:
    operation(p, ImageOps.invert)