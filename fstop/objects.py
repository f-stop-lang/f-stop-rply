import numpy as np
from rply.token import BaseBox

class ImageRepr(BaseBox):

    def __init__(self, image):
        self.image = image
        self.array = np.asarray(self.image)
    
    def __repr__(self):
        return "<ImageRepr image='%s'>" % self.image

    def __getattribute__(self, attr: str):
        if attr == 'array':
            self.array = np.asarray(self.image)
            return self.array
        else:
            return super().__getattribute__(attr)