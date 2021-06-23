import numpy as np
import cv2 as cv
from rply.token import BaseBox

class ImageRepr(BaseBox):

    def __init__(self, image):
        self.image = image
        self.array = np.array(self.image)
    
    def __repr__(self):
        return "<ImageRepr image='%s'>" % self.image

    def __getattribute__(self, attr: str):
        if attr == 'array':
            self.array = arr = np.array(self.image)
            return arr
        else:
            return super().__getattribute__(attr)