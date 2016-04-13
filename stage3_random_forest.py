__author__ = 'wintere'

import datetime
import re
import json
import sys
from feature_operations import FeatureGenerator
from sklearn import ensemble
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2


# # put the proper file path to the pairs source here
if len(sys.argv) != 3:
    print("Usage: python stage3_decision_tree.py <training data filename> <test data filename>")
    exit()

# fetch page and split into tuples
training_fp = sys.argv[1]
training_fd = open(training_fp, mode='r', encoding="ascii", errors='ignore')

# there might be a better way to do this than the split library...
jumbo_pattern =  r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'
training_samples = 0
training_data = []
labels = []

dataset_count = 0

start_time = datetime.datetime.now()

# Set up the training data
print("Setting up training data...")
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
    # Now append the feature vector + label to our data structures
    if "?MATCH" in match_status:
        label = 1
    else:
        label = -1
    training_data.append(v)
    labels.append(label)
    training_samples += 1
    
training_fd.close()
print("Finished setting up " + str(training_samples) + " training samples!")

# Set up a decision tree classifier using the data passed in
clf = ensemble.RandomForestClassifier()
clf = clf.fit(training_data, labels)
correct_guesses = 0
guesses = 0
unknown = 0
true_positives = 0
true_negatives = 0
false_positives = 0
false_negatives = 0
testing_size = 0

# Open the file with the full dataset
dataset_fp = sys.argv[2]
dataset_fd = open(dataset_fp, mode='r', encoding="ascii", errors='ignore')

# Set up the training data
print("Analyzing the testing dataset...")
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
    if match_vector[0][0] > 0.5:
        match_guess = -1
    if match_vector[0][1] > 0.5:
        match_guess = 1
    if match_vector[0][1] == 0.5:
        unknown += 1
        match_guess = 0
    if match_guess == 1:
        if match_guess == label:
            true_positives += 1
            correct_guesses += 1
        else:
            false_positives += 1
        guesses += 1
    elif match_guess == -1:
        if match_guess == label:
            true_negatives += 1
            correct_guesses += 1
        else:
            false_negatives += 1
        guesses += 1
    testing_size += 1
dataset_fd.close()
    
# Calculate end results
end_time = datetime.datetime.now()
diff_time = end_time - start_time
precision = float (correct_guesses)/(guesses)
recall = float(correct_guesses)/(testing_size)

# CSV stats
print("Precision:", precision)
print("Recall:", recall)
print("True positives:", true_positives)
print("False positives:", false_positives)
print("True negatives:", true_negatives)
print("False negatives:", false_negatives)
print("Unknown values:", unknown)
print("Computation time:", str(diff_time.total_seconds()/60.0), " minutes")

