import numpy as np 
import pandas as pd

#https://www.w3resource.com/pandas/dataframe/dataframe-query.php
#https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/
class Node:
    def __init__(self, data=None):
        self.number = None
        self.data = data
        self.nextTrue = None
        self.nextFalse = None
        self.case = [] # all cases for which rule is true in dataframe. first example is the first one you added (cornerstone case). might be useful to add all cases for which rule gives true. eg all mammals

class SLinkedList:
    def __init__(self):
        self.head = None
        self.count = 1

    def listprint(self):
        printval = self.head
        while printval is not None:
            print (printval.data)
            print("Then")
            print(printval.nextTrue)
            printval = printval.nextFalse

# function to enter a new rule. Returns rule
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
            abort = input("Abort or retry adding new rule? (y/n)")
            if abort.lower() == 'y':
                print("Aborting adding new rule")
                return -1
            else:
                continue

#print(df.query('milk == 0 and name == "frog"')) # only show rows with animals which have milk == 1
#print(df.query('milk == 1')[['name','milk']]) # same but only show columns named

# data imported must be csv file with the first line giving attribute names
# last column is target class column. I will add an empty conclusion column
# care for missing values and weird values
filename = 'animals.csv'
df = pd.read_csv(filename)

# add empty conclusion column
df['conclusion'] = '-'
#print(df)

# rules: linked list of rules
rules = SLinkedList()
# 1 rule
rules.head = Node("milk==1")
rules.head.number = rules.count
# Link first Node to second node
rules.head.nextTrue = "mammal"
rules.head.nextFalse = None
rules.count += 1

# prompt loop
while (True):
    print("Hello")
    print("Press (1) to see rules dataframe")
    print("Press (2) add a rule")
    print("Press (3) to run rules on single case")
    print("Press (4) to run rules on all cases")
    #print("Press (q) to quit")
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
            if rules.head == None:
                rules.head = Node(rule)
                rules.head.number = rules.count
                rules.count += 1
                # Link first Node to second node
                rules.head.nextTrue = conclusion
                rules.head.nextFalse = None
            else:
                n = rules.head
                while n is not None:
                    n = n.nextFalse          
    elif i == 3:
        # single animal
        case = input("Which case to run?\n")
        case = case.lower()
        # run through rules
        n = rules.head
        while n is not None:
            #print(n)
            #print(df.query(name == "frog" and 'milk == 0)) 
            # n is a node in rules tree
            if isinstance(n, Node):
                query = "name==" + "'" + case + "'" + " and " + n.data
                # print case without query for user
                print(df.query("name==" + "'" + case + "'"))
                result = df.query(query) # query this case for rule
                # if empty - no result - rule is not true for this case - goto false branch
                if result.empty == True:
                    print(f"Applying rule: {n.data}")
                    print(f"Result: NOT true for case {case}. Going to FALSE branch of rule")
                    n = n.nextFalse
                # # if not empty - rule is true - goto false branch
                else: 
                    print(f"Applying rule: {n.data}")
                    print(f"Result: IS true for case {case}. Going to TRUE branch of rule")
                    n = n.nextTrue
            # n is a string - assign string to conclusion column for this case
            else:
                print(f"Conclusion reached: {n}")
                df.loc[df["name"] == case, 'conclusion'] = n
                print(df.query("name==" + "'" + case + "'")) # print case for user
                break
        # get target value amd conclusion value - test if equal
        caserow = df.loc[df["name"] == case]
        target = caserow.iloc[0]["target"]
        con = caserow.iloc[0]["conclusion"]
        if target == con:
            print("Conclusion correct")
        elif con == "-":
            print("Conclusion missing")
            print("Add a new rule")
            full_rule = enter_new_rule()
            split_rule = full_rule.split()
            #rule = milk==1
            rule = split_rule[1] + split_rule[2] + split_rule[3]
            #conclusion = mammal
            conclusion = split_rule[5]
            # add rule to rules
            n = rules.head
            prev = n
            if rules.head == None:
                rules.head = Node(rule)
                rules.head.number = rules.count
                rules.count += 1
                # Link first Node to second node
                rules.head.nextTrue = conclusion
                rules.head.nextFalse = None
            else:
                while n is not None:
                    prev = n
                    n = n.nextFalse  
                new = Node(rule)
                new.number = rules.count
                rules.count += 1
                new.nextTrue = conclusion
                new.nextFalse = None
                prev.nextFalse = new
            print("New rule added")
        else:
            print("Conclusion incorrect")
            print("Add a correcting rule")
            
    # and all animals
    elif i == 4:
        pass
    # clear all rules
    elif i == 5:
        pass
    # clear dataframe
    elif: i == 6:
        pass
    else: 
        exit()
            
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