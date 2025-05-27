# CurlingSheet
Run the following commands in the Windows.

## System Requirements
- Windows11
- Python 3.12.x
- Display resolution: **at least 945 pixels in height**
    > Note: The application window height is fixed at 945 pixels.
    > If your screen resolution is high enough but the entire application window is not fully visible, 
    please check the [display settings](#display-settings) section at the end of this document. 

## How to Use
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

Open the "dist" folder and you should see the "CurlingSheet.exe" file.  
You can remove "build" folder.

### Display Settings
Follow these steps to disable DPI scaling on Windows for the application executable:

1. Right-click the ".exe" file and select **Properties**.
1. Go to the **Compatibility** tab.
1. Click **Change high DPI settings**.
1. Check **Override high DPI scaling behavior** and select **Application** from the dropdown.