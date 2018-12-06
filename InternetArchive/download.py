"""
"""

import csv
import hashlib
import pycurl
import os
import shutil
import sys
import time
import tempfile
import zipfile

curl = pycurl.Curl()
files = []

def mkdir(target):
    dn = os.path.dirname(target)
    if not os.path.exists(dn):
        print("creating directory", dn)
        os.makedirs(dn)

def md5sum(target):
    md5 = hashlib.md5()
    with open(target, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def Timestamps(filename):
    """
    Read in the timestamps file for `filename`.
    """
    with open(os.path.join("timestamps", filename + ".txt")) as f:
        lines = f.readlines()
    return map(str.rstrip, lines)


def Download(target, url):
    """
    Download the file at `url` to `target`.
    """
    if os.path.exists(target):
        print("found", target)
    else:
        mkdir(target)
        print("downloading", url)
        curl.setopt(curl.URL, url)
        curl.setopt(curl.FOLLOWLOCATION, True)
        with open(target, "wb") as f:
            curl.setopt(curl.WRITEDATA, f)
            curl.perform()


def Unzip(zipname, ts):
    """
    Unzip the zip file, append the timestamp `ts` to the file names, and
    move them to the snapshots directory.
    """
    tmpdir = tempfile.mkdtemp()
    print("unzipping", zipname, "to", tmpdir, file=sys.stderr)

    try:
        with zipfile.ZipFile(zipname, "r") as z:
            z.extractall(tmpdir)
    except zipfile.BadZipFile:
        print("WARNING: bad zip file", zipname, file=sys.stderr)

    for filename in ["drugclas", "formulat", "listings", "schedule", "product"]:
        variants = [filename + ".txt", filename + ".TXT", filename.upper() + ".TXT"]
        for v in variants:
            source = os.path.join(tmpdir, v)
            if os.path.exists(source):
                target = os.path.join("snapshots", filename, ts + ".txt")
                if os.path.exists(target):
                    print("found", target, file=sys.stderr)
                else:
                    print("copying", source, "to", target, file=sys.stderr)
                    mkdir(target)
                    shutil.copyfile(source, target)
                files.append([filename, ts, md5sum(target)])
                break

    shutil.rmtree(tmpdir)
        

if __name__ == "__main__":

    # load list of Wayback Machine timestamps for each filename
    for filename in ["drugclas", "formulat", "listings"]:

        # download the corresponding file for each filename and timestamp
        for ts in Timestamps(filename):
            target = os.path.join("data", fn, ts + ".txt")
            download(target,
                     "https://web.archive.org/web/{}/http://www.fda.gov/cder/ndc/{}.txt".format(ts, fn))
            files.append([fn, ts, md5sum(target)])

    # load list of Wayback Machine timestamps for each zip filename
    for fn in ["ziptext.zip", "ziptext.exe", "UCM070838.zip", "ndc.zip", "ndctext.zip"]:

        # download the corresponding zip file for each filename and timestamp,
        # and extract the relevant files from the zip
        for ts in timestamps(fn):
            zn = os.path.join("zips", ts + "." + fn)
            url = "https://web.archive.org/web/{}/".format(ts)
            if fn == "UCM070838.zip":
                url += "http://www.fda.gov/downloads/Drugs/DevelopmentApprovalProcess/UCM070838.zip"
            elif fn == "ndc.zip":
                url += "http://www.accessdata.fda.gov/cder/ndc.zip"
            elif fn == "ndctext.zip":
                url += "https://www.accessdata.fda.gov/cder/ndctext.zip"
            else:
                url += "http://www.fda.gov/cder/ndc/{}".format(fn)
            Download(zn, url)
            Unzip(ts, zn)

    # download the current NDC directory
    zn = os.path.join("zips", "current"),
    url = "https://www.accessdata.fda.gov/cder/ndctext.zip")
    ts = time.strftime("%Y%m%d%H%M%S")
    Download(zn, url)
    Unzip(ts, zn)

    # write out csv of filenames, timestamps, and MD5 hashes
    with open("files.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "timestamp", "MD5"])
        for row in files:
            writer.writerow(row)

