__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict

# # put the proper file path to the pairs source here
if len(sys.argv) != 2:
    print("usage: pointer to elec_pairs_stage1.txt file")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
fd = open(fp, mode='r', encoding='utf-8', errors='replace')

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
    try:
        r = json.loads(pair1_json)
        for k in r.keys():
            attribute_list[k] += 1
    except ValueError:
        print("invalid json string" + id_string)

    try:
        s = json.loads(pair2_json)
        for k in s.keys():
            attribute_list[k] += 1
    except ValueError:
        print("invalid json string" + pair2_id)

    # TODO move data to appropriate structure, identify outlier tuples
fd.close()

# # preliminary overview: attribute list sorted by frequency (at most 40,000 as attributes differ b/w tuples)
# for k in sorted(attribute_list.items(), key=lambda t: t[1], reverse=True):
#    print(k[0] + " (" + str(k[1]) + ")")

# Record the top 10 attributes to a list
count = 0
top10_attributes = []
for attribute in sorted(attribute_list.items(), key=lambda t: t[1], reverse=True):
    top10_attributes.append(attribute[0])
    count += 1
    if(count == 10):
        break
    

# Iterate through all the tuples in the file again. Output the top 10 attributes.
fd = open(fp, mode="r")
for line in fd:
    # Split lines and parse the json
    seg = re.split(jumbo_pattern, line)
    pair1_json = seg[4]
    pair2_json = seg[8]

    # json loads returns a dictionary
    try:
        tuple1 = json.loads(pair1_json)
        tuple2 = json.loads(pair2_json)
    except ValueError:
        print("invalid json string" + id_string)

    for attribute in top10_attributes:
        if attribute in tuple1:
            print(attribute + ": " + str(tuple1[attribute]))
        if attribute in tuple2:
             print(attribute + ": " + str(tuple2[attribute]))

    print("\n")

fd.close()