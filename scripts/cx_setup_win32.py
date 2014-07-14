from cx_Freeze import setup, Executable
import sys


base = None
if sys.platform == "win32":
	base = "Win32GUI"

setup(name = "Reddit Wallpaper Switcher",
      version = "0.1.0",
      description = "Downloads wallpapers from /r/wallpaper+wallpapers",
      executables = [Executable("../src/RedditWallpaperSwitcherWin32.py", 
                                base=base,
                                targetName="RedditWallpaperSwitcher.exe",
                                icon="../src/assets/icon.ico")])
