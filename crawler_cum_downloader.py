import urllib.request
import lxml.html
import sys, os
import shutil

#outfile = open("links.txt",'wb')
media = ["mkv","MKV","MP4","mp4"]
quality = "720p"
searchterm = "Dexter"
chunk_size = 1024*1024  # 1 MBs downloadspeed 

def notify(bytes_so_far, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))
    if bytes_so_far >= total_size:
        sys.stdout.write('\n')    
    
def download(url, display_hook = None):
    if quality not in url:
        return
    response = urllib.request.urlopen(url)
    total_size = int(str(response.info()).split("\n")[2].split(":")[-1])
    bytes_so_far = 0
    outfilename = url.split("/")[-1]
    #sys.stdout.write("Found media -> "+outfilename+"  (SIZE "+str(total_size/(1024*1024))+"M)\n")
    if quality not in url:
        return
    outfp = open(os.path.join(os.getcwd(), outfilename), "wb")
    sys.stdout.write("Downloading file to "+os.path.join(os.getcwd(), outfilename)+"\t...\n")
    while(True):
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)
        if not(chunk):
            break
        sys.stdout.write("\rDownloaded %d of %d bytes (%0.2f%%)" % (bytes_so_far, total_size, float(bytes_so_far*100/total_size)))
        sys.stdout.flush()
        outfp.write(chunk)
    if total_size != bytes_so_far:
        print("Error in downloading! Aborting :(")
        exit(1)
    sys.stdout.write("Found media -> "+outfilename+"  (SIZE "+str(bytes_so_far/(1024*1024))+"M)\n")
    outfp.close()
    return
    
def crawler(url):
    sys.stdout.write("Crawlling @ "+url+"\n")
    if any(x in url for x in media):
        download(url, notify)
        return
    curpath = os.path.join(os.getcwd(), url.split("/")[-2])
    sys.stdout.write("going in dir "+curpath+"\n")
    if not(os.path.exists(curpath)):
        os.makedirs(curpath)
    os.chdir(curpath)
    try:
        website = urllib.request.urlopen(url)
    except Exception as e:
        print(e)
        print("Connection Error! Aborting :(")
        exit(1)
    dom = lxml.html.fromstring(website.read())
    links = []
    for link in dom.xpath('//a/@href'):
        if ".." not in link:
            links.append(link)
    for link in links:
        crawler(url+link)
    os.chdir("..")
    
crawler("http://fastdownloadhub.com/Serial/Dexter/")