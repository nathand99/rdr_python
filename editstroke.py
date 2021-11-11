import pandas as pd
from pathlib import Path
# the second last column in animals.csv (before target column) is catsize which is a text column - which sklean's decision tree does not accept. Keeping in mind that rules are being created as an explainability model, creating rules on encoded attrbitues leads to rules rules that are not interpretable and therefore not explainable. As a result, text columns will be removed. 
filename = 'healthcare-dataset-stroke-data.csv'
df = pd.read_csv(filename)
df.iloc[:,-1].replace(0, "nostroke", inplace=True)
df.iloc[:,-1].replace(1, "stroke", inplace=True)
print(df)
# export dataframe to csv
path = Path("strokemodified.csv")
df.to_csv(path, index=False)