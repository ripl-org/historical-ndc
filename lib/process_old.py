"""
Process 1996 to 2005 files.
"""
import pandas as pd


def read_listings(path):
    df = pd.read_fwf(
        path,
        widths=[10, 6, 4, 10, 10, 1, 25, 7, 100],
        names=["lookup", "lblcode", "prodcode", "strength", "produnit", "rx_otc", "dosage", "firm_no", "tradename"],
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


def read_class(path):
    return pd.read_fwf(
        path,
        widths=[10, 4, 52],
        names=["lookup", "prod_class_no", "drug_class"],
        header=None,
        dtype=str
    )


def read_formulation(path):
    return pd.read_fwf(
        path,
        widths=[10, 10, 5, 100],
        names=["lookup", "ai_strength", "ai_unit", "active_ingred"],
        header=None,
        dtype=str
    )


def Process(target, source, env):

    listings = []
    classes = []
    formulations = []

    for path in [f.path for f in source]:
        filetype = path.split("/")[2]
        if filetype == "listings":
            listings.append(read_listings(path))
        elif filetype == "drugclas":
            classes.append(read_class(path))
        elif filetype == "formulat":
            formulations.append(read_formulation(path))
        else:
            raise Exception("Unexpected file type: {}".format(filetype))

    # Drugs file
    drugs = pd.concat(listings, ignore_index=True).drop_duplicates()
    drugs["ndc"] = drugs.apply(lambda x: "{:05d}{:04d}".format(x["lblcode"], x["prodcode"]), axis=1)
    drugs["name"] = drugs["tradename"].str.upper()
    drugs["schedule"] = "NA"
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
