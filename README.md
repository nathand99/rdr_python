# rdr_python

### Background
---
### Setup
---
### Description
---
### Walkthrough

The following walkthrough is an extract from the final thesis report detailing a walkthrough of an example use of the system. The "animalsmodified.csv" dataset (included in this repository) is used for this walkthrough. In the walkthrough, a sample use of the system is demonstrated for this dataset.

In a terminal, if we run the python program using python3, we are greeted with the following screen:

![image](https://user-images.githubusercontent.com/47731415/144803525-edc35015-cf2a-40e8-b776-0f2880cc5b50.png)
Figure 26 – user inputs CSV file name which is to be imported

We are prompted to input the name of the CSV (comma separated values) file which is to be imported into the system. There are multiple conditions that must be met for this file. The file must be a CSV file and have a .csv format in its name. The first column must be called “name’ and contain the name of each case. The last column must be called “target” and contain the labels for each case. The labels must be of type string due to label encoding. The data (all columns in between the first and last column) must contain numeric data only. There must be no missing values. Examples on how to edit CSV files into a format suitable for this program are provided in this project’s GitHub repository. [3]
 
![image](https://user-images.githubusercontent.com/47731415/144803551-1207d50a-bf10-41a3-b07c-56650002af0a.png)

Figure 27 - user inputs a number corresponding to the black box classifier they want to use as a black box

After entering the CSV file to be used, we now must select a classifier to be used as the black box classifier. The selection can be changed later as all classifiers are trained when the program starts (as shown in Figure 27). For this example, option 2 - random forest is chosen.
We are now shown a menu screen containing all options available to a user. 
 
![image](https://user-images.githubusercontent.com/47731415/144803580-91394f7f-76e8-4951-b83a-5528f1b63faa.png)
Figure 28 - menu screen

Entering 1 (and pressing enter), the user is shown the dataframe of cases.
 
![image](https://user-images.githubusercontent.com/47731415/144803613-750b1a0b-eb03-4c10-ac25-7a2a9cb25eaa.png)
Figure 29 - dataframe of cases

Figure 29 shows a truncated version of the dataframe containing the rows of animals and their data as well as the 2 added columns, an encoded version of the target and empty conclusion column. Note: for this demonstration, there is a large amount of truncation in the images shown in order allow the text in these images to be readable. When using the program, if the terminal is enlarged before entering options on the menu screen, the user would be shown more information.

Now it is time to add some rules. The option which provides the implementation of the high-level algorithm is option 4 – run rules on all cases. Press 4.

![image](https://user-images.githubusercontent.com/47731415/144803637-f902ea37-246a-4788-af4b-436cf098e759.png)
Figure 30 - the first case

As described by the option description, the rules are run on all the cases in the dataframe. The first case in the dataframe is the aardvark. The black box prediction is mammal, but the RDR classification is “-“ (or none). This is because when we begin, there are zero rules in the system. Next, the user is told that the conclusion is missing and is shown the application of the rules on the case which led to this classification. However, as stated, there are zero rules currently, so there is no rules application. The user is then shown the aardvark case and instructed to add a new cornerstone rule. A cornerstone rules means that no rules are true for this case so therefore it has no classification.

To enter a new rule, the user must first enter an attribute. We know from before that milk is a defining attribute for mammals, so write “milk”.

![image](https://user-images.githubusercontent.com/47731415/144803657-efc9e7f0-189c-442f-a25e-970a115b8915.png)

Figure 31 - adding a new rule

Next, an operator is required. The operators available are: ==, >, <, >=, <=. We will choose ==. Next the value we will choose 1 to make the rule: if milk == 1. It is also possible to add another condition, for example: if milk == 1 AND feathers == 0. However, this single condition will suffice in this case so we enter “n” to decline this option. After this we enter the conclusion that the rule will give as a classification. For this rule, we need to classify as a mammal as the black box predicts so choose mammal. After confirming our rule, it is added and we are taken to the menu. At the menu we can press option 5 to see all rules.

![image](https://user-images.githubusercontent.com/47731415/144803674-687bed2d-a8b2-4234-bfbd-5b0920320a33.png)
Figure 32 - the single rule that has been added

The single rule we have made appears. True_cases is also an attribute of a rule that would be displayed here but it has been omitted to save space.

If we press 4 again, the rules are run on all the cases just as before, but this time, there is a rule in the ruleset – the one we just created.

![image](https://user-images.githubusercontent.com/47731415/144803688-17daa23a-178b-42e6-9a47-22ae07f49a34.png)

Figure 33 - the aardvark and antelope and now correctly classified

The aardvark is now correctly classified as a mammal by the rule that was just created. When a case is classified correctly, we move to the next case – just as shown in the system architecture diagram. The antelope is the next case and it is also correctly classified as a mammal by our rule. The next case is the bass.

![image](https://user-images.githubusercontent.com/47731415/144803706-10d92182-af66-4558-bce1-3a7715dad526.png)

Figure 34 - the fish is not classified by our 1 rule

The bass however has no conclusion given by the RDR – just like we saw with the aardvark when we first saw it. As with the aardvark, the rules application is shown, this time with a rule. When the rule milk == 1 is applied to the bass, this is false – therefore the false branch os taken. As shown in the rules print out, the false branch for this rule is none – so no classification is given. We must now add a cornerstone rule to classify the fish. We add the rule as follows (note: fins == 1 for the bass):

![image](https://user-images.githubusercontent.com/47731415/144803715-bec6966b-c92e-497c-b56a-28e1141434e9.png)

Figure 35 - entering a rule to classify the bass

We add a rule on fins for the bass to classify it as a fish – the classification given by the “black box” classifier. We now have 2 rules in the ruleset, which can be seen by pressing 5.

![image](https://user-images.githubusercontent.com/47731415/144803734-f93aa874-f6b9-4b12-9b73-a606b7764006.png)
Figure 36 - there are now 2 rules in the system

As you can see, the FALSEBranch for rule 1 has been updated to point to the second rule – the rule we just added. Now when milk is not equal to 1 for a case, the next cornerstone rule is applied, which if successful, will classify the case as a fish. If both rules are false for a case, then we will have no conclusion and we need to add a new cornerstone rule.

Choosing the fourth option 2 more times will make the user make 2 more cornerstone rules to classify cases which have no RDR classification. After adding 4 rules, looking at all the rules looks like this:

![image](https://user-images.githubusercontent.com/47731415/144803758-2ac65d70-b7e6-4a33-9634-465f35d192e0.png)
Figure 37 - the ruleset after adding 3 more rules

Since all 4 rules are cornerstone rules, if the rule is false for a case, we simply apply the next rule in the ruleset.

Now when running option 4 once more, we are presented with the case “flea”. 

![image](https://user-images.githubusercontent.com/47731415/144803765-77ec5a3f-7cdb-43cf-aead-280bfe076722.png)
Figure 38 - incorrect RDR conclusion

The black box prediction is insect whereas the RDR classification is mollusc. Therefore, the RDR rules have got this case’s classification wrong, meaning a refinement rule must be added to correct this mistake. The system now shows us the application of all the rules in the system. The first rule to be applied was the first rule we added, a rule on milk. Unfortunately, in figure 38, the value for milk for the flea is omitted due to an effort to make the output readable in this paper. The value for the rule milk == 1 for the flea is, as shown by the output, false. The false branch, as shown in the ruleset (in figure 37) is rule 2. Rule 2 is on fins. Again, this is excluded from Figure 38, but it is 0 for the flea. Going to the false branch we apply rule 3, a rule on feathers. As can be seen, this value is 0 for the flea so again we go down the false branch. The final rule, backbone = 0 is true for the flea, so it is classified as a mollusc. 

![image](https://user-images.githubusercontent.com/47731415/144803777-f6bb8f9d-84d1-44a2-82cf-1aa61f496f2d.png)
Figure 39 - rules application for the flea

But this conclusion of mollusc is different to the black box classification of insect - so a refinement rule must be added.

![image](https://user-images.githubusercontent.com/47731415/144803791-c2025cf9-a084-4721-b30f-6b89cc7da592.png)
Figure 40 - the system gives assistance to the user making a rule

The system now shows us all the rules that are true for this case. In this case it is a single rule, rule 4, which makes a rule on the attribute “backbone”. Therefore, since this rule is true, there is no point in making a rule in terms of backbone. Now the system attempts to help us find an attribute to make a rule on by listing all the attributes that are different between this case (the flea) and the case the true rule was made on (the clam). The new rule must involve features that are different to ensure that the rule already true applies for the case it was made on (since it classifies this case correctly), and the refinement rule only works on this rule. 

Now we need to enter the refinement rule. We choose the attribute “no of legs” from the provided list and make the rule as follows:

![image](https://user-images.githubusercontent.com/47731415/144803802-65c3482f-f7a7-4148-a139-9bd8ee93c58b.png)

Figure 41 - creating the refinement rule

Now we have a refinement rule that correctly classifies the flea as an insect. 

![image](https://user-images.githubusercontent.com/47731415/144803811-70d55ae5-7b82-4219-aa54-fa415aaa497f.png)

Figure 42 - the ruleset after adding 5 rules

In Figure 42, we can see that rule 4’s TRUEBranch and FALSEBranch values have been modified by this action. Previously, if rule 4 was true, then a classification of mollusc was returned. But the refinement rule added to this rule changes this. Now when backbone == 0 is true for a case, we go to rule 5 and evaluate it. If rule 5 is true, like it was for the flea, then we are given a classification of insect. However, if it is false, the classification which was originally made for rule 4 – mollusc – is returned. The false branch of rule 4 retains a value of none. This all means that rule 5 will always but only we applied if rule 4 is true – as it is a refinement rule.

If we continue adding rules until every single animal in the animals dataset is classified correctly, this is a ruleset that we may finish on:

![image](https://user-images.githubusercontent.com/47731415/144803823-a2789b54-abcf-4254-b307-c2fc72ed860b.png)

Figure 43 - a ruleset that correctly classifies all cases
With this print out of the ruleset, we have created an explainable model that explains the predictions of the “black box” classifier. 

Now let’s go over some of the other options in the menu. Option 2 runs the black box classifier on a case inputted by the user.
 
![image](https://user-images.githubusercontent.com/47731415/144803844-8feb6192-3f55-4606-82f3-18d1c7af30a7.png)

Figure 44 - running the black box on case bear

As is intended, this classification gives no information regarding how the black box reached its conclusion. To see an explainable version of this, we can use our RDR model to explain this prediction. Choosing option 3 will run the rules on a single case which is inputted by the user, explaining the application of the rules as makes a classification.

![image](https://user-images.githubusercontent.com/47731415/144803858-f2976c81-38ef-4c99-a7c9-81f8940fd54f.png)
Figure 45 - the rules application for case bear

As we can see in Figure 45 above, the bear was classified as a mammal because of rule 1 which is IF milk == 1, THEN mammal. We the user can clearly see that the RDR ruleset reaches the classification of mammal because for the bear, milk == 1. In this case, the interpretable model has explained to the user how the conclusion was reached.

Now for the rest of the options in the menu:
6.	Clears all the rules in the ruleset. If there are rules in the ruleset, they are removed and the user is placed back in the beginning as if the program was just run
7.	Clears all conclusions in the “conclusion” column in the dataframe which are placed there when the RDR gives a classification of a case
8.	Shows the decision path of the decision tree of a particular case as described in chapter 4. Note: since all classifiers are trained as the program started, it does not matter which black box was selected at the program start, options 8, 9 ,10 can be run at any time.
9.	Shows the feature importances given by the random forest as shown in chapter 4. The graphs shown in chapter 4 are shown to the user and also saved as PNG files.
10.	Shows the feature importances graphs given by XGBoost as shown in chapter 4 and saves them as PNG files.
11.	Shows an evaluation of the system. This will be discussed later this chapter in 5.4.
12.	Run all the rules on all the cases without stopping to create a rule if a case is not classified or classified incorrectly. It is very similar to option 4, except no rules are added. After all the cases have been run through, an accuracy of the ruleset is calculated and shown to the user. For example, after adding the 5 rules shown in this walkthrough, this is the resulting accuracy of the rules:

![image](https://user-images.githubusercontent.com/47731415/144803875-05c11ba0-f6e3-4381-b8c6-edb5570c9f98.png)

Figure 46 - accuracy of rules on animals dataset after adding 5 rules

13.	Run 10-fold cross validation using all three black boxes and print the accuracy of each one for the current dataset. This may be useful when deciding if a dataset should be used for this system. Only datasets which give a high accuracy for the black boxes should be used for this system. The animals dataset accuracies are shown below. It has a high accuracy so is suitable for this system.

![image](https://user-images.githubusercontent.com/47731415/144803883-2f3d19fd-b0c4-4682-97f3-bafe1e4b344a.png)

Figure 47 - accuracy results for 10-fold cross validation on the animals dataset

14.	Save the current ruleset to a file or load a ruleset from a file. Note: only works for data in integer and/or string form.
15.	Change the black box classifier that is used in options 2 and 4.
