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
pld = 'Product Long Description'
count = 0
lc = 0
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
    try:
        r = json.loads(pair1_json)
        if pld in r.keys():
            parser.result = {}
            parser.feed(r[pld][0])
            for parsedkey, parsedval in parser.result.items():
                if parsedkey not in  r.keys():
                    r[parsedkey] = [parsedval]
    except ValueError:
        print("invalid json string" + id_string)

    try:
        s = json.loads(pair2_json)
        if pld in s.keys():
            parser.result = {}
            parser.feed(s[pld][0])
            for parsedkey, parsedval in parser.result.items():
                if parsedkey not in  s.keys():
                    s[parsedkey] = [parsedval]
    except ValueError:
        print("invalid json string" + pair2_id)
fd.close()