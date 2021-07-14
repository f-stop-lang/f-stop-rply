from typing import List, Optional, Any
from io import BytesIO

from .objects import ParserState

from . import lexer, parser

class Runner:

    def __init__(self, reset_after_execute: bool = False) -> None:
        self._reset_after_execute = reset_after_execute
        self._lexer  = lexer
        self._parser = parser

        self._state  = ParserState()

    def execute(
        self, 
        code: str, *,
        streams: Optional[List[BytesIO]] = []
    ) -> List[Any]:

        self._state._stream_env = streams

        tokens = self._lexer.lex(code)
        _ = [f() for f in self._parser.parse(tokens, state=self._state)]

        self.streams = self._state._saved_streams

        if self._reset_after_execute:
            self._state = ParserState()

        return self.streams

    @property
    def stream(self) -> Optional[BytesIO]:
        try:
            return self.streams[0]
        except IndexError:
            return None