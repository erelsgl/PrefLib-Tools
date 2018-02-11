#!python3

"""
Download some of the PrefLib files from PrefLib.org.

"""

import urllib.request, os

BASE = "http://www.preflib.org"

def download(path, filename):
    url = BASE+"/"+path+"/"+filename
    if not os.path.isfile(filename) or os.path.getsize(filename)==0:
        print("Downloading from {} to {}".format(url,filename))
        urllib.request.urlretrieve(url, filename)

def download_matching(subpath, index, subindex_range, extension):
    print("\nDownloading election data {}".format(subpath))
    for subindex in subindex_range:
        download("data/matching/"+subpath, "MD-{:05d}-{:08d}.{}".format(index,subindex,extension))

download_matching("csconf", 2, range(1,3+1), "toi")
download_matching("project", 3, range(1,8+1), "soi")
download_matching("project", 3, range(1,8+1), "toc")
download_matching("aamas", 4, range(1,2+1), "toi")
