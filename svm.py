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

true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0
dataset_count = 0

for line in test:
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]

    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    dataset_count += 1
    v = f.getVector(l, r)
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
test.close()

# Calculate end results
end_time = datetime.datetime.now()
diff_time = end_time - start_time
precision = float (true_positives)/(true_positives + false_positives)
recall = float(true_positives)/(true_positives + false_negatives)

# CSV stats
print("Data records,Precision,Recall,True positives,False positives,True negatives,False negatives,Execution Time")
print(str(dataset_count)+","+str(precision)+","+str(recall)+","+str(true_positives)+","+str(false_positives)+","+str(true_negatives)+","+str(false_negatives)+","+str(diff_time.total_seconds()))