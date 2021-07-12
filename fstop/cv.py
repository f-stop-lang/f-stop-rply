from typing import Callable, Union

import cv2 as cv
import numpy as np
from PIL import Image

from .parser import parser, get_var
from .objects import *

def _fromarray(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(
        cv.cvtColor(
            arr, cv.COLOR_BGR2RGB
        )
    )

def cv_process(state: ParserState, img: str, operation: Callable, *args, **kwargs) -> np.ndarray:
    img = get_var(state, img)
    arr = operation(img.array, *args, **kwargs)
    if isinstance(arr, tuple):
        arr = arr[-1]
    img.array = arr
    img.image = _fromarray(arr)
    return arr

def _corner_dtc(state: ParserState, var: str, fill: Union[int, tuple] = (255, 255, 255), size: int = 5) -> np.ndarray:
    img = get_var(state, var)
    arr: np.ndarray = img.array

    if len(arr.shape[2]) != 1:
        gray = cv.cvtColor(arr, cv.COLOR_BGR2GRAY)
    else:
        gray = arr.copy()

    corners = cv.goodFeaturesToTrack(gray, 100, 0.01, 10)
    corners = np.int0(corners)

    for corner in corners:
        x, y = corner.ravel()
        cv.circle(arr, (x, y), size, fill, -1)

    img.array = arr
    img.image = _fromarray(arr)
    return arr
    
 
@parser.production('expr : CANNY variable number COMMA number')
@evaluate
def canny_st(state: ParserState, p: list) -> np.ndarray:
    return cv_process(state, p[1], cv.Canny, p[2](), p[4]())

 
@parser.production('expr : CVTCOLOR variable string')
@evaluate
def colorspace_convert(state: ParserState, p: list) -> np.ndarray:
    val = p[2]()
    mapping = getattr(cv, 
        (val if val.startswith('COLOR_') else 'COLOR_' + val).upper()
    )
    return cv_process(state, p[1], cv.cvtColor, mapping)

 
@parser.production('expr : NOT variable')
@evaluate
def bitwise_not(state: ParserState, p: list) -> np.ndarray:
    return cv_process(state, p[1], cv.bitwise_not)

 
@parser.production('expr : THRESHOLD variable number COMMA number string')
@evaluate
def threshold_st(state: ParserState, p: list) -> np.ndarray:
    return cv_process(state, p[1], cv.threshold, p[2](), p[4](), getattr(cv, p[5]().upper()))

 
@parser.production('expr : COLORMAP variable string')
@evaluate
def apply_color_map(state: ParserState, p: list) -> np.ndarray:
    val = p[2]()
    mapping = getattr(cv, 
        (val if val.startswith('COLORMAP_') else 'COLORMAP_' + val).upper()
    )
    return cv_process(state, p[1], cv.applyColorMap, mapping)

 
@parser.production('expr : variable INRANGE ntuple COMMA ntuple AS variable')
@evaluate
def inrange_st(state: ParserState, p: list) -> ImageRepr:
    img = get_var(state, p[0])
    arr = cv.inRange(
        img.array, 
        np.uint8(p[2]()), 
        np.uint8(p[4]()),
    )
    img = ImageRepr(_fromarray(arr))
    state.env[p[-1]] = img
    return img

@parser.production('expr : BILFILTER variable number COMMA number COMMA number')
@evaluate
def bilateral_filter(state: ParserState, p: list) -> np.ndarray:
    return cv_process(state, p[1], cv.bilateralFilter, p[2](), p[4](), p[6]())

@parser.production('cascade :  CASCADE string')
@evaluate
def get_cascade(state: ParserState, p: list) -> cv.CascadeClassifier:
    path = p[1]
    if (cascade := state._cascade_cache.get(path)):
        return cascade
    else:
        cascade = cv.CascadeClassifier(path)
        state._cascade_cache[path] = cascade
        return cascade 
    
@parser.production('expr : DETECT variable cascade number COMMA number')
@parser.production('expr : DETECT variable cascade number COMMA number COMMA number')
@parser.production('expr : DETECT variable cascade number COMMA number COMMA number color')
@parser.production('expr : DETECT variable cascade number COMMA number color')
@evaluate 
def detect(state: ParserState, p: list) -> np.ndarray:
    img, cascade, scale, minN = p[1], p[2](), p[3](), p[5]()
    color = p[-1] if len(p) in (7, 9) else (0, 0, 0)
    width = p[7] if len(p) > 7 else 5

    img = get_var(state, img)

    arr: np.ndarray = img.array

    if len(arr.shape[2]) != 1:
        gray = cv.cvtColor(arr, cv.COLOR_BGR2GRAY)
    else:
        gray = arr.copy()

    rect = cascade.detectMultiScale(gray, scale, minN)

    for (x, y, w, h) in rect:
        cv.rectangle(arr, (x, y), (x + w, y + h), color, width)

    img.array = arr
    img.image = _fromarray(arr)
    return arr

@parser.production('expr : CORNERS variable')
@parser.production('expr : CORNERS variable number')
@evaluate
def corner_detect(state: ParserState, p: list) -> np.ndarray:
    size = p[2] if len(p) == 3 else 3
    return _corner_dtc(state, p[1], size=size)

@parser.production('expr : CORNERS variable color')
@parser.production('expr : CORNERS variable number color')
@evaluate
def corner_detect_c(state: ParserState, p: list) -> np.ndarray:
    size = p[2] if len(p) == 4 else 3
    return _corner_dtc(state, p[1], fill=p[-1](), size=size)
    

@parser.production('expr : variable AND variable AS variable')
@evaluate
def bitwise_and(state: ParserState, p: list) -> ImageRepr:
    img, img2 = get_var(state, p[0]), get_var(state, p[2])
    arr = cv.bitwise_and(img.array, img2.array)
    img = ImageRepr(_fromarray(arr))
    state.env[p[-1]] = img
    return img

 
@parser.production('expr : variable OR variable AS variable')
@evaluate
def bitwise_or(state: ParserState, p: list) -> ImageRepr:
    img, img2 = get_var(state, p[0]), get_var(state, p[2])
    arr = cv.bitwise_or(img.array, img2.array)
    img = ImageRepr(_fromarray(arr))
    state.env[p[-1]] = img
    return img

 
@parser.production('expr : variable XOR variable AS variable')
@evaluate
def bitwise_xor(state: ParserState, p: list) -> ImageRepr:
    img, img2 = get_var(state, p[0]), get_var(state, p[2])
    arr = cv.bitwise_xor(img.array, img2.array)
    img = ImageRepr(_fromarray(arr))
    state.env[p[-1]] = img
    return img