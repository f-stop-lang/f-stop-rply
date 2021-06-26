from typing import List, Optional, Dict, Any
from io import BytesIO

import fstop

class Runner:

    def __init__(self) -> None:
        self._lexergen  = fstop.generator
        self._parsergen = fstop.parser
        self.lexer  = self._lexergen.build()
        self.parser = self._parsergen.build()
        self.reset()

    def execute(
        self, 
        code: str, *,
        streams: Optional[List[BytesIO]] = []
    ) -> List[Any]:

        self._parsergen._stream_env = streams
        tokens = self.lexer.lex(code)
        result = [f() for f in self.parser.parse(tokens)]
        self.streams = self._parsergen._saved_streams
        #print(self._parsergen.env)
        return result

    def reset(self) -> Dict:
        self._parsergen.env = {}
        self._parsergen._stream_env = []
        self._parsergen._saved_streams = []
        self.streams = []
        return {}

if __name__ == '__main__':
    with open("test.ft") as ft:
        string = ft.read()

    run = Runner()
    print(run.execute(string))