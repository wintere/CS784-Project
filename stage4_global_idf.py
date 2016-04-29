import datetime
import re
import json
import sys
import math

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def cleanTokenize(string):
    tokens = []
    toks = re.split(r'[ \|\[\]_,\/\(\)\*\n\t\b\r\{\}\~\;\!\:]', string)
    for i in toks:
        if i != '' and i != '\n' and i != '-':
            tokens.append(i.lower())
    return(tokens)

def calcidf():
    # # put the proper file path to the pairs source here
    if len(sys.argv) != 2:
        print("Usage: python stage4_global_idf.py <data filename>")
        exit()

    # fetch page and split into tuples
    training_fp = sys.argv[1]
    training_fd = open(training_fp, mode='r', encoding="ascii", errors='ignore')

    # there might be a better way to do this than the split library...
    jumbo_pattern =  r'(\?MATCH|\?MISMATCH)|(\?\d+#[\w. -]+\?)|(\d+-\d+#[\w. -]+\?\d+\?)'
    product_count = 0
    product_names = []
    all_tokens = {}
    start_time = datetime.datetime.now()

    attribute = 'Product Long Description'

    for line in training_fd:
        # Split line into 3 important parts (tuple1, tuple2, label)
        seg = re.split(jumbo_pattern, line)
        pair1_json = seg[4]
        pair2_json = seg[8]
        match_status = seg[9]
        
        # Set up the feature vector for these tuples
        l = json.loads(pair1_json)
        r = json.loads(pair2_json)
        # lname = l['Product Name']
        # rname = r['Product Name']

        if attribute in l:
            lpld = l[attribute]
            ltokens = cleanTokenize(lpld[0])
            product_names.append(ltokens)
            for t in ltokens:
                if t in all_tokens:
                    all_tokens[t] += 1
                else:
                    all_tokens[t] = 1
            product_count += 1

        if attribute in r:
            rpld = r[attribute]
            rtokens = cleanTokenize(rpld[0])
            product_names.append(rtokens)
            for t in rtokens:
                if t in all_tokens:
                    all_tokens[t] += 1
                else:
                    all_tokens[t] = 1
            product_count += 1

    training_fd.close()
    print("Finished setting up " + str(product_count) + " tuples!")

    for token in all_tokens:
        print(token, ":" , idf(token, product_names))

if __name__ == "__main__":
    calcidf()