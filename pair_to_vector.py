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

def cleanTokenize(string):
    tokens = []
    toks = re.split(r'[ \|\[\]_,\/\(\)\*\n\t\b\r\{\}\~\;\!\:]', string)
    for i in toks:
        if i != '' and i != '\n' and i != '-':
            tokens.append(i.lower())
    return(tokens)

 # put the proper file path to the pairs source here
if len(sys.argv) != 2:
    print("usage: <pointer to stage3_L.txt file>")
    exit()

# fetch page and split into tuples
fp = sys.argv[1]
fd = open(fp, mode='r', errors='ignore', encoding='utf-8')

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
tra = 0
te = 0
lds = []
f = FeatureGenerator()
a = f.getVectorAttributes(allFuncs=True)
lines = []
for line in fd:
    # split line into 5 parts described above
    seg = re.split(jumbo_pattern, line)
    # due to capturing groups we get more segments than we want
    id_string = seg[3]
    pair1_json = seg[4]
    pair2_id = seg[6]
    pair2_json = seg[8]
    match_status = seg[9]
    lines.append(line)

    # r = pair_1's data, s = pair_2's data
    # json loads returns a dictionary
    # if tra == 15000:
    #     te_f.write(line)
    #     te += 1
    # elif te == 5000:
    #     tra_f.write(line)
    #     tra += 1
    # elif random.randint(0,1) == 1:
    #     te_f.write(line)
    #     te += 1
    # else:
    #     tra_f.write(line)
    #     tra += 1
    if random.randint(0,201) == 3:
        l = json.loads(pair1_json)
        r = json.loads(pair2_json)
        v = f.getVector(l, r, allFuncs=True)
        print(match_status)
        count += 1
    if count == 200:
        break
    # ld_text = ''
    # rd_text = ''
    # if "Product Long Description" in l:
    #     ld = l['Product Long Description']
    #     ld_text = f.ie.text_from_html(ld[0])
    # if "Product Long Description" in r:
    #     rd = r['Product Long Description']
    #     rd_text = f.ie.text_from_html(rd[0])
    # lds.append((ld_text.strip('\n') + ' ' + rd_text.strip('\n') + ' '))

    # for i in range(len(v)):
    #     print(a[i], ":", v[i], match_status)
fd.close()

# cv = feature_extraction.text.TfidfVectorizer(encoding='utf-8', decode_error='ignore', tokenizer=cleanTokenize, vocabulary=None)
# tfidf_d = cv.fit(lds).vocabulary_
# pickle.dump(tfidf_d, open("tfidf_longd.p", "wb"))
