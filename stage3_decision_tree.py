__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict
from feature_operations import FeatureGenerator
from sklearn import tree

# # put the proper file path to the pairs source here
if len(sys.argv) != 2:
    print("Usage: python stage3_decision_tree.py <input filename>")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
fd = open(fp, mode='r')

# tuple structure
# pair1ID-pair2ID#source?pair1ID?{pair1.json}?pair2ID{pair2.json}match
# pair1ID and pair2Id are strictly numeric, source can have dashes, periods (urls), or spaces (offline sources)
# match is strictly ?MATCH OR ?MISMATCH

# regular expressions to divide data into pairs of tuples: tested to pull out values on all 20,000 tuples
id_pattern =r'\d+-\d+#[\w. -]+\?\d+\?'
comp2_pattern = r'\?\d+#[\w. -]+\?'
match_pattern = r'\?MATCH|\?MISMATCH'

# there might be a better way to do this than the split library...
jumbo_pattern =  r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'
data = []
labels = []

# Now set up the training data
f = FeatureGenerator()
for line in fd:
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
        print(False)
    else:
        v = f.getVector(l, r)
        print(v, match_status)
        
    # Set up the label for these tuples
    label = 1 if match_status == "?MATCH" else 0
    
    # Now append the feature vector + label to our data structures
    data.append(v)
    labels.append(label)
fd.close()

# Set up a decision tree classifier using the data passed in
clf = tree.DecisionTreeClassifier()
clf = clf.fit(data, labels)

# Run a couple of tests to see if this works
test1 = clf.predict([[0.9701492537313433, 0.8125, 1.0]])
test2 = clf.predict([[0.08860759493670886, 0.3888888888888889, 1.0]])
print("Test 1 (should return 1): " + str(test1[0]))
print("Test 2 (should return 0): " + str(test2[0]))