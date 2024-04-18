import ctypes
import os
import pathlib
import subprocess
PATH = str(pathlib.Path(__file__).parent.absolute())

# TODO: Check
ctypes.windll.user32.SystemParametersInfoW(20, 0, PATH + '\\default_assets\\default_win10.jpg', 0)

os.startfile('panic.bat')
# subprocess.run("taskkill /F /IM python3.11.exe")