import pandas as pd 
import sys

cpfile, ingfile, drugfile, outfile = sys.argv[1:]

# Load child psychiatric active ingredients and categories
cp = pd.read_csv(cpfile, dtype=str)

# Load NDC ingredients
ing = pd.read_csv(ingfile, usecols=["ndc", "ingredient"], dtype=str).dropna(subset=["ndc"])
ing["isdigits"] = ing.ndc.apply(lambda s: sum(c.isdigit() for c in s))
ing = ing[ing.isdigits == 9]
print("after dropping entries with missing or non-digit NDC:", len(ing))

ing = ing[ing.ingredient.notnull() & (ing.ingredient != "")]
print("after dropping entries with missing ingredient:", len(ing))

cp = cp.merge(ing, on="ingredient", how="left")
print("child psychiatric ingredients without any NDCs:", cp.ingredient[cp.ndc.isnull()])

print("unique NDCs matched:", cp.ndc.nunique())

print("Counts of NDC codes per child psychiatric ingredient:")
print(cp.groupby("category").count())

print("Summary of 10 most frequently occuring drug names by category:")
drugs = pd.read_csv(drugfile, dtype=str).merge(cp, on="ndc", how="inner")
for category in cp.category.unique():
    print(category)
    print(drugs[drugs.category == category].groupby("proprietary_name").size().sort_values(ascending=False).head(10))
    print()

# Generate indicators
for category in cp.category.unique():
    cp.loc[:, category] = 0 
    cp.loc[cp.category == category, category] = 1

# Save
cp.drop(columns=["isdigits", "category", "ingredient"]).to_csv(outfile, index=False)

