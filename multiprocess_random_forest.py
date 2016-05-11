__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict
import random
from feature_operations import FeatureGenerator
from html_parser import MyHtmlParser
from sklearn import feature_extraction
import pickle
import queue
import threading
import time
from multiprocessing import Process, Queue, Pool
from sklearn import ensemble

# there might be a better way to do this than the split library...
jumbo_pattern = r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'

#initialize globals
f = FeatureGenerator()
unknown = 0
true_positives = 0
true_negatives = 0
false_positives = 0
false_negatives = 0
testing_size = 0
guesses = 0
correct_guesses = 0

#process (threadish thing) code
def processTraining(line):
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]
    pair1_json = pair1_json.lower()
    pair2_json = pair2_json.lower()
    # Set up the feature vector for these tuples
    l = json.loads(pair1_json)
    r = json.loads(pair2_json)
    v = f.getVector(l, r, allFuncs=True)
    if "?MATCH" in match_status:
        label = 1
    else:
        label = -1
    return [v, label]

def processTesting(line):
    rule_flag = 0
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]
    match_status = seg[9]
    pair1_json = pair1_json.lower()
    pair2_json = pair2_json.lower()
    # check for rule triggers
    if ('stress testing' in pair1_json or 'stress testing' in pair2_json):
        rule_flag = -1
        v = None
    # otherwise, load vector
    else:
        l = json.loads(pair1_json)
        r = json.loads(pair2_json)
        v = f.getVector(l, r, allFuncs=True)
    if "?MATCH" in match_status:
        label = 1
    else:
        label = -1
    return [v, label, rule_flag]


if __name__ == '__main__':

    # put the proper file path to the pairs source here
    if len(sys.argv) != 3:
        print("usage: <train> <test>")
        exit()

    start = time.time()

    #open files
    tr = sys.argv[1]
    te = sys.argv[2]
    train_file = open(tr, mode='r', errors='ignore', encoding='utf-8')
    test_file = open(te, mode='r', errors='ignore', encoding='utf-8')

    #queue up lines to feed up into pool of processes
    train_lines = []
    for line in train_file:
        if not ('stress testing' in line.lower()):
            train_lines.append(line)
    train_file.close()


    #process safe (ok sure)
    with Pool(processes=4) as pool:
       featureVecs = pool.map(processTraining, train_lines)
    #unzip computed tuples into vectors and labels
    trainingData, labels = zip(*featureVecs)
    print("Finished setting up", len(featureVecs),"training samples!")
    cs = time.time()
    features = len(featureVecs[0][0])
    clf = ensemble.RandomForestClassifier(n_estimators=features-10, random_state=26)
    clf = clf.fit(trainingData, labels)
    cf = time.time()
    print("Classifier set up in", (cf-cs)/60,"seconds.")
    test_lines = []
    for line in test_file:
        test_lines.append(line)
    test_file.close()

    with Pool(processes=4) as pool:
        featureVecs = pool.map(processTesting, test_lines)

    for match in featureVecs:
        vector = match[0]
        label = match[1]
        rule_flag = match[2]
        # if a vector was returned, pass it to the classifier
        if vector is not None:
            match_vector = clf.predict_proba([vector])
            if match_vector[0][0] > 0.5:
                match_guess = -1
            if match_vector[0][1] > 0.5:
                match_guess = 1
            if match_vector[0][1] == 0.5:
                match_guess = 0
                unknown += 1
        # otherwise, a rule must have fired
        else:
            match_guess = rule_flag
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


    finish = time.time()
    precision = float (correct_guesses)/(guesses)
    recall = float(correct_guesses)/(testing_size)
    f1 = 2 * float(precision * recall) / (precision + recall)
    # CSV stats
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1:", f1)
    print("True positives:", true_positives)
    print("False positives:", false_positives)
    print("True negatives:", true_negatives)
    print("False negatives:", false_negatives)
    print("Unknown values:", unknown)
    print("Computation time:", (finish - start)/60, " minutes")
