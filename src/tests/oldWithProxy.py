from HTMLParser import HTMLParser
import sys, urllib2, urllib, urlparse, Tkinter, os, random, shutil, time, ctypes
from win32con import SPI_SETDESKWALLPAPER, SPIF_SENDCHANGE, SPIF_UPDATEINIFILE
from os.path import basename
from bs4 import BeautifulSoup
from Tkinter import *
import Image as ImageMain
import getpass
import _winreg as winreg
 
textFont1 = ("Arial", 10, "normal")
#username = ''
#password = ''
#proxy_server = '10.12.172.37'
#proxy_port = '8881'
#proxy_realm = proxy_server
#proxy_auth = ":@:"
soup = ""
opener = ""
username = getpass.getuser()
STARTUP_REG = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Run',
        0, winreg.KEY_ALL_ACCESS)
internetConnection = False
attempt = 1
firstRun = True

def setKey(name, value):
    winreg.CreateKeyEx(STARTUP_REG, name)
    winreg.SetValueEx(STARTUP_REG, name, 0, 1, value)

def clearLine():
    spaces = ""
    for i in range(60):
        spaces += " "
    sys.stdout.write(('%s\r' %spaces))
    sys.stdout.flush()
    #time.sleep(5)

def exit():
    pass

def pressedCmdE():
    print "Pressed"

def makeWindow () :
    global userBoxV, passBoxV, win
    
    win = Tk()
    win.protocol("WM_DELETE_WINDOW", exit)

    frame1 = Frame(win, width=250, height=200)
    frame1.pack()

    Label(frame1, text="User Name").grid(row=0, column=0, sticky=W)
    userBoxV = StringVar()
    userBox = Entry(frame1, textvariable=userBoxV)
    userBox.grid(row=0, column=1, sticky=W)

    Label(frame1, text="Password").grid(row=1, column=0, sticky=W)
    passBoxV= StringVar()
    passBox= Entry(frame1, textvariable=passBoxV, show="*")
    passBox.grid(row=1, column=1, sticky=W)

    frame2 = Frame(win)
    frame2.pack()
    b1 = Button(frame2,text=" Save ",command=addEntry)
    b1.pack()
    return win

def addEntry():
    global userBoxV, passBoxV, win, user, password
    win.destroy()
    user = userBoxV.get()
    password = passBoxV.get()
    
 
def checkProxy():
    global proxy_auth, user, password
        
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
        win = makeWindow()
        win.title("Proxy Credentials")
        win.wm_iconbitmap('icon.ico')
        win.mainloop()
        
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
    global opener, attempt, internetConnection
    proxy_handler = urllib2.ProxyHandler({"http": proxySettings})
    opener = urllib2.build_opener(proxy_handler)
    opener.addheaders = [('User-agent', 'Wallpaper changer with /r/wallpapers as source by ALP_Squid')]
    if(attempt <= 3):
        try:
            opener.open("http://www.google.com")
            attempt = 1
            internetConnection = True
        except EnvironmentError as ex:
            if os.path.exists("ProxyConfig.config"):
                os.remove("ProxyConfig.config")
                attempt += 1
                checkProxy()
    else:
        internetConnection = False
        attempt = 1
    #urllib2.install_opener(opener)
    #schedule()
    #print urllib2.urlopen('http://www.reddit.com').read()
    


def openWebPage(targetUrl):
    global soup, proxy
    while True:
        if proxy:
            try:
                urlContent = opener.open(targetUrl).read()
                soup = BeautifulSoup(''.join(urlContent))
                break
            except EnvironmentError as ex:
                print "Error opening web page: '"+str(ex)+"'"
        else:
            try:
                urlContent = urllib2.urlopen(targetUrl).read()
                soup = BeautifulSoup(''.join(urlContent))
                break
            except EnvironmentError as ex:
                print "Error opening web page: '"+str(ex)+"'"
            

def getImages(targetUrl, message):
    global page2URL, proxy
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
                        if(number <= 25):
                            imgUrl = img['href']
                            fileName = basename(urlparse.urlsplit(imgUrl)[2])
                            if((not os.path.exists("images\\"+fileName)) and (not os.path.exists("temp\\"+fileName))):
                                clearLine()
                                sys.stdout.write("\rDownloading: "+fileName)
                                sys.stdout.flush()
                                if proxy:
                                    imgData = opener.open(imgUrl).read()
                                else:
                                    imgData = urllib2.urlopen(imgUrl).read()
                                output = open("temp\\"+fileName,'wb')
                                output.write(imgData)
                                output.close()
                                number+=1
                            elif not os.path.exists("temp\\"+fileName):
                                clearLine()
                                sys.stdout.write("\rImage %s exists, skipping" %number)
                                sys.stdout.flush()
                                shutil.copy("images\\"+fileName, "temp\\"+fileName)
                                number+=1
                        else:
                            sys.stdout.write("Got to end of page")
                            sys.stdout.flush()
                    except EnvironmentError as ex:
                            print "\nError downloading "+fileName+": Website may be Blocked"
                            print "\nError downloading "+fileName+": '"+str(ex)+"'"
                        #pass
    except EnvironmentError as ex:
        print "Error finding images: '"+str(ex)+"'"


def getPage2(targetUrl):
    try:
        for a in soup.findAll('a'):
            try:
                if 'http://www.reddit.com/r/wallpapers/?count=25&after=' in a['href']:
                    page2Url = a['href']
                    return page2Url
            except KeyError:
                pass
    except EnvironmentError as ex:
        print "Error finding images: '"+ex+"'"

    

def setWallpaper(filename):
    try:
        img = ImageMain.open(filename)
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
        time.sleep(15 * 60)

def mainTasks():
    global page2URL, proxy, url, internetConnection, firstRun

    if not os.path.exists("images"):
        os.makedirs("images")

    if(firstRun):
        time.sleep(10)
        firstRun = False

    if(not urllib2.getproxies().get('http')):
        proxy = False
        try:
            urllib2.urlopen("http://www.google.com", timeout=5)
            internetConnection = True
        except urllib2.URLError:
            print "No Internet Connection"
            internetConnection = False
    else:
        print "You seem to be behind a proxy, switching to it"
        proxy = True
        checkProxy()

    if os.path.exists("temp"):
        shutil.rmtree("temp")

    if(internetConnection):
        url = "http://www.reddit.com/r/wallpapers"
        openWebPage(url)
        getImages(url, "\nDownloading Images from page 1")

        print "\n\nGetting Page 2 Link..."
        openWebPage(getPage2(url))
        getImages(getPage2(url), "Downloading Images from page 2\n")
        print "\n"

        try:
            if os.path.exists("images"):
                shutil.rmtree("images")
            os.rename("temp", "images")
        except EnvironmentError as ex:
            print ex

        if os.path.exists("C:\\Users\\%s\\Pictures\\screen saver" % username):
            try:
                shutil.rmtree("C:\\Users\\%s\\Pictures\\screen saver" % username)
            except:
                pass

        try:
            shutil.copytree("images", "C:\\Users\\%s\\Pictures\\screen saver" % username)  
        except EnvironmentError as ex:
            print "Could not save to Screen Saver Folder: "+"'"+str(ex)+"'"
        
    print "\nSetting Wallpaper..."
    wallpaperChoice = random.choice(os.listdir("images"))

    setWallpaper("images\\"+wallpaperChoice)
    
    print "\nFinished Downloading Images"

    


if __name__ == "__main__":
    try:
        STARTUP_REG_CHECK = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r'Software\Microsoft\Windows\CurrentVersion\Run',
                                     0, winreg.KEY_ALL_ACCESS)
        for i in range(1024):
            n, v, t = winreg.EnumValue(STARTUP_REG_CHECK, i)
            if(n == "Reddit Wallpaper Change"):
                Exists = True
                if(v != '"'+os.getcwd()+'\\reddit Wallpaper Switcher.exe'+'"'):
                    print os.getcwd()
                    directory = v.rsplit('\\', 1)[0]+'"'
                    try:
                        os.chdir(directory.rsplit('"')[1])
                    except EnvironmentError as ex:
                        print ex
                    #print "New DIR: "+os.getcwd()
            else:
                Exists = False            
    except EnvironmentError as ex:
        pass
    
    if Exists:
        print "Exits"
    else:
        setKey('Reddit Wallpaper Change', '"'+os.getcwd()+'\\reddit Wallpaper Switcher.exe'+'"')
        #print "Doesn't Exists"

    schedule()


