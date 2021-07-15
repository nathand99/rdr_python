import numpy as np 
import pandas as pd

#https://www.w3resource.com/pandas/dataframe/dataframe-query.php
#https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/
class Node:
    def __init__(self, num=None, data=None, con=None, nextTrue=None, nextFalse=None, case=None):
        self.num = num
        self.data = data 
        self.con = con
        self.nextTrue = nextTrue # index of true branch or string of conclusion
        self.nextFalse = nextFalse # index of false branch or None or string of conclusion
        self.case = case # case name the rule was added for
        #self.case = [] # all cases for which rule is true in dataframe. first example is the first one you added (cornerstone case). might be useful to add all cases for which rule gives true. eg all mammals

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
        print("-"*50)
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

# rules: linked list of rules
rules = SLinkedList()
# 1 rule
rules.head = Node("milk==1")
rules.head.number = rules.count
# Link first Node to second node
rules.head.nextTrue = "mammal"
rules.head.nextFalse = None
rules.count += 1

# rules list
# Node(number=None, data=None, con=None, nextTrue=0, nextFalse=0, case=None)
rules_list = [None] * 100 # magic number - max 100 rules
# Note: rules_list[0] is always None - rules_list[1] is the head
# rules_count = number of rules currently in list = index of next rule + 1
rules_count = 0
rules_list[1] = Node(1, "milk==1", "mammal", "mammal", None, "aardvark")
rules_count += 1

                
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

# run through rules for a single case - modifys conclusion for case if needed
def run_case(case):
    n = rules_list[1]
    while n is not None:
        # n is a node in rules_list
        if isinstance(n, Node):
            # print case for user
            print(df.query("name==" + "'" + case + "'"))
            query = "name==" + "'" + case + "'" + " and " + n.data
            # query this case for rule
            print(f"Applying rule: {n.data}")
            result = df.query(query) 
            # if empty - no result - rule is not true for this case - goto false branch
            if result.empty == True:
                print(f"Result: FALSE for case {case}. Going to FALSE branch of rule")
                branch = n.nextFalse
            # if not empty - rule is true - goto true branch
            else:
                print(f"Result: TRUE for case {case}. Going to TRUE branch of rule")
                branch = n.nextTrue
            # deal with branch. Could be string->conclusion, None->No conclusion, index->keep going
            if isinstance(branch, str):
                add_conclusion(case, branch)
                return n
            elif branch == None:
                print("End of rules reached. No conclusion")
                return
            else:
                n = rules_list[branch]

# assign "conclusion" string to conclusion column for given case
def add_conclusion(case, conclusion):
    print(f"Conclusion reached: {conclusion}")
    df.loc[df["name"] == case, 'conclusion'] = conclusion
    print(df.query("name==" + "'" + case + "'")) # print case for user
    return

# add new rule to rules_list - cornerstone
def add_rule(rule, conclusion, nextTrue, nextFalse, case, rules_count):
    n = rules_list[1]
    prev = n
    # rules_list is empty
    if rules_list[1] == None:
        rules_count += 1
        rules_list[1] = Node(num=rules_count, data=rule, con=conclusion, nextTrue=nextTrue, nextFalse=nextFalse, case=case)
    # go down nextFalse until None
    else:
        while n is not None:
            prev = n
            index = n.nextFalse  
            if index == None:
                break
            i = rules_list[index]
        rules_count += 1 # when incremented - rules_count = number of rules = index of current rule
        rules_list[rules_count] = Node(num=rules_count, data=rule, con=conclusion, nextTrue=nextTrue, nextFalse=nextFalse, case=case)
        prev.nextFalse = rules_count
    print("New rule added")

# prompt loop
while (True):
    print("Hello")
    print("Press (1) to see cases dataframe")
    print("Press (2) add a rule")
    print("Press (3) to run rules on single case")
    print("Press (4) to run rules on all cases")
    print("Press (5) to see all rules")
    #print("Press (q) to quit")
    i = int(input())
    # print cases dataframe
    if i == 1:
        print(df)
    # enter a new rule - not allowed anymore
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
            add_rule(rule, conclusion, conclusion, None, None, rules_count)
            rules_count += 1 # doesnt increment in function
    # run rules on a single case
    elif i == 3:
        # TODO add check if case is legit
        case = input("Which case to run?\n")
        case = case.lower()
        # run through rules for case. r = the last rule used
        r = run_case(case)
        # get target value amd conclusion value - test if equal
        caserow = df.loc[df["name"] == case]
        target = caserow.iloc[0]["target"]
        con = caserow.iloc[0]["conclusion"]
        print()
        print(f"Is the conclusion correct for case {case} (target == conclusion)?")
        # conclusion correct - nothing to be done
        if target == con:
            print("Conclusion correct")
        # conclusion missing - add new cornerstone case
        elif con == "-":
            print("Conclusion missing")
            print(f"Add a new rule to correctly classify {case}")
            full_rule = enter_new_rule()
            split_rule = full_rule.split()
            #rule = milk==1
            rule = split_rule[1] + split_rule[2] + split_rule[3]
            #conclusion = mammal
            conclusion = split_rule[5]
            # add rule
            add_rule(rule, conclusion, conclusion, None, case, rules_count)
            rules_count += 1 
        # conclusion incorrect - add refinement rule
        else:
            print("Conclusion incorrect")
            print("Add a correcting rule")
            # the last rule gives a conclusion - which is incorrect. Take last rule
            last_rule = r
            # find which branch is taken - which gives incorrect result
            query = "name==" + "'" + case + "'" + " and " + last_rule.data
            result = df.query(query) 
            # if empty - goto false branch
            if result.empty == True:
                branch = False
            else:
                branch = True
            print(branch)
            # we must add a refinement rule on this rule. 
            # refinement rule must use features that have different values from the cornerstone case to differentiate it
            # new rules must include the case that they were added on

            # look up case for last rule. Compare with current case and show which features are different
            # user creates new rule
            query1 = "name==" + "'" + case + "'"
            df1 = df.query(query1) 
            query2 = "name==" + "'" + last_rule.case + "'"
            df2 = df.query(query2) 
            a = df1.columns.intersection(df2.columns)
            print (a)
            # alternatively
            #df1.columns & df2.columns
            full_rule = enter_new_rule()
            split_rule = full_rule.split()
            #rule = milk==1
            rule = split_rule[1] + split_rule[2] + split_rule[3]
            #conclusion = mammal
            conclusion = split_rule[5]
            # add rule
            # true case
            if branch:
                rules_count += 1 
                rules_list[rules_count] = Node(rules_count, rule, conclusion, conclusion, last_rule.nextTrue, case)
                last_rule.nextTrue = rules_count
                print("Refinement rule added")
            else:
                pass
            
            
            # rule manipulation
            # temp = lastrule.nextTrue
            # last rule nextTrue = new rule
            # new rule nextFalse = lastrule.NextTrue

    # run rules on all animals
    elif i == 4:
        pass
        # for case in df['name']:
    # print rules and their branches
    elif i == 5:
        print("Rules")
        #print("Number\tRule\t\tConclusion\t\tTRUEBranch\t\tFALSEBranch\t\tCase")
        print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format("Number", "Rule", "Conclusion", "TRUEBranch", "FALSEBranch", "Case"))
        i = 1
        while i <= rules_count:
            n = rules_list[i]
            #print(f"{n.num}\t{n.data}\t\t{n.con}\t\t{n.nextTrue}\t\t{n.nextFalse}\t\t{n.case}")
            print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case))
            i += 1
    # clear all rules
    elif i == 6:
        rules_count = 0
        rules_list = rules_list = [None] * 100
    # clear dataframe
    elif i == 7:
        df = pd.read_csv(filename)
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