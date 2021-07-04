from typing import List, Optional, Dict, Any
from io import BytesIO

import fstop

import importlib
importlib.reload(fstop)

class Runner:

    def __init__(self, reset_after_execute: Optional[bool] = False) -> None:
        self._reset_after_execute = reset_after_execute
        self._lexergen  = fstop.generator
        self._parsergen = fstop.parser

        self._lexer  = self._lexergen.build()
        self._parser = self._parsergen.build()

        self._state  = fstop.objects.ParserState()

    def execute(
        self, 
        code: str, *,
        streams: Optional[List[BytesIO]] = []
    ) -> List[Any]:

        self._state._stream_env = streams

        tokens = self._lexer.lex(code)
        result = [f() for f in self._parser.parse(tokens, state=self._state)]

        self.streams = self._state._saved_streams

        if self._reset_after_execute:
            self._state = fstop.objects.ParserState()

        return result
    

if __name__ == '__main__':
    with open("test.ft") as ft:
        string = ft.read()

    run = Runner()
    print(run.execute(string))