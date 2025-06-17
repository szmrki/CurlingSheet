# CurlingSheet

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
- Python 3.12.x
- Display resolution: **at least 945 pixels in height**
    > Note: The application window height is fixed at 945 pixels.
    > If your screen resolution is high enough but the entire application window is not fully visible, 
    please check the [Display Settings](#display-settings) section. 

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
(.venv) pip install -r requirements.txt
~~~

### Test
~~~cmd
python main.py
~~~

### Create .exe File
~~~cmd
pyinstaller main.spec
~~~

Open the `dist` folder and you should see the `CurlingSheet.exe` file. This is the latest vesion. 
You can remove `build` folder.

### Display Settings
Follow these steps to set display scalling to 100% for the application executable:

1. Right-click on your desktop and select **Display settings**.
1. Scroll down to the **Scale & layout** section.
1. Under **Scale**, select **100%** from the dropdown.
>Note: Changing the scaling setting affects the entire system. 
You may want to restore your display scaling to the recommended setting after closing the app.

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