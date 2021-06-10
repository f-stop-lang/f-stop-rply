from rply.token import BaseBox
from PIL import Image as PIL_Image

class Image(BaseBox):

    def __init__(self, image: PIL_Image.Image, *, name: str) -> None:
        self.name = name
        self.image = image

    def __repr__(self):
        return "<Image '%s'>" % self.name