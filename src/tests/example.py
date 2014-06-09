import urllib2, urlparse
import os
from os.path import basename
from bs4 import BeautifulSoup

def openWebPage(targetUrl):
    while True:
        try:
            urlContent = urllib2.urlopen(targetUrl).read()
            soup = BeautifulSoup(''.join(urlContent))
            break
        except:
            print "Error opening web page"

def getImages(targetUrl, message):    
    print message
    try:
        for div in soup.findAll('div'):
            for img in div.findAll('a'):
                if ('i.imgur' in img['href']) and ('www.' not in img['href']):
                    try:
                        imgUrl = img['href']
                        imgData = urllib2.urlopen(imgUrl).read()
                        fileName = basename(urlparse.urlsplit(imgUrl)[2])
                        if not os.path.exists("images"):
                            os.makedirs("images")
                        output = open("images\\"+fileName,'wb')
                        output.write(imgData)
                        output.close()
                    except EnvironmentError as ex:
                        print "Error downloading Image: '"+ex+"'"
                        pass
    except EnvironmentError as ex:
        print "Error finding images: '"+ex+"'"

if __name__ == '__main__':  
    url = "http://www.reddit.com/r/wallpapers"
    openWebPage(url)
    getImages(url)

    url+="/?count=25&after=t3_13ee06"
    openWebPage(url)
    getImages(url)
    
    print "Finished Downloading Images"
