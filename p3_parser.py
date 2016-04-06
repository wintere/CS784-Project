__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict
import random
import csv

# # put the proper file path to the pairs source here
if len(sys.argv) != 3:
    print("usage: <pointer to elec_pairs_stage1.txt file> <tuple csv name>")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
output = sys.argv[2]
fd = open(fp, mode='r', errors='replace')

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


# a simple attribute list for test purposes
attribute_list = defaultdict(int)

# for each line (pair of tuples) in the file
lc = 0
count = 0
tuples = set()
for line in fd:
    # split line into 5 parts described above
    seg = re.split(jumbo_pattern, line)
    
    # due to capturing groups we get more segments than we want
    id_string = seg[3]
    pair1_json = seg[4]
    pair2_id = seg[6]
    pair2_json = seg[8]
    match_status = seg[9]

    # r = pair_1's data, s = pair_2's data
    # json loads returns a dictionary
    if count < 200:
        print(id_string)
    count += 1

fd.close()

for t in tuples:
    print(t)
