from typing import List, Optional, Dict, Any
from io import BytesIO

import fstop

with open("test.ft") as ft:
    string = ft.read()

class Runner:

    def __init__(self) -> None:
        self._lexergen  = fstop.generator
        self._parsergen = fstop.parser
        self.lexer  = self._lexergen.build()
        self.parser = self._parsergen.build()
        self.streams = []

    def execute(
        self, 
        code: str, *,
        streams: Optional[List[BytesIO]] = []
    ) -> List[Any]:

        self._parsergen._stream_env = streams
        tokens = self.lexer.lex(code)
        return self.parser.parse(tokens)

    def reset(self) -> Dict:
        self._parsergen.env = {}
        self._parsergen._stream_env = []
        self._parser.gen._saved_streams = []
        self.streams = []
        return {}

if __name__ == '__main__':
    run = Runner()
    run.execute(string)