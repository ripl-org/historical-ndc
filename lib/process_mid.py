"""
Process 2006 to 2012 files.
"""
import pandas as pd


def read_listings(path):
    if path.endswith("20060516021016.txt"):
        df = pd.read_fwf(
            path,
            widths=[8, 7, 5, 10, 11, 2, 8, 100],
            names=["lookup", "lblcode", "prodcode", "strength", "produnit", "rx_otc", "x", "tradename"],
            header=None,
            dtype=str
        )
    else:
        df = pd.read_fwf(
            path,
            widths=[8, 7, 5, 10, 11, 2, 100],
            names=["lookup", "lblcode", "prodcode", "strength", "produnit", "rx_otc", "tradename"],
            header=None,
            dtype=str
        )
    df["lblcode"] = pd.to_numeric(df["lblcode"], errors="coerce")
    df["prodcode"] = pd.to_numeric(df["prodcode"], errors="coerce")
    df = df.dropna(subset=["lblcode"])
    df = df.dropna(subset=["prodcode"])
    df["lblcode"] = df["lblcode"].astype("int")
    df["prodcode"] = df["prodcode"].astype("int")
    return df


def read_formulation(path):
    return pd.read_fwf(
        path,
        widths=[8, 10, 6, 100],
        names=["lookup", "ai_strength", "ai_unit", "active_ingred"],
        header=None,
        dtype=str
    )


def read_schedule(path):
    return pd.read_fwf(
        path,
        widths=[8, 1],
        names=["lookup", "schedule"],
        header=None,
        dtype=str
    )


def Process(target, source, env):

    listings = []
    formulations = []
    schedules = []

    for path in [f.path for f in source]:
        filetype = path.split("/")[2]
        if filetype == "listings":
            listings.append(read_listings(path))
        elif filetype == "formulat":
            formulations.append(read_formulation(path))
        elif filetype == "schedule":
            schedules.append(read_schedule(path))
        else:
            raise Exception("Unexpected file type: {}".format(filetype))

    # Drugs file
    listings = pd.concat(listings, ignore_index=True).drop_duplicates()
    if schedules:
        schedules = pd.concat(schedules, ignore_index=True).drop_duplicates()
        drugs = listings.merge(schedules, on="lookup", how="left")
    else:
        drugs = listings
        drugs["schedule"] = ""
    drugs["ndc"] = drugs.apply(lambda x: "{:05d}{:04d}".format(x["lblcode"], x["prodcode"]), axis=1)
    drugs["name"] = drugs["tradename"].str.upper()
    drugs.to_csv(target[0].path, columns=["ndc", "name", "schedule"], index=False)

    # Ingredients file
    ingredients = pd.concat(formulations, ignore_index=True)\
                    .drop_duplicates()\
                    .merge(drugs, on="lookup", how="inner")\
                    .rename(columns={"ai_strength": "amount",
                                     "ai_unit": "unit",
                                     "active_ingred": "ingredient"})
    ingredients["ingredient"] = ingredients["ingredient"].str.upper()
    ingredients.to_csv(target[1].path, columns=["ndc", "ingredient", "amount", "unit"], index=False)


# vim: syntax=python expandtab sw=4 ts=4
