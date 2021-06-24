from typing import Callable

import cv2 as cv
import numpy as np
from PIL import Image

from .parser import parser, get_var
from .objects import ImageRepr

def _fromarray(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(
        cv.cvtColor(
            arr, cv.COLOR_BGR2RGB
        )
    )

def cv_process(img: str, operation: Callable, *args, **kwargs) -> np.ndarray:
    img = get_var(img)
    arr = operation(img.array, *args, **kwargs)
    if isinstance(arr, tuple):
        arr = arr[-1]
    img.array = arr
    img.image = _fromarray(arr)
    return arr

@parser.production('expr : CANNY variable number COMMA number')
def canny_st(p: list) -> np.ndarray:
    return cv_process(p[1], cv.Canny, p[2], p[4])

@parser.production('expr : CVTCOLOR variable string')
def colorspace_convert(p: list) -> np.ndarray:
    mapping = getattr(cv, 
        (p[2] if p[2].startswith('COLOR_') else 'COLOR_' + p[2]).upper()
    )
    return cv_process(p[1], cv.cvtColor, mapping)

@parser.production('expr : NOT variable')
def bitwise_not(p: list) -> np.ndarray:
    return cv_process(p[1], cv.bitwise_not)

@parser.production('expr : THRESHOLD variable number COMMA number string')
def threshold_st(p: list) -> np.ndarray:
    return cv_process(p[1], cv.threshold, p[2], p[4], getattr(cv, p[5].upper()))

@parser.production('expr : COLORMAP variable string')
def apply_color_map(p: list) -> np.ndarray:
    mapping = getattr(cv, 
        (p[2] if p[2].startswith('COLORMAP_') else 'COLORMAP_' + p[2]).upper()
    )
    return cv_process(p[1], cv.applyColorMap, mapping)

@parser.production('expr : variable INRANGE ntuple COMMA ntuple AS variable')
def inrange_st(p: list) -> ImageRepr:
    img = get_var(p[0])
    arr = cv.inRange(img.array, p[2], p[4])
    img = ImageRepr(_fromarray(arr))
    parser.env[p[-1]] = img
    return img

@parser.production('expr : variable AND variable AS variable')
def bitwise_and(p: list) -> ImageRepr:
    img, img2 = get_var(p[0]), get_var(p[2])
    arr = cv.bitwise_and(img.array, img2.array)
    img = ImageRepr(_fromarray(arr))
    parser.env[p[-1]] = img
    return img

@parser.production('expr : variable OR variable AS variable')
def bitwise_or(p: list) -> ImageRepr:
    img, img2 = get_var(p[0]), get_var(p[2])
    arr = cv.bitwise_or(img.array, img2.array)
    img = ImageRepr(_fromarray(arr))
    parser.env[p[-1]] = img
    return img

@parser.production('expr : variable XOR variable AS variable')
def bitwise_xor(p: list) -> ImageRepr:
    img, img2 = get_var(p[0]), get_var(p[2])
    arr = cv.bitwise_xor(img.array, img2.array)
    img = ImageRepr(_fromarray(arr))
    parser.env[p[-1]] = img
    return img