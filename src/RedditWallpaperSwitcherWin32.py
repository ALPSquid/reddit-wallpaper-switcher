from RedditWallpaperSwitcherBase import RedditWallpaperSwitcherBase
from win32con import SPI_SETDESKWALLPAPER, SPIF_SENDCHANGE, SPIF_UPDATEINIFILE
from PIL import Image as ImageMain
import _winreg as winreg
import ctypes
import sys
import subprocess
import os


class RedditWallpaperSwitcherWin32(RedditWallpaperSwitcherBase):

    def __init__(self):
        super(RedditWallpaperSwitcherWin32, self).__init__()
        self.STARTUP_REG = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_ALL_ACCESS)

    def set_key(self, name, value):
        winreg.CreateKeyEx(self.STARTUP_REG, name)
        winreg.SetValueEx(self.STARTUP_REG, name, 0, 1, value)

    def set_wallpaper(self, file_name):
        try:
            img = ImageMain.open(file_name)
            destination = r'CurrentWallpaper.bmp'
            img.save(destination)

            SPIF_TELLALL = SPIF_SENDCHANGE | SPIF_UPDATEINIFILE
            ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0,
                                                     os.getcwd()+"\\"+destination, SPIF_TELLALL)
        except IOError as ioe:
            print (str(ioe)+", skipping bmp conversion")
            SPIF_TELLALL = SPIF_SENDCHANGE | SPIF_UPDATEINIFILE
            ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0,
                                                     os.getcwd()+"\\"+file_name, SPIF_TELLALL)

    def add_to_startup(self):
        try:
            STARTUP_REG_CHECK = self.STARTUP_REG
            for i in range(1024):
                n, v, t = winreg.EnumValue(STARTUP_REG_CHECK, i)
                if(n == "Reddit Wallpaper Switcher"):
                    Exists = True
                    if(v != '"'+os.getcwd()+'\\Reddit_Wallpaper_Switcher.exe'+'"'):
                        print os.getcwd()
                        directory = v.rsplit('\\', 1)[0]+'"'
                        try:
                            os.chdir(directory.rsplit('"')[1])
                        except EnvironmentError as ex:
                            print ex
                else:
                    Exists = False
        except EnvironmentError as ex:
            pass
        if(Exists):
            print "[OK] Key Exists"
        else:
            self.set_key('Reddit Wallpaper Switcher', '"'+os.getcwd()+'\\Reddit_Wallpaper_Switcher.exe'+'"')

    def setup(self):
        self.add_to_startup

if(__name__ == "__main__"):
    RWS_Win32 = RedditWallpaperSwitcherWin32()
    RWS_Win32.run()