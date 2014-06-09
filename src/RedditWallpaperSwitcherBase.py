from bs4 import BeautifulSoup
import GUI
import threading
import urlparse
import os
import urllib2
import random
import time
import getpass
import shutil


class RedditWallpaperSwitcherBase(object):

    def __init__(self):
        # ---- Variables
        self.WALLPAPERS_URL = "http://www.reddit.com/r/wallpaper+wallpapers"
        self.PROJECT_PATH = self.get_app_dir()
        self.IMAGES_PATH = self.PROJECT_PATH+"/files/Images"
        self.TEMP_PATH = self.PROJECT_PATH+"/files/Temp"
        self.ASSETS_PATH = self.PROJECT_PATH+"/assets"
        self.WALLPAPER_PATH = self.PROJECT_PATH+"/files/CurrentWallpaper.png"
        self.APP_USER = getpass.getuser()
        self.SWITCH_INTERVAL = 15*60
        self.internet_connection = False
        self.connection_attempt = 1
        self.first_run = True
        self.quit_app = False
        self.threads = []
        self.soup = None

        self.spaces = ""
        for i in range(75):
            self.spaces += " "
        # ----

    def run_thread(self, target):
        """
        Run target function in a new thread

        Keyword arguments:
        target -- function to run

        """
        method_thread = threading.Thread(target=target)
        method_thread.start()
        self.threads.append(method_thread)

    def get_app_dir(self):
        """
        Return the app directory
        """
        path = os.path.dirname(__file__)
        if(".zip" in path):
            path, zip = os.path.split(path)
        return path

    def print_line(self, string):
        """
        Print to same line

        Keyword arguments:
        string -- String to print

        """
        print("\r"+self.spaces)  # Clear line
        print("\r"+str(string))

    def string_contains(self, string, *substrings):
        """
        Check if string contains all substrings

        Keyword arguments:
        string -- string to check
        substrings -- strings to find

        """
        for substring in substrings:
            if(substring in string):
                return True
        return False

    def open_web_page(self, target_url):
        """
        Get BeautifulSoup HTML of page

        Keyword arguments:
        target_url -- URL to get source of

        """
        while 1:
            try:
                url_content = urllib2.urlopen(target_url).read()
                self.soup = BeautifulSoup(''.join(url_content))
                break
            except EnvironmentError as ex:
                print("Error opening web page: '"+str(ex)+"'")

    def get_images(self, target_url, message):
        """
        Download Images from url if it doesn't exit

        Keyword arguments:
        target_url -- URL to get images from
        message -- informative message to print

        """
        print(message)
        number = 1
        try:
            if(not os.path.exists(self.TEMP_PATH)):
                os.makedirs(self.TEMP_PATH)
        except:
            pass
        try:
            for img in self.soup.findAll("a"):
                try:
                    if((self.string_contains(img["href"], "i.imgur", ".jpg", ".png"))
                       and (not self.string_contains(img["href"], "www.", "domain/"))):
                        try:
                            # if(number <= 25):
                            # else: print("Got to end of page")
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
                            elif(not os.path.exists(self.TEMP_PATH+"/"+file_name)):
                                self.print_line("Image %s exists, skipping" %number)
                                shutil.copy(self.IMAGES_PATH+"/"+file_name, self.TEMP_PATH+"/"+file_name)
                                number += 1

                        except EnvironmentError as ex:
                            print("\nError Downloading "+file_name+": Website may be Blocked")
                            print("\nError Downloading "+file_name+": '"+str(ex)+"'")
                except KeyError:
                    pass
        except EnvironmentError as ex:
            print("Error finding images: '"+str(ex)+"'")

    def get_page2(self, target_url):
        """
        Return the url of subreddit page 2

        Keyword arguments:
        target_url -- URL of page 1

        """
        try:
            for a in self.soup.findAll("a"):
                try:
                    if(self.WALLPAPERS_URL+"/?count=25&after=" in a["href"]):
                        page2_url = a["href"]
                        return page2_url
                except KeyError:
                    pass
        except EnvironmentError as ex:
            print("Error finding images: '"+str(ex)+"'")

    def set_wallpaper(self, file_name):
        """
        Set the OS wallpaper. OS specific

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
        if(not os.path.exists(self.IMAGES_PATH)):
            os.makedirs(self.IMAGES_PATH)
        if(os.path.exists(self.TEMP_PATH)):
            shutil.rmtree(self.TEMP_PATH)
        if(self.first_run):
            #TODO: this
            time.sleep(15)  # Wait for os to connect to internet
            self.first_run = False
        try:
            urllib2.urlopen("http://www.google.com", timeout=5)
            self.internet_connection = True
        except urllib2.URLError:
            print("No Internet Connection")
            self.internet_connection = False
        ##
        if(self.internet_connection):
            self.open_web_page(self.WALLPAPERS_URL)
            self.get_images(self.WALLPAPERS_URL, "\nDownloading Images from page 1")

            page2_url = self.get_page2(self.WALLPAPERS_URL)
            self.open_web_page(page2_url)
            self.get_images(page2_url, "Downloading Images from page 2")
            print("\n")

            try:
                if(os.path.exists(self.IMAGES_PATH)):
                    shutil.rmtree(self.IMAGES_PATH)
                os.rename(self.TEMP_PATH, self.IMAGES_PATH)
            except EnvironmentError as ex:
                print("Error changing '/files/temp' to '/files/images': '"+str(ex)+"'")
            print("Finished Downloading Images")

        print("Setting Wallpaper")
        self.change_wallpaper()


    def schedule(self):
        """
        Automatic background switching process
        """
        while(not self.quit_app):
            self.main_tasks()
            for i in range(self.SWITCH_INTERVAL):
                if(not self.quit_app):
                    time.sleep(1)
        print("Schedule Finished")

    def main(self):
        self.run_thread(self.schedule)
        GUI.main(self)
        for thread in self.threads:
            thread.join()

    def setup(self):
        raise NotImplementedError

    def run(self):
        self.setup()
        self.main()