from lib import (
    Download, Unzip,
    process_old, process_mid, process_new,
    CombineDrugs, CombineIngredients
)
import os
from pandas import read_csv

env = Environment(ENV=os.environ)
env.Decider("MD5-timestamp")

### Download and unzip bundled Internet Archive data from figshare ###

Snapshots = read_csv("InternetArchive/files.csv")
Snapshots["target"] = Snapshots.apply(lambda x: "scratch/HistoricalNDC-20180411/{filename}/{timestamp}.txt".format(**x), axis=1)
Snapshots["year"] = Snapshots.timestamp.apply(lambda x: int(str(x)[:4]))

env.Command("scratch/HistoricalNDC-20180411.zip",
            [Value("https://ndownloader.figshare.com/files/11054477"),
             Value("3db1cacd9f03ce12d333034b58ed70cc")],
            Download)

for row in Snapshots.itertuples():
    env.Command(row.target,
                ["scratch/HistoricalNDC-20180411.zip",
                 Value(row.MD5)],
                Unzip)

years = sorted(Snapshots.year.unique())

### Process snapshots by year ###

for year in years:
    if (year >= 1998) and (year <= 2005):
        Process = process_old.Process
        sourcefile = "#lib/process_old.py"
    elif (year >= 2006) and (year <= 2010):
        Process = process_mid.Process
        sourcefile = "#lib/process_mid.py"
    elif (year >= 2011) and (year <= 2018):
        Process = process_new.Process
        sourcefile = "#lib/process_new.py"
    else:
        raise Exception("Unknown year")
    Depends(
        env.Command(["scratch/ndc-drugs-{}.csv".format(year),
                     "scratch/ndc-ingredients-{}.csv".format(year)],
                    Snapshots.loc[Snapshots.year == year, "target"].tolist(),
                    Process),
        sourcefile)

### Combine years into a single data set ###

env.Command("output/ndc-drugs.csv",
            ["scratch/ndc-drugs-{}.csv".format(year) for year in years],
            CombineDrugs)

env.Command("output/ndc-ingredients.csv",
            ["scratch/ndc-ingredients-{}.csv".format(year) for year in years],
            CombineIngredients)

### Opioid classification based on ingredient amounts ###

env.Command(["output/ndc-opioids.csv", "output/ndc-opioids.log"],
            ["lib/opioids.py", "output/ndc-ingredients.csv"],
            "python $SOURCES ${TARGETS[0]} > ${TARGETS[1]}")

### Child psychiatric classification based on ingredient list ###

env.Command(["output/ndc-child-psychiatric.csv", "output/ndc-child-psychiatric.log"],
            ["lib/child-psychiatric.py",
             "input/child-psychiatric-ingredients.csv",
             "output/ndc-ingredients.csv",
             "output/ndc-drugs.csv"], 
            "python $SOURCES ${TARGETS[0]} > ${TARGETS[1]}")

# vim: syntax=python expandtab sw=4 ts=4
