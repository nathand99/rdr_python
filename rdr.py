import numpy as np 
import pandas as pd
from sklearn import preprocessing, tree
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.tree import export_graphviz
from six import StringIO 
from IPython.display import Image 
from pydot import graph_from_dot_data

class Node:
    def __init__(self, num=None, data=None, con=None, nextTrue=None, nextFalse=None, case=None, true_cases=[]):
        self.num = num
        self.data = data 
        self.con = con
        self.nextTrue = nextTrue # index of true branch or string of conclusion
        self.nextFalse = nextFalse # index of false branch or None or string of conclusion
        self.case = case # case name the rule was added for
        self.true_cases = true_cases # all rules that are true leading up to this rule

def print_full(x):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

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
            # split rule by spaces
            split_rule = string.split()
            #rule = milk==1
            rule = split_rule[1] + split_rule[2] + split_rule[3]
            #conclusion = mammal
            conclusion = split_rule[5]
            return rule, conclusion
        else:
            abort = input("Abort? (y) or retry adding new rule? (y/n)")
            if abort.lower() == 'y':
                print("Aborting adding new rule")
                return -1
            else:
                continue

# rules list
# Node(number=None, data=None, con=None, nextTrue=0, nextFalse=0, case=None)
rules_list = [None] * 100 # magic number - max 100 rules
# Note: rules_list[0] is always None - rules_list[1] is the head
# rules_count = number of rules currently in list. Increment before adding rule
rules_count = 0
rules_list[1] = Node(1, "milk==1", "mammal", "mammal", 2, "aardvark", [])
rules_count += 1
rules_list[2] = Node(2, "acquatic==1", "fish", "fish", None, "bass", [])
rules_count += 1

# data imported must be csv file with the first line giving attribute names
# last column is target class column. I will add an empty conclusion column
# only numeric data allowed. target values allowed to be text
# care for missing values and weird values
filename = 'animals.csv'
df = pd.read_csv(filename)

# change target to numeric value. Note: the numeric value is in alphabetical order of the targets
targets = np.unique(df['target'].values) # targets_list
le = preprocessing.LabelEncoder()
le.fit(targets)
    #['mammal', 'fish', 'bird', 'mollusc', 'insect', 'amphibian', 'reptile']
transformed = le.transform(targets)
    #[4 2 1 5 3 0 6]
back = list(le.inverse_transform(transformed))
    #['mammal', 'fish', 'bird', 'mollusc', 'insect', 'amphibian', 'reptile']
# add empty encoded column - add int encoding of each target to encoding column
df['encoded'] = '-'
for c in df['name']:
    caserow = df.loc[df["name"] == c]
    t = caserow.iloc[0]["target"] # mammal
    transform = le.transform([t])[0]
    df.loc[df["name"] == c, 'encoded'] = transform

# add empty conclusion column
df['conclusion'] = '-'

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
                print("\nEnd of rules reached. No conclusion\n")
                return
            else:
                n = rules_list[branch]

# run_case function but with no print statements
def run_case_no_prints(case):
    n = rules_list[1]
    while n is not None:
        # n is a node in rules_list
        if isinstance(n, Node):
            # print case for user
            query = "name==" + "'" + case + "'" + " and " + n.data
            # query this case for rule
            result = df.query(query) 
            # if empty - no result - rule is not true for this case - goto false branch
            if result.empty == True:
                branch = n.nextFalse
            # if not empty - rule is true - goto true branch
            else:
                branch = n.nextTrue
            # deal with branch. Could be string->conclusion, None->No conclusion, index->keep going
            if isinstance(branch, str):
                add_conclusion_no_prints(case, branch)
                return n
            elif branch == None:
                return
            else:
                n = rules_list[branch]

# find rules that are true to lead to give case
def find_true_rules(case):
    true_rules = []
    n = rules_list[1]
    while n is not None:
        # n is a node in rules_list
        if isinstance(n, Node):
            query = "name==" + "'" + case + "'" + " and " + n.data
            # query this case for rule
            result = df.query(query) 
            # if empty - no result - rule is not true for this case - goto false branch
            if result.empty == True:
                branch = n.nextFalse
            # if not empty - rule is true - goto true branch
            else:
                true_rules.append(n.num)
                branch = n.nextTrue
            # is string - return true_rules
            if isinstance(branch, str):
                return true_rules
            elif branch == None:
                return true_rules
            else:
                n = rules_list[branch]
    return true_rules

# assign "conclusion" string to conclusion column for given case
def add_conclusion(case, conclusion):
    print(f"\nConclusion reached: {conclusion}\n")
    df.loc[df["name"] == case, 'conclusion'] = conclusion
    print(df.query("name==" + "'" + case + "'")) # print case for user
    return

# add_conclusion - with no prints
def add_conclusion_no_prints(case, conclusion):
    df.loc[df["name"] == case, 'conclusion'] = conclusion
    return

# add new rule to rules_list - cornerstone. true_cases = []
def add_cornerstone_rule(rule, conclusion, nextTrue, nextFalse, case, rules_count):
    n = rules_list[1]
    prev = n
    # rules_list is empty
    if rules_list[1] == None:
        rules_count += 1
        rules_list[1] = Node(num=rules_count, data=rule, con=conclusion, nextTrue=nextTrue, nextFalse=nextFalse, case=case, true_cases=[])
    # go down nextFalse until None
    else:
        while n is not None:
            prev = n
            index = n.nextFalse  
            if index == None:
                break
            n = rules_list[index]
        rules_count += 1 # when incremented - rules_count = number of rules = index of current rule
        rules_list[rules_count] = Node(num=rules_count, data=rule, con=conclusion, nextTrue=nextTrue, nextFalse=nextFalse, case=case, true_cases=[])
        prev.nextFalse = rules_count
    print("New rule added")

def add_refinement_rule(last_rule, case, rules_count):
    # find which branch is taken - which gives incorrect result
    query = "name==" + "'" + case + "'" + " and " + last_rule.data
    result = df.query(query) 
    # if empty - goto false branch
    if result.empty == True:
        branch = False
    else:
        branch = True
    # find rules which are true for case
    true_list = find_true_rules(case)
    # refinement rule must use features that have different values from the cornerstone case to differentiate it
    # 1. must show rules that already apply. len(true_list) > 1 should always be true
    if len(true_list) > 0:
        print("Rules true for this case up to this point")
        print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format("Number", "Rule", "Conclusion", "TRUEBranch", "FALSEBranch", "Case"))
        for i in true_list:
            n = rules_list[i]
            print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case))
    # 2. must show attributes that are different and which a rule can be made
    # look up case for the last true rule. Compare with current case and show which features are different
        query1 = "name==" + "'" + case + "'"
        df1 = df.query(query1) 
        query2 = "name==" + "'" + rules_list[true_list[-1]].case + "'"
        df2 = df.query(query2) 
        df3 = df1.append(df2)
        print(f"The following columns have different values for the case for which the last rule was true ({rules_list[true_list[-1]].case}) and the current case ({case}). Use these attributes to make a new rule.")
        for col in df3.columns:
            if col == "conclusion" or col == "target" or col == "encoded" or col == "name":
                continue
            if len(df3[col].value_counts()) > 1:
                print(col)
    # add refinement rule
    rule, conclusion = enter_new_rule()
    # true case
    if branch:
        rules_count += 1 
        rules_list[rules_count] = Node(rules_count, rule, conclusion, conclusion, last_rule.nextTrue, case, true_list)
        last_rule.nextTrue = rules_count
    # false case
    else:
        rules_count += 1 
        rules_list[rules_count] = Node(rules_count, rule, conclusion, conclusion, last_rule.nextFalse, case, true_list)
        last_rule.nextFalse = rules_count
    print("\nRefinement rule added: ")
    n = rules_list[rules_count]
    print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}\n'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))

# predict case using decision tree
def predict_case(dt, case):
    c = df.loc[df["name"] == case]
    c = c.iloc[:,1:-4]
    r = dt.predict(c) # gives an encoded array
    r = le.inverse_transform(r) # unencode it
    return r[0]

# initialised outside the loop
dt = DecisionTreeClassifier()
X = df.iloc[:,1:-4]

# prompt loop
while (True):
    print("Hello")
    print("Press (0) train decision tree on data")
    print("Press (1) to see cases dataframe")
    print("Press (2) to run decision tree on a single case")
    print("Press (3) to run rules on single case")
    print("Press (4) to run rules on all cases")
    print("Press (5) to see all rules")
    print("Press (6) to clear rules")
    print("Press (7) to clear conclusions")
    print("Press (8) to show decision path of decision tree")
    #print("Press (q) to quit")
    i = int(input())
    if i == 0:
        X = df.iloc[:,1:-4] # leave out last 3 columns (4 and dont give name)
        Y = df.iloc[:,-2] # take target as encoded column - note: all values must be numeric - hence encoded
        Y=Y.astype('int')
        #print(X)
        #print(Y)
        # split data and train dt
        X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=1, stratify = Y)
        dt = DecisionTreeClassifier()
        dt = dt.fit(X_train, y_train)
        # show the dt - in file
        #tree.plot_tree(dt) # doesnt work
        feature_names = df.columns.values[1:-4] # leave out last 3 columns (4 and dont give name)
        target_names = np.unique(df['target'].values) # unique target values - sorted (for some reason)
        #tree.export_graphviz(clf, out_file=dot_data) #le.inverse_transform(list(transformed))
        dot_data = StringIO()
        # Note: the value array puts the encoded in numeric order
        export_graphviz(dt, out_file=dot_data, feature_names=feature_names, class_names=target_names , filled=True)
        (graph, ) = graph_from_dot_data(dot_data.getvalue())
        # print(dot_data.getvalue()) - dot data - print to find node numers in dt
        graph.write_png('tree2.png')
        Image(graph.create_png())
        print("\nDecision tree trained\n")
        #predict
        y_pred = dt.predict(X_test)
        #confusion matrix
        #species = np.array(y_test).argmax(axis=0)
        #predictions = np.array(y_pred).argmax(axis=0)
        #confusion_matrix(species, predictions)
    # print cases dataframe
    elif i == 1:
        print_full(df)
    # run dt on case
    elif i == 2:
        case = input("Which case to run on the decision tree?\n").lower()
        prediction = predict_case(dt, case)    
        print(f"\nDecision tree classification: {prediction}\n") 
    # run rules on a single case
    elif i == 3:
        # TODO add check if case is legit
        case = input("Which case to run?\n").lower()
        # run through rules for case. will put conclusion in df in there is one. r = the last rule used
        last_rule = run_case(case)
        # get target value amd conclusion value - test if equal
        caserow = df.loc[df["name"] == case]
        target = caserow.iloc[0]["target"]
        con = caserow.iloc[0]["conclusion"]
        print(f"\nIs the conclusion correct for case {case} (target == conclusion)?")
        # conclusion correct - nothing to be done
        if target == con:
            print("\nConclusion correct\n")
        # conclusion missing - add new cornerstone case
        elif con == "-":
            print("\nConclusion missing\n")
            print(f"Add a cornerstone rule to correctly classify {case}")
            rule, conclusion = enter_new_rule()
            add_cornerstone_rule(rule, conclusion, conclusion, None, case, rules_count)
            rules_count += 1 
        # conclusion incorrect - add refinement rule
        else:
            print("\nConclusion incorrect\n")
            print(f"Add a refinement rule to correctly classify {case}\n")
            add_refinement_rule(last_rule, case, rules_count)
            rules_count += 1 
    # run rules on all animals
    elif i == 4:
        # train model before this step
        # for each case
        for case in df['name']:
            # run case through dt and observe prediction 1
            print(f"Case: {case}")
            pred1 = predict_case(dt, case)    
            print(f"Decision tree classification: {pred1}") 
            # run case through rules and observe prediction 2
            last_rule = run_case_no_prints(case)
            caserow = df.loc[df["name"] == case]
            pred2 = caserow.iloc[0]["conclusion"]
            print(f"RDR classification: {pred2}") 
            # if match - move to next case
            # else - add a new rule to give prediction 1 for case
            if pred1 == pred2:
                print("Conclusion correct. Move onto next case\n")
            # conclusion missing - add new cornerstone rule
            elif pred2 == "-":
                print("Conclusion missing. The rules application is shown below: \n")
                run_case(case) # run case again just to print
                print(f"\nAdd a new cornerstone rule to correctly classify {case}\n")
                rule, conclusion = enter_new_rule()
                add_cornerstone_rule(rule, conclusion, conclusion, None, case, rules_count)
                rules_count += 1
                print("New cornerstone rule added:")
                n = rules_list[rules_count]
                print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}\n'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))
                break
            # conclusion incorrect - add refinement rule
            else:
                print("Conclusion incorrect. The rules application is shown below: \n")
                run_case(case) # run case again just to print
                print(f"\nAdd a refinement rule to correctly classify {case}\n")
                add_refinement_rule(last_rule, case, rules_count)
                rules_count += 1 
                break
            # if prediction 1 == prediction 2:
                # continue
            # else:
                # add a new rule to give prediction 1 for case
    # possibility for new loop: start action on a specific case:
    # for case in df['name']:
    # if name != name && flag ==- true: continue
    # if name == name: flag == false. now do stuff
    # print rules and their branches
    elif i == 5:
        print("Rules")
        #print("Number\tRule\t\tConclusion\t\tTRUEBranch\t\tFALSEBranch\t\tCase")
        print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format("Number", "Rule", "Conclusion", "TRUEBranch", "FALSEBranch", "Case", "true_cases"))
        i = 1
        while i <= rules_count:
            n = rules_list[i]
            #print(f"{n.num}\t{n.data}\t\t{n.con}\t\t{n.nextTrue}\t\t{n.nextFalse}\t\t{n.case}")
            print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))
            i += 1
    # clear all rules
    elif i == 6:
        rules_count = 0
        rules_list = rules_list = [None] * 100
    # clear dataframe
    elif i == 7:
        df['conclusion'] = '-'
    # show decision path of decision tree
    elif i == 8:
        # decision path experiment
        dt_path = dt.decision_path(X)
        decision_path_list = list(dt_path.toarray())
        print("Full matrix - a 1 at (x, y) corresponds to node y in dt being used for case x")
        print("Find node numbers by printing out dot data")
        for path in decision_path_list:
            print(path)
        print("Co-ordinates for 1's in matrix only")
        print(dt_path)
    else: 
        exit()

#for each case
    # train dt model
    # get a case
    # run case through dt and observe prediction 1
    # run case through rules and observe prediction 2
    # if prediction 1 == prediction 2:
        # continue
    # else:
        # add a new rule to give prediction 1 for case

""" 
code to encode a string as an int
m = "mammal"
mBytes = m.encode("utf-8")
mInt = int.from_bytes(mBytes, byteorder="big")
mBytes = mInt.to_bytes(((mInt.bit_length() + 7) // 8), byteorder="big")
m = mBytes.decode("utf-8") """            

#print(df.query('milk == 0 and name == "frog"')) # only show rows with animals which have milk == 1
#print(df.query('milk == 1')[['name','milk']]) # same but only show columns named

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

""" class SLinkedList:
def __init__(self):
    self.head = None
    self.count = 1

def listprint(self):
    printval = self.head
    while printval is not None:
        print (printval.data)
        print("Then")
        print(printval.nextTrue)
        printval = printval.nextFalse """
""" # rules: linked list of rules
rules = SLinkedList()
# 1 rule
rules.head = Node("milk==1")
rules.head.number = rules.count
# Link first Node to second node
rules.head.nextTrue = "mammal"
rules.head.nextFalse = None
rules.count += 1
"""
#https://www.w3resource.com/pandas/dataframe/dataframe-query.php
#https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/