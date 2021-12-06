import pandas as pd
from pathlib import Path
# the second last column in animals.csv (before target column) is catsize which is a text column - which sklean's decision tree does not accept. Keeping in mind that rules are being created as an explainability model, creating rules on encoded attrbitues leads to rules rules that are not interpretable and therefore not explainable. As a result, text columns will be removed. 
filename = 'animals.csv'
df = pd.read_csv(filename)
print(df.iloc[:,-2]) # second last column to be removed
df = df.drop(df.columns[[-2]], axis = 1) # insert any columns to be removed inside the double square brackets [[]]
print(df) # the catsize column is removed
# export dataframe to csv
path = Path("animalsmodified.csv")
df.to_csv(path, index=False)