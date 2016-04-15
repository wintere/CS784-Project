__author__ = 'wintere'

import datetime
import re
import json
import sys
from feature_operations import FeatureGenerator
from sklearn import ensemble
from sklearn import cross_validation


# # put the proper file path to the pairs source here
if len(sys.argv) != 3:
    print("Usage: python stage3_random_forest_predictions.py <training data filename> <test data filename>")
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

# Set up a random forest classifier using the data passed in
clf = ensemble.RandomForestClassifier(n_estimators=16, random_state=14)
clf = clf.fit(training_data, labels)


# Open the file with the full dataset
dataset_fp = sys.argv[2]
dataset_fd = open(dataset_fp, mode='r', encoding="ascii", errors='ignore')

# Open the predictions file we'll output to
predictions_fd = open("predictions_Group18.txt", 'w')

# Set up the training data
print("Analyzing the predictions dataset...")
for line in dataset_fd:
    # Split line into important parts
    seg = line.split("?")
    if len(seg) != 5:
        print("Error: Line split yielded unexpected results")
    pairId = seg[0]
    pair1_id = seg[1]
    pair1_json = seg[2]
    pair2_id = seg[3]
    pair2_json = seg[4]
    if pairId != pair1_id or pair1_id != pair2_id:
        print("Error: Pair IDs do not match, something is wrong")
    
    # Set up the feature vector for these tuples
    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    dataset_count += 1
    v = f.getVector(l, r, allFuncs=True)
    match_vector = clf.predict_proba([v])
    
    # Make a prediction for this line based on match_vector
    if match_vector[0][0] > .73:
        match_guess = "MISMATCH"
    if match_vector[0][1] > 0.65:
        match_guess = "MATCH"
    if match_vector[0][1] <= 0.65 and match_vector[0][0] <= 0.73:
        match_guess = "UNKNOWN"
    predictions_fd.write(pairId + ", " + str(match_guess) + "\n")
    
dataset_fd.close()
predictions_fd.close()


end_time = datetime.datetime.now()
diff_time = end_time - start_time
print("Computation time:", str(diff_time.total_seconds()/60.0), " minutes")

