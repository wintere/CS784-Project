__author__ = 'wintere'

import datetime
import re
import json
import sys
from collections import defaultdict
from feature_operations import FeatureGenerator
from sklearn.linear_model import LogisticRegression

# # put the proper file path to the pairs source here
if len(sys.argv) != 3:
    print("Usage: python stage3_decision_tree.py <training data filename> <full dataset filename>")
    exit()

# fetch page and split into tuples
training_fp = sys.argv[1]
training_fd = open(training_fp, mode='r', encoding="latin-1")

# regular expressions to divide data into pairs of tuples: tested to pull out values on all 20,000 tuples
id_pattern =r'\d+-\d+#[\w. -]+\?\d+\?'
comp2_pattern = r'\?\d+#[\w. -]+\?'
match_pattern = r'\?MATCH|\?MISMATCH'

# there might be a better way to do this than the split library...
jumbo_pattern =  r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'
training_samples = 0
training_data = []
labels = []

start_time = datetime.datetime.now()

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
        test = 0 # do nothing print("Skipped stress testing item.")
    else:
        v = f.getVector(l, r)
        #print(v, match_status)
        # Now append the feature vector + label to our data structures
        training_data.append(v)
        labels.append(match_status)
        training_samples += 1        
    
training_fd.close()
print("Finished setting up " + str(training_samples) + " training samples!")

# Set up a logistic regression classifier using the data passed in
clf = LogisticRegression()
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
    dataset_count += 1
    v = f.getVector(l, r)
    
    # Predict the match status using our classifier
    match_guess = clf.predict([v])
    if match_guess == '?MATCH':
        if match_guess == match_status:
            true_positives += 1
        else:
            false_positives += 1
    else:
        if match_guess == match_status:
            true_negatives += 1
        else:
            false_negatives += 1

    
dataset_fd.close()

# Calculate end results
end_time = datetime.datetime.now()
diff_time = end_time - start_time
precision = float (true_positives)/(true_positives + false_positives)
recall = float(true_positives)/(true_positives + false_negatives)

# CSV stats
print("Data records,Precision,Recall,True positives,False positives,True negatives,False negatives,Execution Time")
print(str(dataset_count)+","+str(precision)+","+str(recall)+","+str(true_positives)+","+str(false_positives)+","+str(true_negatives)+","+str(false_negatives)+","+str(diff_time.total_seconds()))

