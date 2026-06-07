# CurlingSheet

*(For the Japanese version, see [README.md](README.md).)*

## Quick Start
The latest version of the application is available on the [Releases page](https://github.com/szmrki/CurlingSheet/releases).

- Download the `CurlingSheet-vX.Y.Z.exe`

## Features
- Place stones freely at any position on the sheet
- Supports both normal and Mixed Doubles (MD) formats
- Save the sheet as an image, including stones
- Export stone placements to a JSON file
- Import stone placements from a JSON file ([JSON Format](#json-format))
- Customize the color of the house

## System Requirements
- Windows11
- Python 3.12+
- Display resolution: **at least 945 pixels in height**
    > Note: The application window height is fixed at 945 pixels.
    > If your screen resolution is high enough but the entire application window is not fully visible, 
    please check the [Display Settings](#display-settings) section. 

## Installation via pip

~~~cmd
pip install git+https://github.com/szmrki/CurlingSheet.git
~~~

After installation, launch the app with:

~~~cmd
curlingsheet
~~~

You can also use it as a library in your own project:

~~~python
from curlingsheet.sheet import Sheet
from curlingsheet import sheet2pos as sp
~~~

See [Using as a Library](#using-as-a-library) for drawing the sheet with
matplotlib or your own renderer, and for toggling the MD points / outer frame.

## Installation from Source (on Windows)

If you want to run the app from the source code, follow these steps:

### Clone this Repository
~~~cmd
git clone https://github.com/szmrki/CurlingSheet.git
cd CurlingSheet
~~~

### Create Virtual Environment
~~~cmd
python -m venv .venv
.venv\Scripts\activate.bat      #cmd
.\.venv\Scripts\Activate.ps1    #Powershell
(.venv) pip install -e .
~~~

### Test
~~~cmd
python main.py
~~~

### Create .exe File
~~~cmd
pyinstaller main.spec
~~~

- Open the `dist` folder and you should see the `CurlingSheet.exe` file. This is the latest vesion.  
- You can remove `build` folder.

### Display Settings
Follow these steps to set display scalling to 100% for the application executable:

1. Right-click on your desktop and select **Display settings**.
1. Scroll down to the **Scale & layout** section.
1. Under **Scale**, select **100%** from the dropdown.
>Note: Changing the scaling setting affects the entire system. 
You may want to restore your display scaling to the recommended setting after closing the app.

## Using as a Library

The drawing is split into two layers so it can be rendered by any backend:

1. **Spec layer** (`curlingsheet.spec`, `curlingsheet.primitives`) — backend
   independent. `build_sheet_spec()` turns options + stones into a list of
   plain shapes (`Circle` / `Line` / `Rect`) in screen coordinates
   (origin top-left, y downwards, unit = px, sheet size 300×600).
   This layer does **not** import PyQt6.
2. **Renderers** (`curlingsheet.renderers`) — consume a spec and draw it.
   `render_qt` (PyQt6) is what the desktop app uses; `render_matplotlib`
   draws onto a matplotlib `Axes`. Writing your own is just a loop over the
   shapes.

### Options: MD points / outer frame / house colors

`SheetOptions` controls what is drawn. All toggles default to the same look
as the desktop app, so existing behavior is unchanged.

~~~python
from curlingsheet import SheetOptions

opts = SheetOptions(
    show_pochi=False,   # MD points (ポチ) on/off
    show_frame=False,   # outer frame on/off
    show_background=True,
    color12=2,          # 12-foot circle color index (0=red, 1=blue, 2=green)
    color4=0,           # 4-foot circle color index
)
~~~

> `SheetOptions` is only needed when you want to change something from the
> default. If the default look is fine, you can omit it from
> `build_sheet_spec()` (defaults are used internally).

## Generating sheet images as a library

There are two ways to generate a sheet image from another script.

| What you want | Recommended |
|------|------|
| A **pixel-identical** image to the desktop app / already inside a Qt app | **Route A** |
| Image generation in a Qt-free script / embedding into a matplotlib figure | **Route B** |
| Mouse interaction / editing in a GUI | Use `Sheet` as a widget |
| Drawing with your own library | [Write your own renderer](#write-your-own-renderer) |

### Route A: `Sheet` + `grab()` (Qt rendering)

Use this when you need an image identical to the desktop app. A
`QApplication` is required even without showing the GUI.

~~~python
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"   # run without a display
from PyQt6.QtWidgets import QApplication
from curlingsheet.sheet import Sheet

app = QApplication([])

sheet = Sheet(show_pochi=False, show_frame=True)
sheet.add_stone([(149, 159, "red"), (120, 300, "yellow")])  # (x, y, team)
sheet.grab().save("out.png")     # same mechanism as the app's image export
~~~

### Route B: `build_sheet_spec` + `render_matplotlib` (no Qt)

Good for script-based image output and figures for papers/slides.
Works **without installing PyQt6**.

Install the optional dependency: `pip install "curlingsheet[mpl]"`.

~~~python
import matplotlib
matplotlib.use("Agg")            # to save without a display
import matplotlib.pyplot as plt
from curlingsheet import build_sheet_spec, SheetOptions
from curlingsheet.renderers.mpl import render_matplotlib

class Stone:  # any object with x, y, team (and optional radius) works
    def __init__(self, x, y, team): self.x, self.y, self.team = x, y, team

spec = build_sheet_spec(
    SheetOptions(show_pochi=False, show_frame=False),
    [Stone(149, 159, "red"), Stone(120, 300, "yellow")],
)
fig, ax = plt.subplots()
render_matplotlib(spec, ax)
fig.savefig("out.png", dpi=100)  # or plt.show()
~~~

### Write your own renderer

A renderer is just a loop over the primitives — no subclassing required.
Colors are `RGBA(r, g, b, a)` with 0–255 channels (`None` means "no fill /
no stroke").

~~~python
from curlingsheet import build_sheet_spec, SheetOptions, Circle, Line, Rect

for shape in build_sheet_spec(SheetOptions()):
    if isinstance(shape, Circle):
        my_canvas.circle(shape.cx, shape.cy, shape.r, shape.fill, shape.stroke)
    elif isinstance(shape, Line):
        my_canvas.line(shape.x1, shape.y1, shape.x2, shape.y2, shape.color)
    elif isinstance(shape, Rect):
        my_canvas.rect(shape.x, shape.y, shape.w, shape.h, shape.fill, shape.stroke)
~~~

Drawing dimensions (house rings, line positions, MD point coordinates) are
centralized in `curlingsheet.geometry` if you need to reference them.

## JSON Format
### Example
~~~json
[
  {
    "x": 2.1049331104,
    "y": 32.1341428571,
    "team": "red"
  },
  {
    "x": -0.0079431438,
    "y": 37.7441008403,
    "team": "yellow"
  },
  ...
]
~~~

- `x` : The horizontal position of the stone (float, range: -2.375 to 2.375)
- `y` : The vertical position of the stone(float, range: 32.004 to 40.234)
- `team` : The team color of the stone (`"red"` of `"yellow"`)

The coordinate system follows the specification used in [DigitalCurling3](https://digitalcurling.github.io/DigitalCurling3/md_coordinate.html).
