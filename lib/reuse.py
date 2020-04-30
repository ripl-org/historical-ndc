import pandas as pd
import re
import sys

drugfiles = sys.argv[1:-1]
outfile   = sys.argv[-1]

def load(filename):
    year = int(re.split("[-\.]", filename)[-2])
    df = pd.read_csv(filename, usecols=["ndc", "name"], dtype={"ndc": str})
    df["year"] = year
    return df

drugs = pd.concat(map(load, drugfiles), ignore_index=True)\
          .groupby(["ndc", "name"])\
          .max()\
          .reset_index()

drugs.groupby("ndc").filter(lambda group: len(group) > 1)\
     .sort_values(["ndc", "year"])\
     .to_csv(outfile, columns=["ndc", "year", "name"], index=False)

# vim: syntax=python expandtab sw=4 ts=4
