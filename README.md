# CurlingSheet
Run the following commands in the Windows Command Prompt (cmd.exe).

## Environment
- Python 3.12.x

## How to Use
### Clone this Repository
~~~cmd
git clone https://github.com/szmrki/CurlingSheet.git
cd CurlingSheet
~~~

### Create virtual environment
~~~cmd
python -m venv .venv
.venv\Scripts\activate.bat
(.venv) pip install -r requirements.txt
~~~

### Create exe file
~~~cmd
pyinstaller main.spec
~~~
Open the "dist" folder and you should see the "Curling Sheet.exe" file.