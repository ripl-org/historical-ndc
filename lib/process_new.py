"""
Process 2011-present files.
"""
import pandas as pd


def reformat_ndc(x):
    """
    Convert unpadded XXXXX-XXXX format to zero-padded XXXXXXXXX.
    """
    upper, _, lower = x.upper().partition("-")
    return upper.zfill(5) + lower.zfill(4)


def split_ingredients(products):
    """
    Some years have multiple amounts, units and ingredients with a semi-colon
    separator. Break these into separate rows.
    """
    ingredients = {"ndc": [], "amount": [], "unit": [], "ingredient": []}

    for row in products[products.amount.notnull() &
                        products.unit.notnull() &
                        products.ingredient.notnull()].itertuples():

        amount = list(map(str.strip, row.amount.split(";")))
        unit = list(map(str.strip, row.unit.split(";")))
        ingredient = list(map(str.strip, row.ingredient.split(";")))

        assert len(amount) == len(unit)
        assert len(amount) == len(ingredient)

        for a, u, i in zip(amount, unit, ingredient):
            ingredients["ndc"].append(row.ndc)
            ingredients["amount"].append(a)
            ingredients["unit"].append(u.partition("/")[0].upper())
            ingredients["ingredient"].append(i.upper())

    return pd.DataFrame(ingredients, columns=["ndc", "ingredient", "amount", "unit"]).drop_duplicates()


def Process(target, source, env):

    products = []

    for path in [f.path for f in source]:

        if path.split("/")[2] != "product": continue

        header = open(path, encoding="latin-1").readline().split("\t")

        if len(header) == 16:
            usecols = [0, 4, 12, 13, 14]
            names = ["ndc", "name", "ingredient", "amount", "unit"]
        elif len(header) == 17:
            usecols = [0, 4, 12, 13, 14, 16]
            names = ["ndc", "name", "ingredient", "amount", "unit", "schedule"]
        else:
            usecols = [1, 5, 13, 14, 15, 17]
            names = ["ndc", "name", "ingredient", "amount", "unit", "schedule"]

        if header[0] == "PRODUCTNDC" or header[0] == "PRODUCTID":
            skiprows = 1
        else:
            skiprows = 0

        df = pd.read_csv(path, encoding="latin-1", sep="\t",
                         usecols=usecols, names=names, skiprows=skiprows, dtype=str)

        df["ndc"] = df["ndc"].apply(reformat_ndc)
        df["name"] = df["name"].str.upper()

        if "schedule" in df.columns:
            df["schedule"] = df["schedule"].map({"": "", "CI": "1", "CII": "2", "CIII": "3", "CIV": "4", "CV": "5"})
        else:
            df["schedule"] = ""

        products.append(df)

    products = pd.concat(products, ignore_index=True).drop_duplicates()

    # Drugs file
    products.to_csv(target[0].path, columns=["ndc", "name", "schedule"], index=False)

    # Ingredients file
    split_ingredients(products).to_csv(target[1].path, index=False)


# vim: syntax=python expandtab sw=4 ts=4
