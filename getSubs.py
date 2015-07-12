from BeautifulSoup import BeautifulSoup
import urllib2
import socket
import sys
import os
from string import split
import re
import urllib
import zipfile
import pprint

HEADERS = {"User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5",
       "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language" : "ru,en-us;q=0.7,en;q=0.3",
       "Accept-Charset" : "windows-1251,utf-8;q=0.7,*;q=0.7",
       "Accept-Encoding" : "identity, *;q=0",
       "Connection" : "Keep-Alive"}
PROXY=None
timeout=60
ROOTURL = "http://subscene.com"
SEARCHURL = "/subtitles/release?q="
def levenshtein(s, t):
    ''' From Wikipedia article; Iterative with two matrix rows. '''
    if s == t: return 0
    elif len(s) == 0: return len(t)
    elif len(t) == 0: return len(s)
    v0 = [None] * (len(t) + 1)
    v1 = [None] * (len(t) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]
    
    return v1[len(t)]

def parsePage(pageStr):
    print pageStr
    slovar={}
    global timeout
    socket.setdefaulttimeout(timeout)
    if PROXY is not None:
            proxy_handler = urllib2.ProxyHandler( { "http": "http://"+PROXY+"/" } )
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
    page_request = urllib2.Request(url=pageStr, headers=HEADERS)
    try:
        page_zapr = urllib2.urlopen(url=page_request)
#         print "Page reading ... %s"
        page=page_zapr.read()
    except Exception ,error:
        print str(error)
        res=False
        return res,slovar
    soup = BeautifulSoup(page)
    return soup

def parse_page_subs(subStr):
    subStr = re.sub('[^a-zA-Z0-9]', ' ', subStr)
    relevant = ""
    openURL = ROOTURL + SEARCHURL + urllib.quote_plus(subStr)
#     print openURL
    #openURL = "http://subscene.com/subtitles/release?q=jurrasic.park"
    soup = parsePage(openURL)
    minDist = len(subStr)
    for link in soup.findAll('a'): # find all links
        internalCheckSub = link['href'][:4]
        if not internalCheckSub == "http" and "english" in link['href']:
            nameOfSubs = link("span")[1](text=True)[0].strip()
            nameOfSubs = re.sub('[^a-zA-Z0-9]', ' ', nameOfSubs)
            distCurr = levenshtein(nameOfSubs, subStr)
            if(distCurr < minDist):
                relevant= link['href']
                minDist = distCurr
#             pprint.pprint(link)
#             print link['href']
#             print(link("span")[1](text=True)[0])
    return relevant

def getSubsFrom(pageStr, saveDir):
    soup1 = parsePage(pageStr)
#     pprint.pprint(soup)
    titleLink = soup1.find("a", {"id": "downloadButton"})
    pprint.pprint(titleLink['href'])
    url = ROOTURL + titleLink['href']

    file_name = saveDir + url.split('/')[-1] + ".zip"
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
    
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    
    f.close()
    zfile = zipfile.ZipFile(file_name)
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        print (dirname, filename)
        print "Decompressing " + filename + " on " + saveDir
#         if not os.path.exists(dirname):
#             os.makedirs(dirname)
        zfile.extract(name, saveDir)
    os.remove(file_name)

def populateToParseList(fileName, getSubsFor, mediaFilesArray):
    mediatype = fileName.split('.')[-1]
    if mediatype in mediaFilesArray:
        getSubsFor.append(fileName.split('/')[-1])

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
saveInDir = toParse[:toParse.rfind('/')+1]
# print saveInDir
for singleSub in getSubsFor:
    subsOnPage = parse_page_subs(singleSub)
    subsOnURL = ROOTURL + subsOnPage
    getSubsFrom(pageStr=subsOnURL, saveDir=saveInDir)
    