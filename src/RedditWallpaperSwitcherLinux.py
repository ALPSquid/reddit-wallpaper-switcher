from RedditWallpaperSwitcherBase import RedditWallpaperSwitcherBase
from gi.repository import Gio
from PIL import Image as ImageMain
import sys
import subprocess
import os


class RedditWallpaperSwitcherLinux(RedditWallpaperSwitcherBase):

    def __init__(self):
        super(RedditWallpaperSwitcherLinux, self).__init__()
        self.GSETTINGS_SCHEMA = "org.gnome.desktop.background"
        self.GSETTINGS_KEY = "picture-uri"

    def set_wallpaper(self, file_name):
        try:
            image = ImageMain.open(file_name)
            destination = self.WALLPAPER_PATH
            image.save(destination)

            file_path = os.path.abspath(destination).replace(" ", "%20")
            gsettings = Gio.Settings.new(self.GSETTINGS_SCHEMA)
            print gsettings.set_string(self.GSETTINGS_KEY, "file://"+file_path)
            gsettings.apply()
            print(gsettings.get_string(self.GSETTINGS_KEY))
            #cmd = ["gsettings","set", "org.gnome.desktop.background", "picture-uri", "file://"+file_path]
            #subprocess.call(cmd)
            #os.system("gsettings set org.gnome.desktop.background picture-uri " +"'"+file_path+"'")

        except IOError as ioe:
            print (str(ioe)+", error setting wallpaper")


    def get_superuser(self):
        euid = os.geteuid()
        if euid != 0:
            args = ['sudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('sudo', *args)


    def setup(self):
        self.get_superuser()

if(__name__ == "__main__"):
    RWS_Linux = RedditWallpaperSwitcherLinux()
    RWS_Linux.run()
