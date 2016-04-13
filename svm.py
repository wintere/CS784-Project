__author__ = 'wintere'

from sklearn import svm

import datetime
import re
import json
import sys
from collections import defaultdict
import random
from feature_operations import FeatureGenerator

 # put the proper file path to the pairs source here
if len(sys.argv) != 3:
    print("usage: <pointer to training file> <pointer to test file>")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
fp2 = sys.argv[2]
training = open(fp, mode='r', errors='replace')
test = open(fp2, mode='r', errors='replace')

jumbo_pattern =  r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'

training_data = []
labels = []

start_time = datetime.datetime.now()

f = FeatureGenerator()
clf = svm.SVC(probability=True)
for line in training:
    # split line into 5 parts described above
    seg = re.split(jumbo_pattern, line)

    # due to capturing groups we get more segments than we want
    id_string = seg[3]
    pair1_json = seg[4]
    pair2_id = seg[6]
    pair2_json = seg[8]
    match_status = seg[9]
    try:
        l = json.loads(pair1_json)
    except ValueError:
        print("invalid json string" + id_string)
    try:
        r = json.loads(pair2_json)
    except ValueError:
        print("invalid json string" + id_string)
    v = f.getVector(l, r, allFuncs=True)
    if "?MATCH" in match_status:
        label = 1
    else:
        label = -1
    # Now append the feature vector + label to our data structures
    training_data.append(v)
    labels.append(label)

training.close()
print("training loaded")
clf.fit(training_data, labels)

true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0
dataset_count = 0
unknown = 0

for line in test:
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]

    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    dataset_count += 1
    v = f.getVector(l, r, allFuncs=True)
    match_vector = clf.predict_proba([v])
    if "?MATCH" in match_status:
        label = 1
    if "?MISMATCH" in match_status:
        label = -1
    if match_vector[0][0] > 0.6:
        match_guess = -1
    if match_vector[0][1] > 0.6:
        match_guess = 1
    if match_vector[0][1] < 0.6 and match_vector[0][0] < 0.6:
        unknown += 1
        match_guess = 0
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
test.close()

# Calculate end results
end_time = datetime.datetime.now()
diff_time = end_time - start_time
precision = float (true_positives)/(true_positives + false_positives)
recall = float(true_positives)/(true_positives + false_negatives)

print("Precision:", precision)
print("Recall:", recall)
print("True positives:", true_positives)
print("False positives:", false_positives)
print("True negatives:", true_negatives)
print("False negatives:", false_negatives)
print("Unknown values:", unknown)
print("Computation time:", str(diff_time.total_seconds()/60.0), " minutes")