from HTMLParser import HTMLParser
import sys, urllib2, urllib, urlparse, Tkinter, os, random, Image, shutil, time, ctypes
from win32con import SPI_SETDESKWALLPAPER, SPIF_SENDCHANGE, SPIF_UPDATEINIFILE
from os.path import basename
from bs4 import BeautifulSoup
 
textFont1 = ("Arial", 10, "normal")
username = ''
password = ''
proxy_server = '10.12.172.37'
proxy_port = '8881'
proxy_realm = proxy_server
proxy_auth = ":@:"
soup = ""
 
class EntryWidget(Tkinter.Entry):
    def __init__(self, master, initial=""):
        Tkinter.Entry.__init__(self, master=master)
        self.value = Tkinter.StringVar()
        self.config(textvariable=self.value, width=15,
                    relief="sunken", font=textFont1,
                    bg="#eee", fg="#000",
                    justify='center',
                    show="*")
        self.pack()
        self.value.set(initial)
 
class App(Tkinter.Tk):
    global proxy_auth
    def __init__(self, title="Proxy Password"):
        
        if(os.path.exists("ProxyConfig.config")):
            try:
                ProxyConfig = open('ProxyConfig.config', 'r')
                lines = ProxyConfig.readlines()
                user1 = lines[0].split('\n')
                password = lines[1]
                user = user1[0]
            except EnvironmentError as ex:
                print "Error reading config file: "+str(ex)
            finally:
                ProxyConfig.close()
        else:
            userTemp = raw_input('Proxy Username: ')
            user = "guilsborough\\"+userTemp
            Tkinter.Tk.__init__(self)
            self.title(title)
            self.w = EntryWidget(self)
            self.mainloop()
            password = self.w.value.get()
            ProxyConfig = open('ProxyConfig.config', 'w')
            ProxyConfig.write(user + '\n' + password)
            ProxyConfig.close()

        #print user, password
         
        proxy_auth = "%s:%s@%s:%s" % (user,
                                     password,
                                     proxy_server,
                                     proxy_port)
        setupProxy(proxy_auth)

def setupProxy(proxySettings):
    proxy_handler = urllib2.ProxyHandler({"http": proxySettings})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
    schedule()
    #print urllib2.urlopen('http://www.reddit.com').read()
    


def openWebPage(targetUrl):
    global soup
    while True:
        try:
            urlContent = urllib2.urlopen(targetUrl).read()
            soup = BeautifulSoup(''.join(urlContent))
            break
        except EnvironmentError as ex:
            print "Error opening web page: '"+str(ex)+"'"
            

def getImages(targetUrl, message):
    global page2URL
    print message
    number = 1
    try:
        if not os.path.exists("temp"):
            os.makedirs("temp")
    except:
        pass
    try:
        for div in soup.findAll('div'):
            for img in div.findAll('a'):
                if (('i.imgur' in img['href']) or '.jpg' in img['href']) and ('www.' not in img['href']):
                    try:
                        imgUrl = img['href']
                        #THIS AFTER!!!!! CHECK DATA
                        #Seperate file to change wallpaper?
                        fileName = basename(urlparse.urlsplit(imgUrl)[2])
                        if((not os.path.exists("images\\"+fileName)) and (not os.path.exists("temp\\"+fileName))):
                            sys.stdout.write("\rDownloading: "+fileName)
                            sys.stdout.flush()
                            imgData = urllib2.urlopen(imgUrl).read()
                            output = open("temp\\"+fileName,'wb')
                            output.write(imgData)
                            output.close()
                            number+=1
                        elif not os.path.exists("temp\\"+fileName):
                            sys.stdout.write("\rImage %s exists, skipping" %number)
                            sys.stdout.flush()
                            shutil.copy("images\\"+fileName, "temp\\"+fileName)
                            number+=1
                    except EnvironmentError as ex:
                        print "Error downloading Image: '"+str(ex)+"'"
                        pass
    except EnvironmentError as ex:
        print "Error finding images: '"+str(ex)+"'"


def getPage2(targetUrl):
    try:
        for div in soup.findAll('div'):
            for ps in div.findAll('p'):
                for a in ps.findAll('a'):
                    if 'http://www.reddit.com/r/wallpapers/?count=25&after=' in a['href']:
                        page2Url = a['href']
                        return page2Url
    except EnvironmentError as ex:
        print "Error finding images: '"+ex+"'"

    

def setWallpaper(filename):
    try:
        img = Image.open(filename)
        destination = r'CurrentWallpaper.bmp'
        img.save(destination)

        SPIF_TELLALL = SPIF_SENDCHANGE | SPIF_UPDATEINIFILE
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0,
                                                 os.getcwd()+"\\"+destination, SPIF_TELLALL)
    except IOError as ioe:
        print (str(ioe)+", skipping bmp conversion")
        SPIF_TELLALL = SPIF_SENDCHANGE | SPIF_UPDATEINIFILE
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0,
                                                 os.getcwd()+"\\"+filename, SPIF_TELLALL)

def schedule():
    while True:
        mainTasks()
        time.sleep(5 * 60)

def mainTasks():
    global url
    global page2URL

    try:
        urllib2.urlopen("http://www.google.com")
        proxy = False
    except IOError:
        print "You seem to be behind a proxy, switching to it"
        proxy = True
        
    if proxy:
        app = App()

    if os.path.exists("temp"):
        shutil.rmtree("temp")

    url = "http://www.reddit.com/r/wallpapers"
    openWebPage(url)
    getImages(url, "\nDownloading Images from page 1")

    print "\n\nGetting Page 2 Link..."
    openWebPage(getPage2(url))
    getImages(getPage2(url), "Downloading Images from page 2\n")

    try:
        if os.path.exists("images"):
            shutil.rmtree("images")
        os.rename("temp", "images")
    except EnvironmentError as ex:
        print ex
        

    print "\nSetting Wallpaper..."
    wallpaperChoice = random.choice(os.listdir("images"))

    setWallpaper("images\\"+wallpaperChoice)
    
    print "\nFinished Downloading Images"

    


if __name__ == "__main__":
    schedule()


