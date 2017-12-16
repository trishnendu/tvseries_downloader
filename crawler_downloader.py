import urllib.request
import lxml.html
import sys, os, time
import shutil

#outfile = open("links.txt",'wb')
media = ["mkv","MKV","MP4","mp4"]
quality = "720p"
chunk_size = 256*1024   

class http_response_message:
    def __init__(self, response):
        self.dict = {}
        if type(response) is not str:
            response = str(response)
        for line in response.split("\n"):
            fields = line.split(":")
            if len(fields) == 2:
                self.dict[fields[0]] = fields[1]
        
def notify(bytes_so_far, total_size, time = None):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    if time:
        sys.stdout.write("Downloaded %0.2f Mbytes of %0.2f Mbytes (%0.2f%%)\tSpeed = %0.2f MBps\r" % (float(bytes_so_far/(1024*1024)), float(total_size/(1024*1024)), percent, float(1/time)))
    else:
        sys.stdout.write("Downloaded %0.2f Mbytes of %0.2f Mbytes (%0.2f%%) \r" % (float(bytes_so_far/(1024*1024)), float(total_size/(1024*1024)), percent))
    if bytes_so_far >= total_size:
        sys.stdout.write('\n')    
    
def download(url, display_hook = None):
    if quality not in url:
        return
    response = urllib.request.urlopen(url)
    message = http_response_message(response.info())
    total_size = int(message.dict["Content-Length"])
    bytes_so_far = 0
    outfilename = url.split("/")[-1]
    #sys.stdout.write("Found media -> "+outfilename+"  (SIZE "+str(total_size/(1024*1024))+"M)\n")
    if quality not in url:
        return
    outfilename = os.path.join(os.getcwd(), outfilename)
    if os.path.exists(outfilename) and os.path.getsize(outfilename) == total_size:
        sys.stdout.write(outfilename+" already downloaded, skipping... \n")
        return
    outfp = open(os.path.join(os.getcwd(), outfilename), "wb")
    sys.stdout.write("Downloading file to "+os.path.join(os.getcwd(), outfilename)+"\t...\n")
    starttime = time.time()
    while(True):
        ts = time.time()
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)
        if not(chunk):
            break
        notify(bytes_so_far, total_size, time.time() - ts)
        #sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%) -> " % (bytes_so_far, total_size, float(bytes_so_far*100/total_size)))
        #sys.stdout.write(os.path.join(os.getcwd(), outfilename)+"\n" )
        outfp.write(chunk)
    if total_size != bytes_so_far:
        print("Error in downloading! Aborting :(")
        exit(1)
    sys.stdout.write("Download "+str(float(total_size/(1024*1024)))+" MB in "+str(float(time.time()-starttime)/60)+" Min complete :) -> "+os.path.join(os.getcwd(), outfilename)+"\n" )
    outfp.close()
    return
    
def crawler(url, download_content = False, crawl_depth = float('inf')):
    if crawl_depth < 0:
        return
    sys.stdout.write("Crawlling @ "+url+"\n")
    if any(x in url for x in media):
        if(download_content):
            download(url, notify)
        else:
            sys.stdout.write("Found media -> "+url+"\n")
        return
    if(download_content):
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
        crawler(url+link, download_content = download_content, crawl_depth = crawl_depth - 1)
    if(download_content): os.chdir("..")

os.chdir(os.path.join(os.getcwd(),"Dexter"))    
crawler("http://fastdownloadhub.com/Serial/Dexter/S02/", download_content = True)