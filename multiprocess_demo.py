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

#process (threadish thing) code
def processLine(line):
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
    # test_file = open(te, mode='r', errors='ignore', encoding='utf-8')

    #queue up lines to feed up into pool of processes
    train_lines = []
    for line in train_file:
        train_lines.append(line)
    train_file.close()

    #process safe (ok sure)
    with Pool(processes=6) as pool:
       featureVecs = pool.map(processLine, train_lines)
    #unzip computed tuples into vectors and labels
    featureVecs, labels = zip(*featureVecs)
    clf = ensemble.RandomForestClassifier(n_estimators=37, random_state=26)
    clf = clf.fit(featureVecs, labels)

    finish = time.time()
    print(finish - start)
