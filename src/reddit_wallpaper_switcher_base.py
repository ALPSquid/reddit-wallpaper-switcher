import gui
import threading
import os
import urlparse
import urllib2
import random
import time
import getpass
import shutil
import utils
from bs4 import BeautifulSoup


class RedditWallpaperSwitcherBase(object):

    def __init__(self):
        self.WALLPAPERS_URL = "http://www.reddit.com/r/wallpaper+wallpapers"
        self.PROJECT_PATH = utils.get_app_dir()
        self.IMAGES_PATH = self.PROJECT_PATH+"/files/Images"
        self.TEMP_PATH = self.PROJECT_PATH+"/files/Temp"
        self.ASSETS_PATH = self.PROJECT_PATH+"/assets"
        self.WALLPAPER_PATH = self.PROJECT_PATH+"/files/CurrentWallpaper.png"
        self.APP_USER = getpass.getuser()
        self.SWITCH_INTERVAL = 15 * 60

        self.internet_connection = False
        self.connection_attempt = 1
        self.first_run = True
        self.quit_app = False
        self.threads = []
        self.spaces = ""
        for i in range(75):
            self.spaces += " "

    def run_thread(self, target):
        """
        Run target function in a new thread

        Keyword arguments:
        target -- function to run

        """
        method_thread = threading.Thread(target=target)
        method_thread.start()
        self.threads.append(method_thread)

    def print_line(self, string):
        print("\r"+self.spaces)  # Clear line
        print("\r"+str(string))

    def open_web_page(self, target_url):
        """
        Get BeautifulSoup HTML of target_url

        Keyword arguments:
        target_url -- URL to get source of

        """
        while 1:
            try:
                url_content = urllib2.urlopen(target_url).read()
                soup = BeautifulSoup(''.join(url_content))
                break
            except EnvironmentError as ex:
                #TODO: Handle this
                print("Error opening web page: '"+str(ex)+"'")
                soup = ""
        return soup

    def get_images(self, target_soup, message):
        """
        Download Images from url if it doesn't exit

        Keyword arguments:
        target_soup -- soup to get images from
        message -- informative message to print

        """

        print(message)
        number = 1
        try:
            if not os.path.exists(self.TEMP_PATH):
                os.makedirs(self.TEMP_PATH)
        except OSError as ex:
            #TODO: Handle this
            pass
        try:
            #TODO: Optimisation: filter this further by attribute
            for img in target_soup.findAll("a"):
                try:
                    if((utils.string_contains(img["href"], "i.imgur", ".jpg", ".png"))
                       and (not utils.string_contains(img["href"], "www.", "domain/"))):
                        try:
                            img_url = img["href"]
                            file_name = os.path.basename(urlparse.urlsplit(img_url)[2])
                            if((not os.path.exists(self.IMAGES_PATH+"/"+file_name))
                               and (not os.path.exists(self.TEMP_PATH+"/"+file_name))):
                                self.print_line("Downloading: "+file_name)
                                img_data = urllib2.urlopen(img_url).read()
                                output = open(self.TEMP_PATH+"/"+file_name, "wb")
                                output.write(img_data)
                                output.close()
                                number += 1
                            elif not os.path.exists(self.TEMP_PATH+"/"+file_name):
                                self.print_line("Image %s exists, skipping" % number)
                                shutil.copy(self.IMAGES_PATH+"/"+file_name, self.TEMP_PATH+"/"+file_name)
                                number += 1

                        except EnvironmentError as ex:
                            print("\nError Downloading "+file_name+": Website may be Blocked")
                            print("\nError Downloading "+file_name+": '"+str(ex)+"'")
                except KeyError:
                    pass
        except EnvironmentError as ex:
            print("Error finding images: '"+str(ex)+"'")

    def get_page2(self, target_soup):
        """
        Return the url of subreddit page 2

        Keyword arguments:
        target_soup -- soup of page 1

        """
        try:
            #TODO: Optimisation: filter this further by attribute
            for a in target_soup.findAll("a"):
                try:
                    if self.WALLPAPERS_URL+"/?count=25&after=" in a["href"]:
                        page2_url = a["href"]
                        return page2_url
                except KeyError:
                    pass
        except EnvironmentError as ex:
            utils.log("Error finding images: '"+str(ex)+"'", utils.MsgTypes.ERROR)

    def set_wallpaper(self, file_name):
        """
        Set the OS wallpaper. OS specific, implement in respective class

        Keyword arguments:
        file_name -- file to set as wallpaper
        """
        raise NotImplementedError

    def change_wallpaper(self):
        """
        Pick a random image from /images folder and call set_wallpaper with it
        """
        wallpaper_choice = random.choice(os.listdir(self.IMAGES_PATH))
        self.set_wallpaper(self.IMAGES_PATH+"/"+wallpaper_choice)

    def main_tasks(self):
        """
        Main download and switch workflow
        """
        if not os.path.exists(self.IMAGES_PATH):
            os.makedirs(self.IMAGES_PATH)
        if os.path.exists(self.TEMP_PATH):
            shutil.rmtree(self.TEMP_PATH)
        if self.first_run:
            time.sleep(15)  # Wait for os to connect to the internet (bit of a quick workaround)
            self.first_run = False
        try:
            urllib2.urlopen("http://www.google.com", timeout=5)
            self.internet_connection = True
        except urllib2.URLError:
            utils.log("No Internet Connection", utils.MsgTypes.INFO)
            self.internet_connection = False

        if self.internet_connection:
            soup = self.open_web_page(self.WALLPAPERS_URL)
            self.get_images(soup, "\nDownloading Images from page 1")

            page2_url = self.get_page2(soup)
            soup = self.open_web_page(page2_url)
            self.get_images(soup, "Downloading Images from page 2")
            print("\n")

            try:
                if os.path.exists(self.IMAGES_PATH):
                    shutil.rmtree(self.IMAGES_PATH)
                os.rename(self.TEMP_PATH, self.IMAGES_PATH)
            except EnvironmentError as ex:
                print("Error changing '/files/temp' to '/files/images': '"+str(ex)+"'")
            print("Finished Downloading Images")

        utils.log("Setting Wallpaper", utils.MsgTypes.INFO)
        self.change_wallpaper()

    def schedule(self):
        """
        Automatic background switching process
        """
        while not self.quit_app:
            self.main_tasks()
            for i in range(self.SWITCH_INTERVAL):
                if not self.quit_app:
                    time.sleep(1)
        utils.log("Schedule Finished", utils.MsgTypes.INFO)

    def main(self):
        self.run_thread(self.schedule)
        gui.main(self)
        for thread in self.threads:
            thread.join()

    def setup(self):
        raise NotImplementedError

    def run(self):
        self.setup()
        self.main()