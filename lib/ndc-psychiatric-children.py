import pandas as pd 
import sys

ingfile, ndcing_file, drug_file, outfile = sys.argv[1:]

#Getting associated NDC codes for ingredients of interest 
ingredients = pd.read_csv(ingfile, dtype={'category_name': str, 'binomial': str})
ingredients["binomial"] = ingredients["binomial"].str.upper()
ingredients["category_name"] = ingredients["category_name"].str.upper()


ndc_ing = pd.read_csv(ndcing_file, dtype = {'ndc': str,'ingredient': str , 'amount':float, 'unit': str})
ndc_ing = ndc_ing.dropna(subset=["ndc"])
ndc_ing["ndc_isdigits"] = ndc_ing.ndc.apply(lambda s: sum(c.isdigit() for c in s))
ndc_ing = ndc_ing[ndc_ing.ndc_isdigits == 9]
print("after dropping entries with missing or non-digit NDC:", len(ndc_ing))

ndc_ing = ndc_ing[ndc_ing.ingredient.notnull() & (ndc_ing.ingredient != "")]
print("after dropping entries with missing ingredient:", len(ndc_ing))

ndc_child = pd.merge(ndc_ing, 
                    ingredients, 
                    left_on = 'ingredient', 
                    right_on = 'binomial', 
                    how = 'right')
(print("drug ingredients that aren't in ndc file:", ndc_child.binomial[ndc_child.ndc.isnull()]))


ndc_child = ndc_child[['ndc', 'ingredient', 'category_name']]
ndc_child = ndc_child.sort_values("ndc")
print("unique NDCs:", len(ndc_child.ndc.unique()))
#Summary on number of ndc codes per ingredient 
count_by_category = ndc_child.groupby('category_name').count()
print(count_by_category)

#Quick sanity check -- spot check drug names to see if they match what we wanted them to be (ritalin, adderal, etc.)
drugs = pd.read_csv(drug_file, dtype = {'ndc': str, 'name': str, 'schedule': str})
ndc_drug = pd.merge(ndc_child, 
                    drugs, 
                    left_on = 'ndc', 
                    right_on = 'ndc', 
                    how = 'inner')
print(ndc_drug.head())
print(len(ndc_drug.ndc.unique()))

drugs_by_cats = ndc_drug.groupby(['category_name', 'name']).size()
print(drugs_by_cats)


#Generating indicators
category = {
    
    "ADHD", 
    "ANTIDEPRESSANT", 
    "ANTIPYSCHOTIC", 
    "MOOD STABILIZER AND ANTICONVULSANT", 
    "ANTI-ANXIETY", 
    "SLEEP"

}

for name in category: 
    ndc_child.loc[:, name] = 0 
    ndc_child.loc[ndc_child["category_name"] == name, name] = 1

#Quick spot check 
print(ndc_child[["ndc", "category_name", "ANTI-ANXIETY"]]) 

ndc_child = ndc_child[["ndc", "ADHD", "ANTIDEPRESSANT", "ANTIPYSCHOTIC", "MOOD STABILIZER AND ANTICONVULSANT", "ANTI-ANXIETY", "SLEEP"]]

ndc_child = ndc_child.groupby("ndc")[["ADHD", "ANTIDEPRESSANT", "ANTIPYSCHOTIC", "MOOD STABILIZER AND ANTICONVULSANT", "ANTI-ANXIETY", "SLEEP"]].max().reset_index()

#Number should be the same if aggregation was done correctly 
print("number ndc:", len(ndc_child.ndc))
print("number unique ndc:", len(ndc_child.ndc.unique()))


#Save to CSV
ndc_child.to_csv(outfile, index=False)

