from __future__ import annotations

from typing import Dict, Any, Callable, List, Tuple
from io import BytesIO

import numpy as np
import cv2 as cv

from PIL.ImageFont import FreeTypeFont
from rply.token import BaseBox

Streams = List[BytesIO]
Fonts = Dict[Tuple[str, int], FreeTypeFont]
Cascades = Dict[str, cv.CascadeClassifier]

__all__: tuple = (
    'Function',
    'ImageRepr', 
    'ParserState', 
    'evaluate',
)

class Function:

    def __init__(self, 
        state: ParserState, 
        name: str, 
        statements: List[Callable[[], Any]],
        args: Tuple[str, ...],
    ) -> None:

        self._state = state
        self._name = name
        self._statements = statements
        self._args = args

        state.env[self._name] = self
    
    def __call__(self, *values) -> None:
        return self.callback(*values)

    def callback(self, *args) -> None:
        for k, v in zip(self._args, args):
            self._state.env[k] = v
        for st in self._statements:
            st()

class ImageRepr(BaseBox):

    def __init__(self, image) -> None:
        self.image = image
        self.array = self._get_arr()

    def _get_arr(self) -> np.ndarray:
        return cv.cvtColor(
            np.asarray(self.image), 
            cv.COLOR_RGB2BGR
        )
    
    def __repr__(self) -> str:
        return "<ImageRepr image='%s'>" % self.image

    def __getattribute__(self, attr: str) -> Any:
        if attr == 'array':
            self.array = arr = self._get_arr()
            return arr
        else:
            return super().__getattribute__(attr)

class ParserState:

    def __init__(self, env: Dict[str, Any] = None) -> None:
        self.env = env or {}
        self._stream_env: Streams = []
        self._saved_streams: Streams = []
        self._font_cache: Fonts = {}
        self._cascade_cache: Cascades = {}


def evaluate(fn: Callable):
    def wrapper(state: ParserState, p: list):
        def inner():
            return fn(state, p)
        return inner
    return wrapper