import pandas as pd
from pathlib import Path
# Name is renamed to name and survived renamed to survived
filename = 'titanictrain2.csv'
df = pd.read_csv(filename)
df = df[["name"] + [col for col in df.columns if col != "name"]] # put name at front
df = df.drop(df.columns[[1]], axis = 1) # remove passenger id
df = df[[col for col in df.columns if col != "target"] + ["target"]] # put target at the end
#df["name"] = df["name"].astype(str)
df.iloc[:,-1].replace(0, "died", inplace=True) # change target values to string
df.iloc[:,-1].replace(1, "lived", inplace=True)
df.iloc[:,2].replace("male", 0, inplace=True) # change gender to numeric
df.iloc[:,2].replace("female", 1, inplace=True)
df = df.fillna(method="ffill") # change nans to value in next row
df = df.drop(df.columns[[-2, -3, -5]], axis = 1) # remove cabin and embarked and ticket number because they contain strings
df = df.replace('\'', '', regex=True)
print(df)
# export dataframe to csv
path = Path("titanicmodified.csv")
df.to_csv(path, index=False)