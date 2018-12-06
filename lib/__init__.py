import hashlib
import os
import pandas as pd
import requests
import sys
import zipfile

def mkdir(target):
    dn = os.path.dirname(target)
    if not os.path.exists(dn):
        print("creating directory", dn, file=sys.stderr)
        os.makedirs(dn)

def md5sum(target):
    md5 = hashlib.md5()
    with open(target, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

def md5verify(target, md5):
    print("verifying", target, file=sys.stderr)
    test = md5sum(target)
    if test != md5:
        print("ERROR: MD5 mismatch for", target, file=sys.stderr)
        print("expected:", md5, file=sys.stderr)
        print("found:   ", test, file=sys.stderr)
        sys.exit(1)

def Download(target, source, env):
    target = str(target[0])
    url = str(source[0])
    md5 = str(source[1])
    print("downloading", url, file=sys.stderr)
    mkdir(target)
    with open(target, "wb") as f:
        response = requests.get(url)
        f.write(response.content)
    md5verify(target, md5)

def Unzip(target, source, env):
    target = str(target[0])
    zip_path = str(source[0])
    md5 = str(source[1])
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extract(target.partition("/")[2], "scratch")
    md5verify(target, md5)

def CombineDrugs(target, source, env):
    df = pd.concat([pd.read_csv(f.path, dtype={"ndc": str}) for f in source])
    df.groupby("ndc").max().to_csv(target[0].path, float_format="%g")

def CombineIngredients(target, source, env):
    df = pd.concat([pd.read_csv(f.path, dtype=str) for f in source])
    df.drop_duplicates().to_csv(target[0].path, index=False)

# vim: syntax=python expandtab sw=4 ts=4
