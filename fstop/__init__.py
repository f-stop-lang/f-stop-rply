
import warnings
warnings.filterwarnings('ignore')

from .lexer import generator
from .parser import parser
from .objects import ImageRepr

from . import operations
from . import cv

lexer = generator.build()
parser = parser.build()

from .core import Runner

__title__ = 'f-stop'
__author__ = 'Tom-the-Bomb'
__version__ = '0.3.0'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021 Tom the Bomb'

__all__: tuple = (
    'ImageRepr',
    'lexer', 
    'parser', 
    'Runner',
)