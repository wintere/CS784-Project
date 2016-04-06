__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict
from feature_operations import FeatureGenerator
from sklearn import tree

# # put the proper file path to the pairs source here
if len(sys.argv) != 3:
    print("Usage: python stage3_decision_tree.py <training data filename> <full dataset filename>")
    exit()

# fetch page and split into tuples
training_fp = sys.argv[1]
training_fd = open(training_fp, mode='r')

# regular expressions to divide data into pairs of tuples: tested to pull out values on all 20,000 tuples
id_pattern =r'\d+-\d+#[\w. -]+\?\d+\?'
comp2_pattern = r'\?\d+#[\w. -]+\?'
match_pattern = r'\?MATCH|\?MISMATCH'

# there might be a better way to do this than the split library...
jumbo_pattern =  r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'
training_samples = 0
training_data = []
labels = []


# Set up the training data
print("Setting up training data...");
f = FeatureGenerator()
for line in training_fd:
    # Split line into 3 important parts (tuple1, tuple2, label)
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]
    
    # Set up the feature vector for these tuples
    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    ln = l['Product Name']
    rn = r['Product Name']
    if 'stress testing item' in ln[0].lower() or 'stress' in rn[0].lower():
        print("Skipped stress testing item.")
    else:
        v = f.getVector(l, r)
        #print(v, match_status)
        # Now append the feature vector + label to our data structures
        training_data.append(v)
        labels.append(match_status)
        training_samples += 1        
    
training_fd.close()
print("Finished setting up " + str(training_samples) + " training samples!")

# Set up a decision tree classifier using the data passed in
clf = tree.DecisionTreeClassifier()
clf = clf.fit(training_data, labels)

# MC: The following code is mostly a copy of the first half, we should refactor.

true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0
dataset_count = 0

# Open the file with the full dataset
dataset_fp = sys.argv[2]
dataset_fd = open(dataset_fp, mode='r', encoding="latin-1")

# Set up the training data
print("Analyzing the full dataset...");
for line in dataset_fd:
    # Split line into 3 important parts (tuple1, tuple2, label)
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]
    
    # Set up the feature vector for these tuples
    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    ln = l['Product Name']
    rn = r['Product Name']
    if 'stress testing item' in ln[0].lower() or 'stress' in rn[0].lower():
        true_negatives += 1
    else:
        dataset_count += 1
        v = f.getVector(l, r)
        match_guess = clf.predict([v])
        if match_guess == match_status:
            true_positives += 1
        elif match_guess != match_status:
            false_positives += 1
                 
    
dataset_fd.close()

# Output some results
precision_percent = true_positives * 100 / (true_positives + false_positives)

print("Finished analyzing " + str(dataset_count) + " data records")
print("True positives: " + str(true_positives))
print("False positives: " + str(false_positives))
print("Precision: " + str("%.2f" % precision_percent) + "%")

