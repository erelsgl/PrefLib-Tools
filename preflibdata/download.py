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

def download_election(subpath, index, subindex_range):
    print("\nDownloading election data {}".format(subpath))
    for subindex in subindex_range:
        download("data/election/"+subpath, "ED-{:05d}-{:08d}.soc".format(index,subindex))


download_election("netflix", 4, range(1,200+1))
download_election("skate", 6, [3,4,7,8,11,12,18,21,22,28,29,32,33,34,35,36,37,44,46,48])
download_election("agh", 9, range(1,2+1))
download_election("web", 11, range(1,3+1))
download_election("shirt", 12, [1])
download_election("sushi", 14, [1])
download_election("cleanweb", 15, range(1,79+1))
download_election("dots", 24, range(1,4+1))
download_election("puzzle", 25, range(1,4+1))
download_election("education", 32, [2])
