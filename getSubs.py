from BeautifulSoup import BeautifulSoup
import urllib2
import socket
import sys
import os
from string import split
import re
import urllib
import pprint

HEADERS = {"User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5",
       "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language" : "ru,en-us;q=0.7,en;q=0.3",
       "Accept-Charset" : "windows-1251,utf-8;q=0.7,*;q=0.7",
       "Accept-Encoding" : "identity, *;q=0",
       "Connection" : "Keep-Alive"}
PROXY=None
timeout=60
SEARCHURL = "http://subscene.com/subtitles/release?q="

def parse_page_subs(page_str_about):
    page_str_about = re.sub('[^a-zA-Z0-9]', ' ', page_str_about)
    slovar={}
    global timeout
    socket.setdefaulttimeout(timeout)
    if PROXY is not None:
            proxy_handler = urllib2.ProxyHandler( { "http": "http://"+PROXY+"/" } )
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
    openURL = SEARCHURL+urllib.quote_plus(page_str_about)
    print openURL
    #openURL = "http://subscene.com/subtitles/release?q=jurrasic.park"
    page_request = urllib2.Request(url=openURL, headers=HEADERS)
    try:
        page_zapr = urllib2.urlopen(url=page_request)
        print "Page reading ... %s"
        page=page_zapr.read()
    except Exception ,error:
        print str(error)
        res=False
        return res,slovar
    soup = BeautifulSoup(page)
    relevant = []
    for link in soup.findAll('a'): # find all links
        internalCheckSub = link['href'][:4]
        if not internalCheckSub == "http" and "english" in link['href']:
            relevant.append((link['href'],link("span")[1](text=True)[0]))
#             pprint.pprint(link)
#             print link['href']
            print(link("span")[1](text=True)[0])

def populateToParseList(fileName, getSubsFor, mediaFilesArray):
    splitName = split(fileName,'.')
    mediatype = splitName[len(splitName)-1]
    if mediatype in mediaFilesArray:
        fileDirectoryArray = split(fileName,'/')
        getSubsFor.append(fileDirectoryArray[len(fileDirectoryArray)-1])

getSubsFor = []
mediaFilesArray = ["mp4", "mkv", "avi"]
toParse = sys.argv[1]
if os.path.isdir(toParse):
    contents = os.listdir(toParse)
    for fname in contents:
        if not os.path.isdir(fname):
            populateToParseList(fname, getSubsFor, mediaFilesArray)
else:
    populateToParseList(toParse, getSubsFor, mediaFilesArray)

for singleSub in getSubsFor:
    parse_page_subs(singleSub)