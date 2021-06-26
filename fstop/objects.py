import numpy as np
import cv2 as cv
from rply.token import BaseBox

class ImageRepr(BaseBox):

    def __init__(self, image):
        self.image = image
        self.array = self._get_arr()

    def _get_arr(self):
        return cv.cvtColor(
            np.asarray(self.image), 
            cv.COLOR_RGB2BGR
        )
    
    def __repr__(self):
        return "<ImageRepr image='%s'>" % self.image

    def __getattribute__(self, attr: str):
        if attr == 'array':
            self.array = arr = self._get_arr()
            return arr
        else:
            return super().__getattribute__(attr)

def evaluate(fn):
    def wrapper(p):
        def inner():
            return fn(p)
        return inner
    return wrapper