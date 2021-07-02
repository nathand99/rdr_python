import numpy as np 
import pandas as pd

#https://www.w3resource.com/pandas/dataframe/dataframe-query.php
#https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/
class Node:
    def __init__(self, dataval=None):
        self.dataval = dataval
        self.nexttrue = None
        self.nextfalse = None
        self.case = [] # all cases for which rule is true in dataframe. first example is the first one you added (cornerstone case). might be useful to add all cases for which rule gives true. eg all mammals

class SLinkedList:
    def __init__(self):
        self.headval = None

    def listprint(self):
        printval = self.headval
        while printval is not None:
            print (printval.dataval)
            print("Then")
            print(printval.nexttrue)
            printval = printval.nextfalse



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
#print(df)

# rules linked list
list = SLinkedList()

# prompt loop
while (True):
    print("Hello")
    print("Press (1) to see rules dataframe")
    print("Press (2) add a rule")
    print("Press (3) to run rule")
    i = int(input())
    if i == 1:
        print(df)
    elif i == 2:
        full_rule = enter_new_rule()
        if full_rule == -1:
            continue
        else:
            print(f"Added rule: {full_rule}")
            # split full_rule into rule and conclusion
            split_rule = full_rule.split()
            #rule = milk==1
            rule = split_rule[1] + split_rule[2] + split_rule[3]
            #conclusion = mammal
            conclusion = split_rule[5]
            if list.headval == None:
                list.headval = Node(rule)
                # Link first Node to second node
                list.headval.nexttrue = conclusion
            else:
                n = list.headval
                while n is not None:
                    n = n.nextFalse
                
    elif i == 3:
        # single animal and all animals
        n = list.headval
        while n is not None:
            query = n.dataval + " and " + "name==" + "'" + "aardvark" + "'"
            print(df.query(query))
            #ddd = query ... if ddd.empty == true
            
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