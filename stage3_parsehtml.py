__author__ = 'wintere'

import re
import json
import sys
from collections import defaultdict
from html_parser import MyHtmlParser

# # put the proper file path to the pairs source here
if len(sys.argv) != 2:
    print("Usage: python stage3.py <input filename>")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
fd = open(fp, mode='r', encoding="latin-1")

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

    parser = MyHtmlParser()
    pld = 'Product Long Description'
    try:
        print("Tuple1")
        r = json.loads(pair1_json)
        for k in r.keys():
            attribute_list[k] += 1
            print(k, ':', r[k][0])
        if pld in r.keys():
            parser.feed(r[pld][0])
        print("")
    except ValueError:
        print("invalid json string" + id_string)

    try:
        print("Tuple2")
        s = json.loads(pair2_json)
        for k in s.keys():
            attribute_list[k] += 1
            print(k, ':', s[k][0])
        if pld in s.keys():
            parser.feed(s[pld][0])
        print("")
    except ValueError:
        print("invalid json string" + pair2_id)

    print(match_status)
    print("")
    
    # TODO move data to appropriate structure, identify outlier tuples
#print(attribute_list)
fd.close()