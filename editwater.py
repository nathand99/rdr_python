import pandas as pd
from pathlib import Path
# the second last column in animals.csv (before target column) is catsize which is a text column - which sklean's decision tree does not accept. Keeping in mind that rules are being created as an explainability model, creating rules on encoded attrbitues leads to rules rules that are not interpretable and therefore not explainable. As a result, text columns will be removed. 
filename = 'water_potability2.csv'
df = pd.read_csv(filename)
df.iloc[:,-1].replace(0, "good", inplace=True)
df.iloc[:,-1].replace(1, "bad", inplace=True)
name = range(0, df.shape[0])
df["name"] = name
df = df[["name"] + [col for col in df.columns if col != "name"]]
df["name"] = df["name"].astype(str)
print(df)
# export dataframe to csv
path = Path("watermodified.csv")
df.to_csv(path, index=False)