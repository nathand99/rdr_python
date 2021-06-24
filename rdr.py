import numpy as np 
import pandas as pd

#https://www.w3resource.com/pandas/dataframe/dataframe-query.php
#https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/

# function to enter a new rule. Returns 
def enter_new_rule():
    while(1):
        print("Entering new rule")
        print("-"*50)
        print("if")
        attribute = input("Enter an attribute: ")
        operator = input("Enter an operator: ")
        value = input("Enter an value: ")
        print("then: ")
        conclusion = input("Enter a conclusion: ")
        print("Rule entered:")
        string = f"if {attribute} {operator} {value} then {conclusion}"
        print(string)
        correct = input("Is the rule correct (y/n)? ")
        if correct.lower() == 'y':
            return string
        else:
            abort = input("Retry or abort adding new rule? ")
            if abort.lower() == 'y':
                print("Aborting adding new rule")
                return -1
            else:
                continue

# data imported must be csv file with the first line giving attribute names
# last column is target class column. I will add an empty conclusion column
# care for missing values and weird values
filename = 'animals.csv'
df = pd.read_csv(filename)
#print(df.query('milk == 0 and name == "frog"')) # only show rows with animals which have milk == 1
#print(df.query('milk == 1')[['name','milk']]) # same but only show columns named

# add empty conclusion column
df['conclusion'] = '-'
print(df)

# rules list
rules = []

full_rule = enter_new_rule()
if full_rule == -1: 
    exit()
else:
    print(f"Added rule: {full_rule}")

# split full_rule into rule and conclusion
split_rule = full_rule.split()
rule = split_rule[1] + split_rule[2] + split_rule[3]
#rule = milk==1
conclusion = split_rule[5]
#conclusion = mammal
print(df.query(rule)[['name','milk','target']])
#print(df.query('milk == 1')[['name','milk','type']])
#rule = "milk == 1"
rules.append(rule + " " + conclusion)
print("here are the rules")
print(rules)

# for all animals - apply rules
for animal in df['name']:
    for r in rules:
        # if query returns a result - it means the rule is true
        # if nothing returned - rule is false - go to next rule (or list of rules)
        query = r.split()[0] + " and " + "name==" + "'" + animal + "'"
        print(query)
        #print(df.query(query)[['name','milk','target']])
        #if df.query(query)[['name','milk','target']] != None:
        #df.loc[9,['avg_precipitation']] = np.nan

        # here the rule is true - i set conclusion to the conclusion given by the rule
        # DO NOT wrap .loc in print statement
        df.loc[df["target"] == "mammal", 'conclusion'] = r.split()[1]
        #df.loc[0, 'conclusion'] = 10
        #print(df)
        df.loc[df["name"] == animal][["conclusion"]] = r.split()[1]
        print(df[['name','milk', 'target', 'conclusion']])
        break
    break


