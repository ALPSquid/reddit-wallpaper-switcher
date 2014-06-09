from reddit_wallpaper_switcher_base import RedditWallpaperSwitcherBase
from gi.repository import Gio
from PIL import Image as ImageMain
import sys
import os
import utils


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

              # Still trying to work out the best way of doing this.
              # Sometimes the wallpaper doesn't refresh on Gnome
            file_path = os.path.abspath(destination).replace(" ", "%20")
            gsettings = Gio.Settings.new(self.GSETTINGS_SCHEMA)
            utils.log(gsettings.set_string(self.GSETTINGS_KEY, "file://"+file_path), utils.MsgTypes.INFO)
            gsettings.apply()
            utils.log(gsettings.get_string(self.GSETTINGS_KEY), utils.MsgTypes.INFO)
            #cmd = ["gsettings","set", "org.gnome.desktop.background", "picture-uri", "file://"+file_path]
            #subprocess.call(cmd)
            #os.system("gsettings set org.gnome.desktop.background picture-uri " +"'"+file_path+"'")

        except IOError as ioe:
            utils.log(str(ioe)+", error setting wallpaper", utils.MsgTypes.ERROR)

    def get_superuser(self):
        euid = os.geteuid()
        if euid != 0:
            args = ['sudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('sudo', *args)

    def setup(self):
        # self.get_superuser()
        pass

if __name__ == "__main__":
    RWS_Linux = RedditWallpaperSwitcherLinux()
    RWS_Linux.run()
