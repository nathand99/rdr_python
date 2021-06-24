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

list = SLinkedList()
list.headval = Node("if milk == 1")
# Link first Node to second node
list.headval.nexttrue = "mammal"

e2 = Node("if aquatic == 1")
list.headval.nextfalse = e2
e2.nexttrue = "fish"
e2.nextfalse = None

print("2 rules")
list.listprint()
print()
print("added a new rule")
e3 = Node("if aquatic == 1 and teeth == 10")
e3.nexttrue = "shark"
e3.nextFalse = None
# gotta fix up rule above
e2true = e2.nexttrue
e2.nexttrue = e3
e3.nextfalse = e2true
# Link second Node to third node
#e2.nextval = e3

list.listprint()