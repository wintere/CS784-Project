__author__ = 'wintere'

from sklearn import svm

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

f = FeatureGenerator()
clf = svm.SVC()
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
    v = f.getVector(l, r)
    training_data.append(v)
    labels.append(match_status)

training.close()
print("training loaded")
clf.fit(training_data, labels)

true_pos = 0
false_pos = 0
true_neg = 0
false_neg = 0
for line in test:
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]

    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    v = f.getVector(l, r)
    match_guess = clf.predict([v])
    if match_guess == '?MATCH':
        if match_guess == match_status:
            true_pos += 1
        else:
            false_pos += 1
    else:
        if match_guess == match_status:
            true_neg += 1
        else:
            false_neg += 1
test.close()

print("True positives: " + str(true_pos))
print("False positives: " + str(false_pos))
print("True negatives: " + str(true_neg))
print("False negatives: " + str(false_neg))
precision = float (true_pos)/(true_pos + false_pos)
recall = float(true_pos)/(true_pos + false_neg)
print ("Precision:",precision, "Recall:",recall)
