from rply.token import BaseBox
from PIL import Image as PIL_Image

class Image(BaseBox):

    def __init__(self, file: str, name: str) -> None:
        self.file = file
        self.name = name
        self.image = PIL_Image.open(file)

    def __repr__(self):
        return "<Image '%s'>" % self.name