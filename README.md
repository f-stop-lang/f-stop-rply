# F-Stop
![logo](https://avatars.githubusercontent.com/u/85209342?s=200&v=4)
---
- A mini-lang for basic image manipulation written in python

- Uses rply for lexing / parsing
    - Pillow & OpenCV for the processing

## Execution

```py
from fstop import Runner

runner = Runner(reset_after_execute=True)
# reset_after_execute indicates to not preserve state after each execution
runner.execute(
    'ECHO "hello world"' # hello world program :D
)
```

## Language Examples

(basic)
```prolog
OPEN 'filename.png' AS img // Opens a local image
CONVERT img "RGBA"         // convert to RGBA mode
RESIZE  img (256, 256)     // resize image to size 256 x 256
BLUR img 10 v              // blur the image by 10 deg
SAVE img 'OUTPUT.PNG'      // save the image as output.png
```

(streams)
- streams can be passed in via the `streams` kwarg in `execute`
EX: `runner.execute(..., streams=[BytesIO(some_bytes)])`
- And can be accessed via `OPEN STREAM index AS ...`

```prolog
OPEN STREAM 0 AS img
INVERT img
SAVE img 'out.jpg'
```
- you can save output images into streams ex:
`SAVE img STREAM 'png'`
- they can be accessed via `runner.streams` which will return `List[BytesIO]`

(sequences / GIFs)
```prolog
NEW [] AS sequence // new empty sequence

OPEN 'frame1.png' AS frame1
APPEND frame1 TO sequence // append to sequence
OPEN 'frame2.png' AS frame2
APPEND frame2 TO sequence // append to sequence

SAVE sequence 'test.gif' 
// specify duration and loop vvv
SAVE sequence 'test.gif' DURATION 10 LOOP 0

// initialize sequence with existing frames
NEW [img, img2] AS seq
// initialize sequence from a gif image
NEW SEQUENCE img AS seq
```

(Iterating)
```prolog
// iterate over a container
ITER ((0, 5, 1, 2) AS i) -> (
    ECHO i
) // tuple

ITER ([img1, img2, img3] AS frame) -> (
    APPEND frame TO something
) // sequence

ITER (RANGE (1, 20) AS deg) -> (
    CLONE img AS clone
    BLUR clone deg
    SAVE clone STREAM 'PNG'
) // iter over a range and blur image by that degree

ITER (img AS frame) -> (
    INVERT frame
) // iterates over an image and inverts each frame
// same effect as INVERT img, 
// but that inverts the first frame only and makes it static
// which is fine for static images but not really for gifs
```

(pasting and blending)
```prolog
BLEND img, img2 ALPHA 0.5 AS blended
```
```prolog
PASTE img ON img2 (10, 10)
// with a mask
PASTE img ON img2 MASk mask (10, 10)
```

and more! (soon)

- fstop is still in early development
- bug fixes will come soon, open an issue if you encounter one :)
- more features to come
    - more opencv features
    - variable declaration
    - better imagedraws

---
(Still a WIP)                                                                     
**[Documentation](https://f-stop-lang.github.io/docs/)**

#### Contributors

1. **Tom-the-Bomb**   - Main dev of this impl
2. **MrKomodoDragon** - Main dev of the `lark` implementation
3. **Cryptex-github** - helps with the docs
4. **Jay3332** - Helps with ideas, regex and other stuff