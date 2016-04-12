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
    v = f.getVector(l, r, allFuncs=True)
    if "?MATCH" in match_status:
        label = 1
    else:
        label = -1
    # Now append the feature vector + label to our data structures
    training_data.append(v)
    labels.append(label)
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
unknown = 0
dataset_count = 0

# Open the file with the full dataset
dataset_fp = sys.argv[2]
dataset_fd = open(dataset_fp, mode='r', encoding="latin-1")

# Set up the training data
print("Analyzing the testing dataset...");
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
    v = f.getVector(l, r, allFuncs=True)
    match_vector = clf.predict_proba([v])
    if "?MATCH" in match_status:
        label = 1
    if "?MISMATCH" in match_status:
        label = -1
    if match_vector[0][0] > 0.65:
        match_guess = -1
    if match_vector[0][1] > 0.65:
        match_guess = 1
    if match_vector[0][1] < 0.65 and match_vector[0][0] < 0.65:
        match_guess = 0
        unknown += 1
    if match_guess == 1:
        if match_guess == label:
            true_positives += 1
        else:
            false_positives += 1
    elif match_guess == -1:
        if match_guess == label:
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
print("Precision:", precision)
print("Recall:", recall)
print("True positives:", true_positives)
print("False positives:", false_positives)
print("True negatives:", true_negatives)
print("False negatives:", false_negatives)
print("Unknown values:", unknown)
print("Computation time:", str(diff_time.total_seconds()/60.0), " minutes")

