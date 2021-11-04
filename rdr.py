import numpy as np 
import pandas as pd
from sklearn import preprocessing, tree
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from six import StringIO 
from IPython.display import Image 
from pydot import graph_from_dot_data
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance
import time

class Node:
    def __init__(self, num=None, data=None, con=None, nextTrue=None, nextFalse=None, case=None, true_cases=[]):
        self.num = num # rule number - starts at 1
        self.data = data # if milk == 1
        self.con = con # mammal
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
        print("if: ")
        rule = ""
        while(1):
            attribute = input("Enter an attribute: ")
            operator = input("Enter an operator: ")
            value = input("Enter an value: ")
            more = input('Add another condition? (Y/n): ')
            if more.lower() == 'y':
                op = input('and/or: ').lower()
                rule += f"`{attribute}` {operator} {value} {op} "
                continue
            else:
                rule += f"`{attribute}` {operator} {value}"
                break
        print("then: ")
        conclusion = input("Enter a conclusion: ")
        print("Rule entered:")
        #rule = f"if {attribute} {operator} {value} then {conclusion}"
        full_rule = "if " + rule + " then " + conclusion
        print(full_rule)
        correct = input("Is the rule correct (y/n)? ")
        #print(rule)
        if correct.lower() == 'y':
            return rule, conclusion
        else:
            abort = input("Retry? (y) or abort(n)? (y/n)")
            if abort.lower() == 'n':
                print("Aborting adding new rule")
                return -1
            else:
                continue

# functions involving df
# run through rules for a single case - modifys conclusion for case if needed
def run_case(df, case):
    n = rules_list[1]
    # print case if no rules
    if n is None:
        print(df.query("name==" + "'" + case + "'"))
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
                add_conclusion(df, case, branch)
                return n
            elif branch == None:
                print("\nEnd of rules reached. No conclusion\n")
                return
            else:
                n = rules_list[branch]

# run_case function but with no print statements
def run_case_no_prints(df, case):
    n = rules_list[1]
    while n is not None:
        # n is a node in rules_list
        if isinstance(n, Node):
            # print case for user
            query = "name==" + "'" + case + "'" + " and " + n.data
            # query this case for rule
            #print(query)
            result = df.query(query) 
            # if empty - no result - rule is not true for this case - goto false branch
            if result.empty == True:
                branch = n.nextFalse
            # if not empty - rule is true - goto true branch
            else:
                branch = n.nextTrue
            # deal with branch. Could be string->conclusion, None->No conclusion, index->keep going
            if isinstance(branch, str):
                add_conclusion_no_prints(df, case, branch)
                return n
            elif branch == None:
                return
            else:
                n = rules_list[branch]

# find rules that are true to lead to give case
def find_true_rules(df, rules_list, case):
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
def add_conclusion(df, case, conclusion):
    print(f"\nConclusion reached: {conclusion}\n")
    df.loc[df["name"] == case, 'conclusion'] = conclusion
    print(df.query("name==" + "'" + case + "'")) # print case for user
    return

# add_conclusion - with no prints
def add_conclusion_no_prints(df, case, conclusion):
    df.loc[df["name"] == case, 'conclusion'] = conclusion
    return

# predict case using black box (bb) and dataframe (df)
def predict_case(df, bb, case):
    # xgboost uses a dmatrix instead of dataframe
    if bb == bst:
        # create the dmatrix needed for xgboost
        dmatrix = xgb.DMatrix(X, label=y)
        # get dataframe index of given case
        index = df.index[df['name']==case].tolist()[0]
        # ypred gives an array of numbers - round these numbers to get the encoded values
        ypred = bb.predict(dmatrix)
        # inverse transform these numbers to get the class
        r = list(le.inverse_transform([round(ypred[index])]))
        return r[0]
    else:
        c = df.loc[df["name"] == case]
        c = c.iloc[:,1:-3]
        r = bb.predict(c) # gives an encoded array
        r = le.inverse_transform(r) # unencode it
        return r[0]

# add new rule to rules_list - cornerstone. true_cases = []. returns an updated rules_list
def add_cornerstone_rule(rule, conclusion, nextTrue, nextFalse, case, rules_count, rules_list):
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
    return rules_list

# returns an updated rules_list
def add_refinement_rule(last_rule, case, rules_count, rules_list, df):
    # find which branch is taken - which gives incorrect result
    query = "name==" + "'" + case + "'" + " and " + last_rule.data
    result = df.query(query) 
    # if empty - goto false branch
    if result.empty == True:
        branch = False
    else:
        branch = True
    # find rules which are true for case
    true_list = find_true_rules(df, rules_list, case)
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
        limit = 10
        for col in df3.columns:
            if col == "conclusion" or col == "target" or col == "encoded" or col == "name":
                continue
            if len(df3[col].value_counts()) > 1:
                print(col)
                limit -= 1
                if limit == 0:
                    print("(max 10 examples reached - there may be more)")
                    break
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
    return rules_list

# let the user choose which "black box" classifier
def choose_black_box():
    print(f"Choose which model to use as a \"black box\" classifier: ")
    print("Press (1) to use a decision tree")
    print("Press (2) to use a random forest")
    print("Press (3) to use xgboost")
    m = int(input())
    bb = dt # black box is decision tree by default
    # use decision tree (dt)
    if m == 1:
        bb = dt
    # use random forest (rf)
    elif m == 2:
        bb = rf
    else:
        bb = bst
    return bb

#############################################################################################################################
print("initialising rules_list and rules_count...", end='')
# initialise rules list and rule count
# rules list
# Node(rules_count, rule, conclusion, conclusion, last_rule.nextTrue, case, true_list)
NUM_RULES = 100 # magic number - max 100 rules
rules_list = [None] * NUM_RULES
time_list = [None] * NUM_RULES
# Note: rules_list[0] is always None - rules_list[1] is the head
# rules_count = increment before/after adding a new rule
#rules_count = 0
#rules_list[1] = Node(1, "`milk` == 1", "mammal", "mammal", 2, "aardvark", [])
#rules_count += 1
#rules_list[2] = Node(2, "`acquatic` == 1", "fish", "fish", None, "bass", [])
#rules_count += 1
rules_count = 0
print("Done")

# data imported must be csv file with:
# - the first row giving attribute names. 
# - the first column containing the names of each case. Labelled "name"
# - the last column containing the target class of each case. Labelled "target"
# - numeric data only. target values allowed to be text - they will be transformed
# care for missing or weird values
# an empty conclusion column will be added
filename = 'animalsmodified.csv'
print(f"importing data from {filename} into dataframe...", end='')
df = pd.read_csv(filename)
print("Done")

# add encoded column. encoded is used by sklearn as the target column 
# target values will be transformed to numeric in the encoded column 
# if target values are already numeric - copy to encoded
print(f"modifying dataframe by adding columns encoded and conclusion...", end='')
if df.dtypes['target'] == np.int64 or df.dtypes['target'] == np.float64:
    df['encoded'] = df['target']
else:
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

# add empty conclusion column as last column
df['conclusion'] = '-'
print("Done")

# separate data
X = df.iloc[:,1:-3] # X-values: leave out last 3 columns (target, encoded, conclusion) as well as first column (name)
y = df.iloc[:,-2].astype('int') # take target as encoded column (second last column). note: all values must be numeric - hence encoded
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1, test_size=0.20) # split with 80/20 train/test

# special df - need the names of cases in the test set (X_test doesn't contain names). random state keeps selections the same
# used in evaluation
specialX = df.iloc[:,:-3]
_, special_X_test, _, _ = train_test_split(specialX, y, random_state=1, test_size=0.20) # split with 80/20 train/test

# train decision tree
print(f"training decision tree as \"black box\" classifier...", end='')
dt = DecisionTreeClassifier()
dt = dt.fit(X, y)

# show the dt - in file
#tree.plot_tree(dt) # doesnt work
feature_names = df.columns.values[1:-3] # leave out last 3 columns (target, encoded, conclusion) as well as first column (name)
target_names = np.unique(df['target'].values) # unique target values - sorted (for some reason)
#tree.export_graphviz(clf, out_file=dot_data) #le.inverse_transform(list(transformed))
dot_data = StringIO()
# Note: the value array puts the encoded in numeric order
export_graphviz(dt, out_file=dot_data, feature_names=feature_names, class_names=target_names , filled=True)
(graph, ) = graph_from_dot_data(dot_data.getvalue())
# print(dot_data.getvalue()) - dot data - print to find node numers in dt
treefile = "tree2.png"
graph.write_png(treefile)
Image(graph.create_png())
print("Done")
#predict
#y_pred = dt.predict(X_test)
#confusion matrix
#species = np.array(y_test).argmax(axis=0)
#predictions = np.array(y_pred).argmax(axis=0)
#confusion_matrix(species, predictions)

# train random forest
print(f"training random forest as \"black box\" classifier...", end='')
rf = RandomForestClassifier() # using default parameters (100 trees)
rf = rf.fit(X, y)
print("Done")

# train xgboost
print(f"training xgboost as \"black box\" classifier...", end='')
# xgboost uses a dmatrix instead of a dataframe
dmatrix = xgb.DMatrix(X, label=y, feature_names=feature_names)
num_round = 10
bst = xgb.train([], dmatrix, num_round, [])
bst.save_model('xgboostmodel.model')
#xgb.plot_tree(bst, num_trees=2)
print("Done\n")

# choose bb model
bb = choose_black_box()

# prompt loop
while (True):
    print(f"Welcome to python RDR")
    print("Press (1) to see cases dataframe")
    print("Press (2) to run black box classifier on a single case")
    print("Press (3) to run rules on single case")
    print("Press (4) to run rules on all cases")
    print("Press (5) to see all rules")
    print("Press (6) to clear rules")
    print("Press (7) to clear conclusions")
    print("Press (8) to show decision path of decision tree")
    print("Press (9) to show feature importances from random forest")
    print("Press (10) to show feature importances from xgboost")
    print("Press (11) for evaluation")
    print("Press (12) to save/load rules_list to/from a file")
    print("Press (13) to change black box model")
    #print("Press (q) to quit")
    i = int(input())
    # print cases dataframe
    if i == 1:
        print(df)
    # run bb on case
    elif i == 2:
        case = input("Which case to run on the black box? \n").lower()
        prediction = predict_case(df, bb, case)    
        print(f"\nBlack box classification: {prediction}\n") 
    # run rules on a single case
    elif i == 3:
        # TODO add check if case is legit
        case = input("Which case to run?\n").lower()
        # run case through black box and observe prediction 1
        print(f"Case: {case}")
        pred1 = predict_case(df, bb, case)    
        print(f"Black box classification: {pred1}") 
        # run case through rules and observe prediction 2 - this function includes prints unlike run on all cases
        last_rule = run_case(df, case)
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
            run_case(df, case) # run case again just to print
            print(f"\nAdd a new cornerstone rule to correctly classify {case}\n")
            rule, conclusion = enter_new_rule()
            rules_list = add_cornerstone_rule(rule, conclusion, conclusion, None, case, rules_count, rules_list)
            rules_count += 1
            print("New cornerstone rule added:")
            n = rules_list[rules_count]
            print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}\n'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))
            break
        # conclusion incorrect - add refinement rule
        else:
            print("Conclusion incorrect. The rules application is shown below: \n")
            run_case(df, case) # run case again just to print
            print(f"\nAdd a refinement rule to correctly classify {case}\n")
            rules_list = add_refinement_rule(last_rule, case, rules_count, rules_list, df)
            rules_count += 1 
            break
    # run rules on all animals
    elif i == 4:
        # for each case
        for case in df['name']:
            # run case through black box and observe prediction 1
            print(f"Case: {case}")
            pred1 = predict_case(df, bb, case)    
            print(f"Black box classification: {pred1}") 
            # run case through rules and observe prediction 2
            last_rule = run_case_no_prints(df, case)
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
                run_case(df, case) # run case again just to print
                print(f"\nAdd a new cornerstone rule to correctly classify {case}\n")
                start = time.time()
                rule, conclusion = enter_new_rule()
                end = time.time()
                rules_list = add_cornerstone_rule(rule, conclusion, conclusion, None, case, rules_count, rules_list)
                rules_count += 1
                time_list[rules_count] = end - start
                print("Time taken to add rule: {:.2f}s".format(time_list[rules_count]))
                print("New cornerstone rule added:")
                n = rules_list[rules_count]
                print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}\n'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))
                break
            # conclusion incorrect - add refinement rule
            else:
                print("Conclusion incorrect. The rules application is shown below: \n")
                run_case(df, case) # run case again just to print
                print(f"\nAdd a refinement rule to correctly classify {case}\n")
                rules_list = add_refinement_rule(last_rule, case, rules_count, rules_list, df)
                rules_count += 1 
                break
    # possibility for new loop: start action on a specific case:
    # for case in df['name']:
    # if name != name && flag == true: continue
    # if name == name: flag == false. now do stuff
    # print rules and their branches
    elif i == 5:
        print("Rules")
        #print("Number\tRule\t\tConclusion\t\tTRUEBranch\t\tFALSEBranch\t\tCase")
        #print('{:<12} {:<32} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}'.format("Number", "Rule", "Conclusion", "TRUEBranch", "FALSEBranch", "Case", "true_cases", "Time taken (s)"))
        print('{:<12} {:<32} {:<12} {:<12} {:<12} {:<12} {:<12}'.format("Number", "Rule", "Conclusion", "TRUEBranch", "FALSEBranch", "Case", "true_cases"))
        i = 1
        while i <= rules_count:
            n = rules_list[i]
            #print(f"{n.num}\t{n.data}\t\t{n.con}\t\t{n.nextTrue}\t\t{n.nextFalse}\t\t{n.case}")
            #print('{:<12} {:<32} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12.2f}'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases), time_list[i])) - put this back when timing is in save/load
            print('{:<12} {:<32} {:<12} {:<12} {:<12} {:<12} {:<12}'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))
            i += 1
    # clear all rules
    elif i == 6:
        rules_count = 0
        rules_list = rules_list = [None] * NUM_RULES
    # clear dataframe
    elif i == 7:
        df['conclusion'] = '-'
    # show decision path of decision tree
    elif i == 8:
        # decision path experiment
        dt_path = dt.decision_path(X)
        #decision_path_list = list(dt_path.toarray())
        #print("Full matrix - a 1 at (x, y) corresponds to node y in dt being used for case x")
        #print("Find node numbers by printing out dot data")
        #for path in decision_path_list:
        #    print(path)
        #print("Co-ordinates for 1's in matrix only")
        #print(dt_path)
        
        # size of dt
        print(f"Total number of nodes in tree: {dt.tree_.node_count}")   
        print(f"Number of leaf nodes in tree: {dt.tree_.n_leaves}") 
        print(f"Number of decision nodes in tree: {dt.tree_.node_count - dt.tree_.n_leaves}")  
        
        node_indicator = dt.decision_path(X) # the decision path in the tree - a matrix. 
        leaf_id = dt.apply(X) # id of leaf node for each case in X
        feature = dt.tree_.feature # numeric version of features used by dt
        features = [feature_names[i] for i in feature] # converted to feature names
        threshold = dt.tree_.threshold # thresholds for each node (rule)
        # get case name
        case = input("Which case name to show decision path?\n").lower()
        # turn case name into index (in dataframe)
        sample_id = df.index[df['name']==case].tolist()[0]
        # obtain ids of the nodes `sample_id` goes through
        node_index = node_indicator.indices[node_indicator.indptr[sample_id]:node_indicator.indptr[sample_id + 1]]
        print('Rules used to predict case {case} (sample {id}):\n'.format(id=sample_id, case=case))
        #help(tree._tree.Tree)
        for node_id in node_index:
            # leaf node - print the class (the most popular field in value whose index is in encoded)
            if leaf_id[sample_id] == node_id:
                print(f"node {node_id} is a leaf node, class:{list(le.inverse_transform([np.argmax(dt.tree_.value[node_id])]))[0]}")
                break
            # check if value of the split feature for sample 0 is below threshold
            if (X.iloc[sample_id, feature[node_id]] <= threshold[node_id]):
                threshold_sign = "<="
            else:
                threshold_sign = ">"
            """ print("decision node {node} : (X[{sample}, {feature}] = {value}) {inequality} {threshold})".format(
                    node=node_id,
                    sample=sample_id,
                    feature=features[node_id],
                    value=X.iloc[sample_id, feature[node_id]],
                    inequality=threshold_sign,
                    threshold=threshold[node_id])) """
            print("decision node {node} : (X[{sample}, {feature}] = {value}) {inequality} {threshold})".format(
                    node=node_id,
                    sample=sample_id,
                    feature=features[node_id],
                    value=X.iloc[sample_id, feature[node_id]],
                    inequality=threshold_sign,
                    threshold=threshold[node_id]))
            if threshold_sign == "<=":
                print(f"value for ({features[node_id]} <= {threshold[node_id]}) is TRUE. Go to TRUE branch - which is node {dt.tree_.children_left[node_id]}")
                #children_left[i]
            else:
                print(f"value for ({features[node_id]} <= {threshold[node_id]}) is FALSE. Go to FALSE branch - which is node {dt.tree_.children_right[node_id]}")
        print()
    # feature importances of random forest
    elif i == 9:
        importances = rf.feature_importances_
        importances_dictionary = dict(zip(feature_names, importances))
        sort_importances = sorted(importances_dictionary.items(), key=lambda x: x[1], reverse=True)
        print("Feature importance determined by random forest - most to least important for entire dataset")
        for i in sort_importances:
            print(f"{i[0]}: {i[1]}")
        print()
        print("saving plots of importances to files: randomforestfeatureimportancesMDI.png, randomforestfeatureimportancesMAD.png...", end='')

        # plot - MDI (mean decrease in impurity) - relatively stable
        std = np.std([
            tree.feature_importances_ for tree in rf.estimators_], axis=0)
        forest_importances = pd.Series(importances, index=feature_names)
        fig, ax = plt.subplots()
        forest_importances.plot.bar(ax=ax) #yerr=std - add horizontal / vertical errorbars to the bar tips. The values are +/- sizes relative to the data
        ax.set_title("Feature importances using MDI") 
        ax.set_ylabel("Mean decrease in impurity")
        fig.tight_layout()
        plt.savefig('randomforestfeatureimportancesMDI.png')
        plt.show()

        # plot - MAD (mean accuracy decrease) - a bit wild
        result = permutation_importance(
            rf, X, y, n_repeats=10, random_state=42, n_jobs=2)

        forest_importances = pd.Series(result.importances_mean, index=feature_names)
        fig, ax = plt.subplots()
        forest_importances.plot.bar(ax=ax)
        ax.set_title("Feature importances using permutation on full model")
        ax.set_ylabel("Mean accuracy decrease")
        fig.tight_layout()
        plt.savefig('randomforestfeatureimportancesMAD.png')
        print("Done\n")
    # get feature importance from xgboost
    elif i == 10:
        # using xgb.feature_importances_
        #plt.bar(feature_names, bst.feature_importances_)
        #xgboost0 = "xgboostfeature_importances_.png"
        #plt.savefig(xgboost0)
        #print(f"Saved feature importances plot 0 to file: {xgboost0}")
        print(bst.feature_names)
        print(bst.get_score(importance_type='weight'))

        # using xgb.plot_importance - weight
        xgb.plot_importance(bst, importance_type="weight", title="Feature importance - weight") #default is weight
        weightplot = "xgboostplot_importance_weight.png"
        plt.savefig(weightplot)
        print(f"Saved feature importances by weight to file: {weightplot}")
        # using xgb.plot_importance - gain
        xgb.plot_importance(bst, importance_type = "gain", title="Feature importance - gain")
        gainplot = "xgboostplot_importance_gain.png"
        plt.savefig(gainplot)
        print(f"Saved feature importances by gain to file: {gainplot}")
        # using xgb.plot_importance - cover
        xgb.plot_importance(bst, importance_type = "cover", title="Feature importance - cover")
        coverplot = "xgboostplot_importance_cover.png"
        plt.savefig(coverplot)
        print(f"Saved feature importances by cover to file: {coverplot}")
        plt.show()
        # custom feature importance - does the same as above
        #feature_important = bst.get_score(importance_type='weight')
        #keys = list(feature_important.keys())
        #values = list(feature_important.values())

        #data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by = "score", ascending=True)
        #data.plot(kind='barh')
        #xgboost1 = 'xgboostfeatureimportancecustom.png'
        #plt.savefig(xgboost1)
        #plt.show()
        #print(f"Saved feature importances plot 2 to file: {xgboost1}\n")
    
    # evaluation
    elif i == 11:
        print("Evaluation\n")
        # learning curve evaluation - using code from option 4
        # each time a rule is added, run the rules on the entire test set (meaning the running is not interrupted by incorrect rules)
        # take the number of correct cases each time
        # repeat
        correct_total = []
        incorrect_total = []
        while (1):
            for case in df['name']:
                # run case through black box and observe prediction 1
                print(f"Case: {case}")
                pred1 = predict_case(df, bb, case)   
                print(f"Black box classification: {pred1}") 
                # run case through rules and observe prediction 2
                last_rule = run_case_no_prints(df, case)
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
                    run_case(df, case) # run case again just to print
                    print(f"\nAdd a new cornerstone rule to correctly classify {case}\n")
                    rule, conclusion = enter_new_rule()
                    rules_list = add_cornerstone_rule(rule, conclusion, conclusion, None, case, rules_count, rules_list)
                    rules_count += 1
                    print("New cornerstone rule added:")
                    n = rules_list[rules_count]
                    print('{:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}\n'.format(n.num, n.data, n.con, str(n.nextTrue), str(n.nextFalse), n.case, str(n.true_cases)))
                    break
                # conclusion incorrect - add refinement rule
                else:
                    print("Conclusion incorrect. The rules application is shown below: \n")
                    run_case(df, case) # run case again just to print
                    print(f"\nAdd a refinement rule to correctly classify {case}\n")
                    rules_list = add_refinement_rule(last_rule, case, rules_count, rules_list, df)
                    rules_count += 1 
                    break
        
            # go through all cases in TEST SET, dont stop, count all correct RDR conclusions and incorrect conclusions
            print("\nTest rules on test set: ")
            correct = 0
            incorrect = 0
            for case in special_X_test['name']: # a X_test that has name
                print(f"Case: {case}")     
                pred1 = predict_case(df, bb, case)   
                print(f"Black box classification: {pred1}") 
                # run case through rules and observe prediction 2
                last_rule = run_case_no_prints(df, case)
                caserow = df.loc[df["name"] == case]
                pred2 = caserow.iloc[0]["conclusion"]
                print(f"RDR classification: {pred2}") 
                # if match - score += 1
                # else - none
                if pred1 == pred2:
                    print("RDR correct")
                    correct += 1
                else:
                    print("RDR incorrect")
                    incorrect += 1
        
            print(f"\nAfter adding {rules_count} rules: ")
            print(f"Correct classifications: {correct}")
            print(f"Incorrect classifications: {incorrect}\n")
            correct_total.append(correct)
            incorrect_total.append(incorrect)
            x_axis = np.arange(1, rules_count + 1)
            print(rules_count)
            print(x_axis)
            print(correct_total)
            print(incorrect_total)
            if incorrect == 0:
                print("All cases classified correctly by RDR")
                break
            input("Press enter to continue: ")
        # plot the evaluation
        plt.plot(x_axis, correct_total, label="correct")
        plt.plot(x_axis, incorrect_total, label="incorrect")
        plt.xlabel("Number of rules added")
        plt.ylabel("Number of correctly/incorrectly classified cases")
        plt.title("Learning curve evaluation")
        plt.legend()
        plt.savefig('learningcurve.png')
        plt.show()
        
    # save or read in rules_list
    elif i == 12:
        saveorload = input("Would you like to save or load rules? (s/l): \n").lower()
        if saveorload == "s" or saveorload == "save":
            print("WARNING: choose a name for a file that does not exist")
            name = input("Enter name of file to be saved to: \n").lower()
            f = open(name, "a")
            # first line is rules count
            f.write(f"{rules_count}\n")
            for n in rules_list:
                if n == None:
                    f.write("None\n")
                else:
                    f.write('{},{},{},{},{},{},{}\n'.format(n.num, n.data, n.con, n.nextTrue, n.nextFalse, n.case, n.true_cases))
            f.close()
            print(f"Rules in rules_list saved to file: {name}")
        else:
            print("WARNING: this operation will overwrite your current rules")
            name = input("Enter name of file to read rules from: \n").lower()
            f = open(name, "r")
            data = f.readlines()
            rules_list = [None] * NUM_RULES
            i = 0
            flag = True
            # go through all rules putting them in rules_list
            for n in data:
                # first line is rules count
                if flag:
                    rules_count = int(data[0])
                    flag = False
                    continue
                if n == "None\n":
                    i += 1
                else:
                    n = n.split("\n")
                    x = n[0].split(",")
                    # data is all strings. try to get an int, if that breaks take the string
                    try:
                        nt = int(x[3])
                    except:
                        nt = x[3]
                    try:
                        nf = int(x[4])
                    except:
                        nf = x[4]
                    tc = list(map(int, eval(x[6])))
                    rules_list[i] = Node(num=int(x[0]), data=x[1], con=x[2], nextTrue=nt, nextFalse=nf, case=x[5], true_cases=tc)
                    i += 1
    # change black box model
    elif i == 13:
        bb = choose_black_box()
    else: 
        exit()

######################################################################################################################
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
#https://www.kdnuggets.com/2019/06/select-rows-columns-pandas.html
#https://www.kdnuggets.com/2017/05/simplifying-decision-tree-interpretation-decision-rules-python.html