__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict
import random
from feature_operations import FeatureGenerator
from html_parser import MyHtmlParser



 # put the proper file path to the pairs source here
if len(sys.argv) != 2:
    print("usage: <pointer to stage3_L.txt file>")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
fd = open(fp, mode='r', errors='ignore', encoding='ascii')

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


# for each line (pair of tuples) in the file
count = 0
tuples = set()
s = 0
m = 0
# parser = MyHtmlParser()
f = FeatureGenerator()
parser = MyHtmlParser()

for line in fd:
    # split line into 5 parts described above
    seg = re.split(jumbo_pattern, line)
    parser.reset()
    # due to capturing groups we get more segments than we want
    id_string = seg[3]
    pair1_json = seg[4]
    pair2_id = seg[6]
    pair2_json = seg[8]
    match_status = seg[9]


    # r = pair_1's data, s = pair_2's data
    # json loads returns a dictionary
    if random.randint(0,12) == 1:
        if count < 50:
            print("NET")
            l = json.loads(pair1_json)
            r = json.loads(pair2_json)
            v = f.getVector(l, r)
            print(match_status)
            # for i in range(len(v)):
            #     print(a[i], ":", v[i], match_status)
            count += 1
        if count == 100:
            break

fd.close()


#l and r are dictionaries