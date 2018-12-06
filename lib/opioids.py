import pandas as pd
import sys

ingfile, outfile = sys.argv[1:]

# Minimum prescribing guidelines from:
# http://www.agencymeddirectors.wa.gov/Files/2015AMDGOpioidGuideline.pdf
opioids = {
    "CODEINE":      30.0,
    "FENTANYL":      0.0125,
    "HYDROCODONE":   5.0,
    "HYDROMORPHONE": 2.0,
    "MEPERIDINE":    0.0,
    "MORPHINE":     10.0,
    "OXYCODONE":     5.0,
    "OXYMORPHONE":   5.0,
    "TAPENTADOL":   50.0,
    "TRAMADOL":     50.0
}
recovery = [
    "BUPRENORPHINE",
    "METHADONE",
    "NALOXONE",
    "NALTREXONE"
]


ingredients = pd.read_csv(ingfile, dtype={"ndc": str, "amount": float})
print(ingredients.head())
print(ingredients.dtypes)
print("unique NDCs:", len(ingredients.ndc.unique()))
print("total ingredient entries:", len(ingredients))

ingredients = ingredients.dropna(subset=["ndc"])
ingredients["ndc_isdigits"] = ingredients.ndc.apply(lambda s: sum(c.isdigit() for c in s))
ingredients = ingredients[ingredients.ndc_isdigits == 9]
print("after dropping entries with missing or non-digit NDC:", len(ingredients))

ingredients = ingredients[ingredients.ingredient.notnull() & (ingredients.ingredient != "")]
print("after dropping entries with missing ingredient:", len(ingredients))

ingredients = ingredients.dropna(subset=["amount"])
print("after dropping entries with missing amount:", len(ingredients))

# Remove spaces from units
ingredients["unit"] = ingredients["unit"].str.strip()

# What are the most common units?
print("most common units:")
print(ingredients["unit"].value_counts()[:20])

# Standardize weight units to mg
units = {
    "UG": 0.001,
    "MCG": 0.001,
    "MG": 1.0,
    "G": 1000.0,
    "GM": 1000.0,
    "KG": 1000000.0
}
for unit, x in units.items():
    ingredients.loc[ingredients["unit"] == unit, "mg"] = x * ingredients.loc[ingredients["unit"] == unit, "amount"]

# How many ingredients are not weights?
print("ingredient entries without weight:", ingredients["mg"].isnull().sum())

# Identify opioid ingredients using the first word of the ingredient.
ingredients["firstword"] = ingredients["ingredient"].str.partition(" ")[0]

# Code opioid ingredients above the threshold as 1, and those below as -1.
ingredients.loc[:, "opioid"] = 0
for name, mg in opioids.items():
    ingredients.loc[ingredients["firstword"] == name, "opioid"] = -1
    ingredients.loc[(ingredients["firstword"] == name) & (ingredients["mg"] >= mg), "opioid"] = 1

# Code recovery ingredients at any amount as 1.
ingredients.loc[:, "recovery"] = 0
for name in recovery:
    ingredients.loc[ingredients["firstword"] == name, "recovery"] = 1

# Groupby/max to code NDCs with at least one opioid/recovery ingredient as that code.
ndc = ingredients.groupby("ndc")[["opioid", "recovery"]].max().reset_index()

print("number of opioid drugs:")
print(ndc["opioid"].value_counts())

print("number of recovery drugs:")
print(ndc["recovery"].value_counts())

print("drugs classified as both opioid and recovery:")
print(ndc[(ndc["opioid"] == 1) & (ndc["recovery"] == 1)])

# Save to CSV
ndc.to_csv(outfile, index=False)

